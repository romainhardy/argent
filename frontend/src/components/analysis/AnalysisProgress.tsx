import { useEffect } from 'react';
import { Loader2, CheckCircle2, XCircle, Clock } from 'lucide-react';
import { AnalysisPhase, AnalysisProgress as AnalysisProgressType, AnalysisStatus } from '../../api/types';
import { PhaseIndicator } from './PhaseIndicator';

interface AnalysisProgressProps {
  status: AnalysisStatus;
  progress: AnalysisProgressType | null;
  onStartStream?: () => void;
  error?: string | null;
}

const PHASES: { phase: AnalysisPhase; label: string }[] = [
  { phase: 'initializing', label: 'Initializing' },
  { phase: 'data_collection', label: 'Collecting Data' },
  { phase: 'technical_analysis', label: 'Technical Analysis' },
  { phase: 'fundamental_analysis', label: 'Fundamental Analysis' },
  { phase: 'sentiment_analysis', label: 'Sentiment Analysis' },
  { phase: 'risk_analysis', label: 'Risk Analysis' },
  { phase: 'macro_analysis', label: 'Macro Analysis' },
  { phase: 'generating_report', label: 'Generating Report' },
  { phase: 'completed', label: 'Completed' },
];

export function AnalysisProgress({
  status,
  progress,
  onStartStream,
  error,
}: AnalysisProgressProps) {
  useEffect(() => {
    if ((status === 'running' || status === 'pending') && onStartStream) {
      onStartStream();
    }
  }, [status, onStartStream]);

  const currentPhaseIndex = progress
    ? PHASES.findIndex((p) => p.phase === progress.phase)
    : -1;

  const getStatusIcon = () => {
    switch (status) {
      case 'pending':
        return <Clock className="w-6 h-6 text-yellow-400 animate-pulse" />;
      case 'running':
        return <Loader2 className="w-6 h-6 text-primary-400 animate-spin" />;
      case 'completed':
        return <CheckCircle2 className="w-6 h-6 text-green-400" />;
      case 'failed':
        return <XCircle className="w-6 h-6 text-red-400" />;
      default:
        return null;
    }
  };

  const getStatusLabel = () => {
    switch (status) {
      case 'pending':
        return 'Waiting to start...';
      case 'running':
        return progress?.message || 'Analysis in progress...';
      case 'completed':
        return 'Analysis complete!';
      case 'failed':
        return error || 'Analysis failed';
      default:
        return '';
    }
  };

  const overallProgress = progress
    ? Math.round(((currentPhaseIndex + 1) / PHASES.length) * 100)
    : 0;

  return (
    <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          {getStatusIcon()}
          <div>
            <h3 className="text-lg font-medium text-white">Analysis Progress</h3>
            <p className="text-sm text-gray-400">{getStatusLabel()}</p>
          </div>
        </div>
        {status === 'running' && (
          <div className="text-right">
            <span className="text-2xl font-bold text-primary-400">{overallProgress}%</span>
          </div>
        )}
      </div>

      {/* Progress bar */}
      {(status === 'running' || status === 'pending') && (
        <div className="mb-6">
          <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-primary-600 to-primary-400 transition-all duration-500"
              style={{ width: `${overallProgress}%` }}
            />
          </div>
        </div>
      )}

      {/* Phase indicators */}
      <div className="grid grid-cols-3 gap-3 md:grid-cols-5 lg:grid-cols-9">
        {PHASES.map((phase, index) => {
          let phaseStatus: 'pending' | 'active' | 'completed' | 'error' = 'pending';

          if (status === 'failed') {
            phaseStatus = index <= currentPhaseIndex ? 'error' : 'pending';
          } else if (status === 'completed') {
            phaseStatus = 'completed';
          } else if (index < currentPhaseIndex) {
            phaseStatus = 'completed';
          } else if (index === currentPhaseIndex) {
            phaseStatus = 'active';
          }

          return (
            <PhaseIndicator
              key={phase.phase}
              label={phase.label}
              status={phaseStatus}
              progress={index === currentPhaseIndex ? progress?.progress : undefined}
            />
          );
        })}
      </div>

      {/* Error message */}
      {status === 'failed' && error && (
        <div className="mt-4 p-4 bg-red-900/20 border border-red-800 rounded-lg">
          <p className="text-red-400 text-sm">{error}</p>
        </div>
      )}
    </div>
  );
}

export default AnalysisProgress;
