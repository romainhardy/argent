import { ReactNode } from 'react';

interface DashboardGridProps {
  children: ReactNode;
  columns?: 1 | 2 | 3 | 4;
  gap?: 'sm' | 'md' | 'lg';
}

export function DashboardGrid({
  children,
  columns = 2,
  gap = 'md',
}: DashboardGridProps) {
  const gapClass = {
    sm: 'gap-2',
    md: 'gap-4',
    lg: 'gap-6',
  }[gap];

  const colsClass = {
    1: 'grid-cols-1',
    2: 'grid-cols-1 lg:grid-cols-2',
    3: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3',
    4: 'grid-cols-1 md:grid-cols-2 xl:grid-cols-4',
  }[columns];

  return <div className={`grid ${colsClass} ${gapClass}`}>{children}</div>;
}

interface GridItemProps {
  children: ReactNode;
  colSpan?: 1 | 2 | 3 | 4 | 'full';
  rowSpan?: 1 | 2 | 3;
}

export function GridItem({ children, colSpan = 1, rowSpan = 1 }: GridItemProps) {
  const colSpanClass = {
    1: '',
    2: 'lg:col-span-2',
    3: 'lg:col-span-3',
    4: 'xl:col-span-4',
    full: 'col-span-full',
  }[colSpan];

  const rowSpanClass = {
    1: '',
    2: 'row-span-2',
    3: 'row-span-3',
  }[rowSpan];

  return <div className={`${colSpanClass} ${rowSpanClass}`}>{children}</div>;
}

interface PageContainerProps {
  children: ReactNode;
  title?: string;
  subtitle?: string;
  actions?: ReactNode;
}

export function PageContainer({
  children,
  title,
  subtitle,
  actions,
}: PageContainerProps) {
  return (
    <div className="p-4 md:p-6 space-y-6">
      {(title || actions) && (
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            {title && <h1 className="text-2xl font-bold text-white">{title}</h1>}
            {subtitle && <p className="text-gray-400 mt-1">{subtitle}</p>}
          </div>
          {actions && <div className="flex items-center gap-3">{actions}</div>}
        </div>
      )}
      {children}
    </div>
  );
}

interface CardProps {
  children: ReactNode;
  title?: string;
  subtitle?: string;
  actions?: ReactNode;
  padding?: boolean;
  className?: string;
}

export function Card({
  children,
  title,
  subtitle,
  actions,
  padding = true,
  className = '',
}: CardProps) {
  return (
    <div
      className={`bg-gray-800 rounded-lg border border-gray-700 overflow-hidden ${className}`}
    >
      {(title || actions) && (
        <div className="px-4 py-3 border-b border-gray-700 flex items-center justify-between">
          <div>
            {title && <h3 className="text-lg font-medium text-white">{title}</h3>}
            {subtitle && <p className="text-sm text-gray-400">{subtitle}</p>}
          </div>
          {actions && <div className="flex items-center gap-2">{actions}</div>}
        </div>
      )}
      <div className={padding ? 'p-4' : ''}>{children}</div>
    </div>
  );
}

interface StatCardProps {
  label: string;
  value: string | number;
  change?: number;
  changeLabel?: string;
  icon?: ReactNode;
  trend?: 'up' | 'down' | 'neutral';
}

export function StatCard({
  label,
  value,
  change,
  changeLabel,
  icon,
  trend,
}: StatCardProps) {
  const getTrendColor = () => {
    if (trend === 'up') return 'text-green-400';
    if (trend === 'down') return 'text-red-400';
    return 'text-gray-400';
  };

  return (
    <div className="bg-gray-800 rounded-lg border border-gray-700 p-4">
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm text-gray-400">{label}</span>
        {icon && <div className="text-gray-500">{icon}</div>}
      </div>
      <div className="text-2xl font-bold text-white">{value}</div>
      {change !== undefined && (
        <div className={`text-sm mt-1 ${getTrendColor()}`}>
          {change >= 0 ? '+' : ''}
          {typeof change === 'number' && !isNaN(change) ? change.toFixed(2) : change}%
          {changeLabel && <span className="text-gray-500 ml-1">{changeLabel}</span>}
        </div>
      )}
    </div>
  );
}

interface LoadingStateProps {
  message?: string;
}

export function LoadingState({ message = 'Loading...' }: LoadingStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-12">
      <div className="w-8 h-8 border-2 border-primary-500 border-t-transparent rounded-full animate-spin mb-4" />
      <p className="text-gray-400">{message}</p>
    </div>
  );
}

interface ErrorStateProps {
  title?: string;
  message: string;
  onRetry?: () => void;
}

export function ErrorState({
  title = 'Error',
  message,
  onRetry,
}: ErrorStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-12">
      <div className="w-12 h-12 bg-red-900/20 rounded-full flex items-center justify-center mb-4">
        <svg
          className="w-6 h-6 text-red-400"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
      </div>
      <h3 className="text-lg font-medium text-white mb-1">{title}</h3>
      <p className="text-gray-400 text-center max-w-md mb-4">{message}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg transition-colors"
        >
          Try Again
        </button>
      )}
    </div>
  );
}

interface EmptyStateProps {
  title: string;
  message: string;
  action?: {
    label: string;
    onClick: () => void;
  };
  icon?: ReactNode;
}

export function EmptyState({ title, message, action, icon }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-12">
      {icon && (
        <div className="w-12 h-12 bg-gray-700 rounded-full flex items-center justify-center mb-4 text-gray-400">
          {icon}
        </div>
      )}
      <h3 className="text-lg font-medium text-white mb-1">{title}</h3>
      <p className="text-gray-400 text-center max-w-md mb-4">{message}</p>
      {action && (
        <button
          onClick={action.onClick}
          className="px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg transition-colors"
        >
          {action.label}
        </button>
      )}
    </div>
  );
}

export default DashboardGrid;
