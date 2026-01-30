import { useCallback, useEffect, useRef, useState } from 'react';
import { AnalysisProgress, SSEEvent } from '../api/types';

interface UseSSEOptions {
  onProgress?: (progress: AnalysisProgress) => void;
  onPartialResult?: (data: unknown) => void;
  onComplete?: (data: unknown) => void;
  onError?: (error: string) => void;
  retryCount?: number;
  retryDelay?: number;
}

interface UseSSEReturn {
  isConnected: boolean;
  error: string | null;
  progress: AnalysisProgress | null;
  connect: () => void;
  disconnect: () => void;
}

export function useSSE(url: string | null, options: UseSSEOptions = {}): UseSSEReturn {
  const {
    onProgress,
    onPartialResult,
    onComplete,
    onError,
    retryCount = 3,
    retryDelay = 1000,
  } = options;

  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [progress, setProgress] = useState<AnalysisProgress | null>(null);

  const eventSourceRef = useRef<EventSource | null>(null);
  const retriesRef = useRef(0);

  const disconnect = useCallback(() => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
      setIsConnected(false);
    }
  }, []);

  const connect = useCallback(() => {
    if (!url) return;

    disconnect();
    setError(null);

    const eventSource = new EventSource(url);
    eventSourceRef.current = eventSource;

    eventSource.onopen = () => {
      setIsConnected(true);
      retriesRef.current = 0;
    };

    eventSource.onmessage = (event) => {
      try {
        const data: SSEEvent = JSON.parse(event.data);

        switch (data.type) {
          case 'progress':
            const progressData = data.data as AnalysisProgress;
            setProgress(progressData);
            onProgress?.(progressData);
            break;

          case 'partial_result':
            onPartialResult?.(data.data);
            break;

          case 'complete':
            onComplete?.(data.data);
            disconnect();
            break;

          case 'error':
            const errorData = data.data as { message: string };
            setError(errorData.message);
            onError?.(errorData.message);
            disconnect();
            break;
        }
      } catch (e) {
        console.error('Failed to parse SSE event:', e);
      }
    };

    eventSource.onerror = () => {
      setIsConnected(false);

      if (retriesRef.current < retryCount) {
        retriesRef.current += 1;
        setTimeout(() => {
          connect();
        }, retryDelay * retriesRef.current);
      } else {
        setError('Connection lost. Please refresh the page.');
        onError?.('Connection lost');
        disconnect();
      }
    };
  }, [url, disconnect, onProgress, onPartialResult, onComplete, onError, retryCount, retryDelay]);

  useEffect(() => {
    return () => {
      disconnect();
    };
  }, [disconnect]);

  return {
    isConnected,
    error,
    progress,
    connect,
    disconnect,
  };
}

export default useSSE;
