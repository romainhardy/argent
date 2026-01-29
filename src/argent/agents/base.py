"""Base agent class with agentic loop pattern."""

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from anthropic import Anthropic
from anthropic.types import Message, ToolResultBlockParam, ToolUseBlock


class FinancialAgentType(str, Enum):
    """Types of financial analysis agents."""

    DATA_COLLECTION = "data_collection"
    MACRO_ANALYSIS = "macro_analysis"
    TECHNICAL_ANALYSIS = "technical_analysis"
    FUNDAMENTAL_ANALYSIS = "fundamental_analysis"
    RISK_ANALYSIS = "risk_analysis"
    SENTIMENT_ANALYSIS = "sentiment_analysis"
    REPORT = "report"


@dataclass
class AgentResult:
    """Result from agent execution."""

    success: bool
    data: dict[str, Any]
    error: str | None = None
    input_tokens: int = 0
    output_tokens: int = 0


@dataclass
class ToolDefinition:
    """Tool definition for Claude API."""

    name: str
    description: str
    input_schema: dict[str, Any]


@dataclass
class BaseAgent(ABC):
    """
    Base agent with agentic loop pattern.

    Implements the core loop:
    1. Build task message from input
    2. Call Claude API with system prompt + tools
    3. Handle stop_reason: end_turn (done) or tool_use (execute & loop)
    4. Track token usage
    5. Parse structured JSON output
    """

    client: Anthropic
    model: str = "claude-sonnet-4-20250514"
    max_turns: int = 10
    _input_tokens: int = field(default=0, init=False)
    _output_tokens: int = field(default=0, init=False)

    @property
    @abstractmethod
    def agent_type(self) -> FinancialAgentType:
        """Return the agent type."""
        pass

    @property
    @abstractmethod
    def system_prompt(self) -> str:
        """Return the system prompt for this agent."""
        pass

    @abstractmethod
    def get_tools(self) -> list[ToolDefinition]:
        """Return available tools for this agent."""
        pass

    @abstractmethod
    def execute_tool(self, tool_name: str, tool_input: dict[str, Any]) -> Any:
        """Execute a tool and return the result."""
        pass

    def _build_tools_schema(self) -> list[dict[str, Any]]:
        """Convert tool definitions to Claude API format."""
        tools = self.get_tools()
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.input_schema,
            }
            for tool in tools
        ]

    def _process_tool_calls(self, message: Message) -> list[ToolResultBlockParam]:
        """Process tool use blocks and return results."""
        results: list[ToolResultBlockParam] = []

        for block in message.content:
            if isinstance(block, ToolUseBlock):
                try:
                    result = self.execute_tool(block.name, block.input)
                    # Convert result to string for Claude
                    if isinstance(result, (dict, list)):
                        content = json.dumps(result, default=str)
                    else:
                        content = str(result)

                    results.append(
                        {
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": content,
                        }
                    )
                except Exception as e:
                    results.append(
                        {
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": f"Error executing tool: {str(e)}",
                            "is_error": True,
                        }
                    )

        return results

    def _extract_json_output(self, message: Message) -> dict[str, Any] | None:
        """Extract JSON output from the final message."""
        for block in message.content:
            if hasattr(block, "text"):
                text = block.text
                # Try to find JSON in the response
                try:
                    # Look for JSON block
                    if "```json" in text:
                        start = text.find("```json") + 7
                        end = text.find("```", start)
                        if end > start:
                            return json.loads(text[start:end].strip())

                    # Try parsing entire text as JSON
                    return json.loads(text)
                except json.JSONDecodeError:
                    continue

        return None

    def run(self, task: str, context: dict[str, Any] | None = None) -> AgentResult:
        """
        Run the agentic loop.

        Args:
            task: The task description
            context: Optional context data

        Returns:
            AgentResult with the analysis output
        """
        self._input_tokens = 0
        self._output_tokens = 0

        # Build initial message
        user_message = task
        if context:
            user_message += f"\n\nContext:\n```json\n{json.dumps(context, default=str)}\n```"

        messages: list[dict[str, Any]] = [{"role": "user", "content": user_message}]
        tools = self._build_tools_schema()

        for turn in range(self.max_turns):
            # Call Claude API
            response = self.client.messages.create(
                model=self.model,
                max_tokens=8192,
                system=self.system_prompt,
                tools=tools if tools else None,
                messages=messages,
            )

            # Track token usage
            self._input_tokens += response.usage.input_tokens
            self._output_tokens += response.usage.output_tokens

            # Check stop reason
            if response.stop_reason == "end_turn":
                # Agent is done - extract output
                output = self._extract_json_output(response)
                if output:
                    return AgentResult(
                        success=True,
                        data=output,
                        input_tokens=self._input_tokens,
                        output_tokens=self._output_tokens,
                    )
                else:
                    # Return text content if no JSON found
                    text_content = ""
                    for block in response.content:
                        if hasattr(block, "text"):
                            text_content += block.text
                    return AgentResult(
                        success=True,
                        data={"text": text_content},
                        input_tokens=self._input_tokens,
                        output_tokens=self._output_tokens,
                    )

            elif response.stop_reason == "tool_use":
                # Process tool calls
                tool_results = self._process_tool_calls(response)

                # Add assistant message and tool results to history
                messages.append({"role": "assistant", "content": response.content})
                messages.append({"role": "user", "content": tool_results})

            else:
                # Unexpected stop reason
                return AgentResult(
                    success=False,
                    data={},
                    error=f"Unexpected stop reason: {response.stop_reason}",
                    input_tokens=self._input_tokens,
                    output_tokens=self._output_tokens,
                )

        # Max turns exceeded
        return AgentResult(
            success=False,
            data={},
            error=f"Max turns ({self.max_turns}) exceeded",
            input_tokens=self._input_tokens,
            output_tokens=self._output_tokens,
        )
