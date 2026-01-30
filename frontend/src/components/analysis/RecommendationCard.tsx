import {
  TrendingUp,
  TrendingDown,
  Minus,
  Target,
  Shield,
  AlertTriangle,
} from 'lucide-react';
import { Recommendation } from '../../api/types';

interface RecommendationCardProps {
  recommendation: Recommendation;
}

export function RecommendationCard({ recommendation }: RecommendationCardProps) {
  const {
    symbol,
    action,
    confidence,
    targetPrice,
    stopLoss,
    rationale,
    risks,
  } = recommendation;

  const getActionConfig = () => {
    switch (action) {
      case 'strong_buy':
        return {
          label: 'Strong Buy',
          color: 'text-green-400',
          bgColor: 'bg-green-900/30',
          borderColor: 'border-green-700',
          icon: <TrendingUp className="w-6 h-6" />,
        };
      case 'buy':
        return {
          label: 'Buy',
          color: 'text-green-400',
          bgColor: 'bg-green-900/20',
          borderColor: 'border-green-800',
          icon: <TrendingUp className="w-5 h-5" />,
        };
      case 'hold':
        return {
          label: 'Hold',
          color: 'text-yellow-400',
          bgColor: 'bg-yellow-900/20',
          borderColor: 'border-yellow-800',
          icon: <Minus className="w-5 h-5" />,
        };
      case 'sell':
        return {
          label: 'Sell',
          color: 'text-red-400',
          bgColor: 'bg-red-900/20',
          borderColor: 'border-red-800',
          icon: <TrendingDown className="w-5 h-5" />,
        };
      case 'strong_sell':
        return {
          label: 'Strong Sell',
          color: 'text-red-400',
          bgColor: 'bg-red-900/30',
          borderColor: 'border-red-700',
          icon: <TrendingDown className="w-6 h-6" />,
        };
      default:
        return {
          label: 'Unknown',
          color: 'text-gray-400',
          bgColor: 'bg-gray-800',
          borderColor: 'border-gray-700',
          icon: <Minus className="w-5 h-5" />,
        };
    }
  };

  const config = getActionConfig();

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(price);
  };

  return (
    <div
      className={`rounded-lg border ${config.borderColor} ${config.bgColor} overflow-hidden`}
    >
      {/* Header */}
      <div className="p-4 border-b border-gray-700/50">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className={`${config.color}`}>{config.icon}</div>
            <div>
              <h3 className="text-xl font-bold text-white">{symbol}</h3>
              <span className={`text-sm font-medium ${config.color}`}>
                {config.label}
              </span>
            </div>
          </div>
          <div className="text-right">
            <div className="text-sm text-gray-400">Confidence</div>
            <div className="flex items-center gap-2">
              <div className="w-16 h-2 bg-gray-700 rounded-full overflow-hidden">
                <div
                  className={`h-full ${
                    confidence >= 70
                      ? 'bg-green-500'
                      : confidence >= 50
                      ? 'bg-yellow-500'
                      : 'bg-red-500'
                  }`}
                  style={{ width: `${confidence}%` }}
                />
              </div>
              <span className="text-white font-medium">{confidence}%</span>
            </div>
          </div>
        </div>
      </div>

      {/* Price targets */}
      {(targetPrice || stopLoss) && (
        <div className="px-4 py-3 grid grid-cols-2 gap-4 border-b border-gray-700/50">
          {targetPrice && (
            <div className="flex items-center gap-2">
              <Target className="w-4 h-4 text-green-400" />
              <div>
                <div className="text-xs text-gray-400">Target Price</div>
                <div className="text-white font-medium">{formatPrice(targetPrice)}</div>
              </div>
            </div>
          )}
          {stopLoss && (
            <div className="flex items-center gap-2">
              <Shield className="w-4 h-4 text-red-400" />
              <div>
                <div className="text-xs text-gray-400">Stop Loss</div>
                <div className="text-white font-medium">{formatPrice(stopLoss)}</div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Rationale */}
      <div className="p-4 border-b border-gray-700/50">
        <h4 className="text-sm font-medium text-gray-300 mb-2">Rationale</h4>
        <p className="text-gray-400 text-sm leading-relaxed">{rationale}</p>
      </div>

      {/* Risks */}
      {risks.length > 0 && (
        <div className="p-4">
          <h4 className="text-sm font-medium text-gray-300 mb-2 flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-yellow-400" />
            Key Risks
          </h4>
          <ul className="space-y-1">
            {risks.map((risk, index) => (
              <li key={index} className="text-gray-400 text-sm flex items-start gap-2">
                <span className="text-yellow-400 mt-1">•</span>
                {risk}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export default RecommendationCard;
