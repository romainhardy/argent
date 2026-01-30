import { CheckCircle2, Loader2, Circle, AlertCircle } from 'lucide-react';

interface PhaseIndicatorProps {
  label: string;
  status: 'pending' | 'active' | 'completed' | 'error';
  progress?: number;
}

export function PhaseIndicator({ label, status, progress }: PhaseIndicatorProps) {
  const getIcon = () => {
    switch (status) {
      case 'completed':
        return <CheckCircle2 className="w-5 h-5 text-green-400" />;
      case 'active':
        return <Loader2 className="w-5 h-5 text-primary-400 animate-spin" />;
      case 'error':
        return <AlertCircle className="w-5 h-5 text-red-400" />;
      default:
        return <Circle className="w-5 h-5 text-gray-600" />;
    }
  };

  const getBackgroundColor = () => {
    switch (status) {
      case 'completed':
        return 'bg-green-900/20 border-green-800';
      case 'active':
        return 'bg-primary-900/20 border-primary-700';
      case 'error':
        return 'bg-red-900/20 border-red-800';
      default:
        return 'bg-gray-800 border-gray-700';
    }
  };

  const getTextColor = () => {
    switch (status) {
      case 'completed':
        return 'text-green-400';
      case 'active':
        return 'text-primary-400';
      case 'error':
        return 'text-red-400';
      default:
        return 'text-gray-500';
    }
  };

  return (
    <div
      className={`flex flex-col items-center p-3 rounded-lg border transition-all duration-300 ${getBackgroundColor()}`}
    >
      <div className="mb-2">{getIcon()}</div>
      <span className={`text-xs text-center font-medium ${getTextColor()}`}>{label}</span>
      {status === 'active' && progress !== undefined && (
        <div className="w-full mt-2">
          <div className="h-1 bg-gray-700 rounded-full overflow-hidden">
            <div
              className="h-full bg-primary-400 transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>
      )}
    </div>
  );
}

export default PhaseIndicator;
