import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useCallback, useState } from 'react';
import {
  getAnalysis,
  getAnalysisStreamUrl,
  listAnalyses,
  startAnalysis,
  StartAnalysisParams,
} from '../api/endpoints';
import { AnalysisProgress, AnalysisResult } from '../api/types';
import { useSSE } from './useSSE';

export function useAnalysisList(limit: number = 10) {
  return useQuery({
    queryKey: ['analyses', limit],
    queryFn: () => listAnalyses(limit),
    staleTime: 30000,
    refetchOnWindowFocus: false,
    placeholderData: (previousData) => previousData,
  });
}

export function useAnalysisById(analysisId: string | null) {
  return useQuery({
    queryKey: ['analysis', analysisId],
    queryFn: () => getAnalysis(analysisId!),
    enabled: !!analysisId,
    refetchInterval: (query) => {
      const data = query.state.data;
      if (data?.status === 'running' || data?.status === 'pending') {
        return 5000;
      }
      return false;
    },
    refetchOnWindowFocus: false,
    placeholderData: (previousData) => previousData,
  });
}

export function useStartAnalysis() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (params: StartAnalysisParams) => startAnalysis(params),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['analyses'] });
    },
  });
}

interface UseAnalysisStreamOptions {
  onProgress?: (progress: AnalysisProgress) => void;
  onComplete?: (result: AnalysisResult) => void;
  onError?: (error: string) => void;
}

export function useAnalysisStream(
  analysisId: string | null,
  options: UseAnalysisStreamOptions = {}
) {
  const queryClient = useQueryClient();
  const [partialResults, setPartialResults] = useState<Partial<AnalysisResult>>({});

  const handleComplete = useCallback(
    (data: unknown) => {
      const result = data as AnalysisResult;
      queryClient.setQueryData(['analysis', analysisId], result);
      queryClient.invalidateQueries({ queryKey: ['analyses'] });
      options.onComplete?.(result);
    },
    [analysisId, queryClient, options]
  );

  const handlePartialResult = useCallback((data: unknown) => {
    setPartialResults((prev) => ({
      ...prev,
      ...(data as Partial<AnalysisResult>),
    }));
  }, []);

  const url = analysisId ? getAnalysisStreamUrl(analysisId) : null;

  const { isConnected, error, progress, connect, disconnect } = useSSE(url, {
    onProgress: options.onProgress,
    onPartialResult: handlePartialResult,
    onComplete: handleComplete,
    onError: options.onError,
  });

  return {
    isConnected,
    error,
    progress,
    partialResults,
    connect,
    disconnect,
  };
}

export function useAnalysisWithStream(analysisId: string | null) {
  const [progress, setProgress] = useState<AnalysisProgress | null>(null);
  const [streamError, setStreamError] = useState<string | null>(null);

  const queryClient = useQueryClient();

  const analysisQuery = useAnalysisById(analysisId);

  const stream = useAnalysisStream(analysisId, {
    onProgress: setProgress,
    onComplete: (result) => {
      queryClient.setQueryData(['analysis', analysisId], result);
    },
    onError: setStreamError,
  });

  const shouldStream =
    analysisQuery.data?.status === 'running' || analysisQuery.data?.status === 'pending';

  return {
    analysis: analysisQuery.data,
    isLoading: analysisQuery.isLoading,
    error: analysisQuery.error?.message || streamError,
    progress,
    isStreaming: shouldStream && stream.isConnected,
    startStream: stream.connect,
    stopStream: stream.disconnect,
  };
}
