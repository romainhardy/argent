"""Agent system prompts."""

from argent.prompts.data_collection import DATA_COLLECTION_SYSTEM_PROMPT
from argent.prompts.fundamental_analysis import FUNDAMENTAL_ANALYSIS_SYSTEM_PROMPT
from argent.prompts.macro_analysis import MACRO_ANALYSIS_SYSTEM_PROMPT
from argent.prompts.report import REPORT_SYSTEM_PROMPT
from argent.prompts.risk_analysis import RISK_ANALYSIS_SYSTEM_PROMPT
from argent.prompts.sentiment_analysis import SENTIMENT_ANALYSIS_SYSTEM_PROMPT
from argent.prompts.technical_analysis import TECHNICAL_ANALYSIS_SYSTEM_PROMPT

__all__ = [
    "DATA_COLLECTION_SYSTEM_PROMPT",
    "MACRO_ANALYSIS_SYSTEM_PROMPT",
    "TECHNICAL_ANALYSIS_SYSTEM_PROMPT",
    "FUNDAMENTAL_ANALYSIS_SYSTEM_PROMPT",
    "RISK_ANALYSIS_SYSTEM_PROMPT",
    "SENTIMENT_ANALYSIS_SYSTEM_PROMPT",
    "REPORT_SYSTEM_PROMPT",
]
