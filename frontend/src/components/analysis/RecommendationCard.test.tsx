import { describe, it, expect } from 'vitest';
import { render, screen } from '../../test/test-utils';
import { RecommendationCard } from './RecommendationCard';
import { Recommendation } from '../../api/types';

describe('RecommendationCard', () => {
  const mockRecommendation: Recommendation = {
    symbol: 'AAPL',
    action: 'buy',
    confidence: 75,
    targetPrice: 200,
    stopLoss: 150,
    rationale: 'Strong fundamentals and positive momentum',
    risks: ['Market volatility', 'Sector rotation'],
  };

  it('should render the symbol', () => {
    render(<RecommendationCard recommendation={mockRecommendation} />);
    expect(screen.getByText('AAPL')).toBeInTheDocument();
  });

  it('should render the action label', () => {
    render(<RecommendationCard recommendation={mockRecommendation} />);
    expect(screen.getByText('Buy')).toBeInTheDocument();
  });

  it('should render confidence percentage', () => {
    render(<RecommendationCard recommendation={mockRecommendation} />);
    expect(screen.getByText('75%')).toBeInTheDocument();
  });

  it('should render target price', () => {
    render(<RecommendationCard recommendation={mockRecommendation} />);
    expect(screen.getByText('$200.00')).toBeInTheDocument();
  });

  it('should render stop loss', () => {
    render(<RecommendationCard recommendation={mockRecommendation} />);
    expect(screen.getByText('$150.00')).toBeInTheDocument();
  });

  it('should render rationale', () => {
    render(<RecommendationCard recommendation={mockRecommendation} />);
    expect(screen.getByText('Strong fundamentals and positive momentum')).toBeInTheDocument();
  });

  it('should render risks', () => {
    render(<RecommendationCard recommendation={mockRecommendation} />);
    expect(screen.getByText('Market volatility')).toBeInTheDocument();
    expect(screen.getByText('Sector rotation')).toBeInTheDocument();
  });

  it('should render strong_buy action correctly', () => {
    const strongBuyRec: Recommendation = {
      ...mockRecommendation,
      action: 'strong_buy',
    };
    render(<RecommendationCard recommendation={strongBuyRec} />);
    expect(screen.getByText('Strong Buy')).toBeInTheDocument();
  });

  it('should render sell action correctly', () => {
    const sellRec: Recommendation = {
      ...mockRecommendation,
      action: 'sell',
    };
    render(<RecommendationCard recommendation={sellRec} />);
    expect(screen.getByText('Sell')).toBeInTheDocument();
  });

  it('should render hold action correctly', () => {
    const holdRec: Recommendation = {
      ...mockRecommendation,
      action: 'hold',
    };
    render(<RecommendationCard recommendation={holdRec} />);
    expect(screen.getByText('Hold')).toBeInTheDocument();
  });
});
