import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Search,
  Bell,
  RefreshCw,
  CheckCircle2,
  AlertCircle,
  Menu,
} from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import { checkHealth } from '../../api/endpoints';

interface HeaderProps {
  onMenuClick?: () => void;
}

export function Header({ onMenuClick }: HeaderProps) {
  const [searchValue, setSearchValue] = useState('');
  const navigate = useNavigate();

  const healthQuery = useQuery({
    queryKey: ['health'],
    queryFn: checkHealth,
    refetchInterval: 60000,
    staleTime: 30000,
    retry: 1,
    refetchOnWindowFocus: false,
    placeholderData: (previousData) => previousData,
  });

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchValue.trim()) {
      navigate(`/charts?symbol=${searchValue.toUpperCase()}`);
      setSearchValue('');
    }
  };

  const getStatusColor = () => {
    if (healthQuery.isLoading) return 'text-yellow-400';
    if (healthQuery.isError) return 'text-red-400';
    if (healthQuery.data?.status === 'healthy') return 'text-green-400';
    if (healthQuery.data?.status === 'degraded') return 'text-yellow-400';
    return 'text-red-400';
  };

  const getStatusIcon = () => {
    if (healthQuery.isLoading) {
      return <RefreshCw className="w-4 h-4 animate-spin" />;
    }
    if (healthQuery.isError || healthQuery.data?.status === 'unhealthy') {
      return <AlertCircle className="w-4 h-4" />;
    }
    return <CheckCircle2 className="w-4 h-4" />;
  };

  return (
    <header className="h-16 bg-gray-900 border-b border-gray-800 flex items-center justify-between px-4 sticky top-0 z-30">
      {/* Left section */}
      <div className="flex items-center gap-4">
        <button
          onClick={onMenuClick}
          className="p-2 hover:bg-gray-800 rounded-lg lg:hidden"
        >
          <Menu className="w-5 h-5 text-gray-400" />
        </button>

        {/* Search */}
        <form onSubmit={handleSearch} className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
          <input
            type="text"
            value={searchValue}
            onChange={(e) => setSearchValue(e.target.value)}
            placeholder="Search symbol (e.g., AAPL)"
            className="w-64 pl-10 pr-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          />
        </form>
      </div>

      {/* Right section */}
      <div className="flex items-center gap-4">
        {/* API Status */}
        <div
          className={`flex items-center gap-2 px-3 py-1.5 rounded-full bg-gray-800 ${getStatusColor()}`}
          title={
            healthQuery.isLoading
              ? 'Checking API status...'
              : healthQuery.isError
              ? 'API connection failed'
              : `API ${healthQuery.data?.status}`
          }
        >
          {getStatusIcon()}
          <span className="text-sm font-medium hidden sm:inline">
            {healthQuery.isLoading
              ? 'Checking...'
              : healthQuery.isError
              ? 'Offline'
              : healthQuery.data?.status === 'healthy'
              ? 'Online'
              : 'Degraded'}
          </span>
        </div>

        {/* Notifications */}
        <button className="relative p-2 hover:bg-gray-800 rounded-lg">
          <Bell className="w-5 h-5 text-gray-400" />
          <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full" />
        </button>

        {/* Refresh */}
        <button
          onClick={() => healthQuery.refetch()}
          className="p-2 hover:bg-gray-800 rounded-lg"
          title="Refresh status"
        >
          <RefreshCw
            className={`w-5 h-5 text-gray-400 ${
              healthQuery.isFetching ? 'animate-spin' : ''
            }`}
          />
        </button>
      </div>
    </header>
  );
}

export default Header;
