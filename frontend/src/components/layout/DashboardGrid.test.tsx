import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '../../test/test-utils';
import {
  DashboardGrid,
  GridItem,
  PageContainer,
  Card,
  StatCard,
  LoadingState,
  ErrorState,
  EmptyState,
} from './DashboardGrid';

describe('DashboardGrid', () => {
  it('should render children', () => {
    render(
      <DashboardGrid>
        <div data-testid="child">Child content</div>
      </DashboardGrid>
    );
    expect(screen.getByTestId('child')).toBeInTheDocument();
  });

  it('should apply grid classes', () => {
    const { container } = render(
      <DashboardGrid columns={2} gap="md">
        <div>Content</div>
      </DashboardGrid>
    );
    expect(container.firstChild).toHaveClass('grid');
    expect(container.firstChild).toHaveClass('gap-4');
  });
});

describe('GridItem', () => {
  it('should render children', () => {
    render(
      <GridItem>
        <div data-testid="child">Content</div>
      </GridItem>
    );
    expect(screen.getByTestId('child')).toBeInTheDocument();
  });
});

describe('PageContainer', () => {
  it('should render title', () => {
    render(<PageContainer title="Test Title">Content</PageContainer>);
    expect(screen.getByText('Test Title')).toBeInTheDocument();
  });

  it('should render subtitle', () => {
    render(
      <PageContainer title="Title" subtitle="Test subtitle">
        Content
      </PageContainer>
    );
    expect(screen.getByText('Test subtitle')).toBeInTheDocument();
  });

  it('should render children', () => {
    render(
      <PageContainer title="Title">
        <div data-testid="content">Page content</div>
      </PageContainer>
    );
    expect(screen.getByTestId('content')).toBeInTheDocument();
  });

  it('should render actions', () => {
    render(
      <PageContainer title="Title" actions={<button>Action</button>}>
        Content
      </PageContainer>
    );
    expect(screen.getByRole('button', { name: 'Action' })).toBeInTheDocument();
  });
});

describe('Card', () => {
  it('should render title', () => {
    render(<Card title="Card Title">Content</Card>);
    expect(screen.getByText('Card Title')).toBeInTheDocument();
  });

  it('should render children', () => {
    render(
      <Card>
        <div data-testid="content">Card content</div>
      </Card>
    );
    expect(screen.getByTestId('content')).toBeInTheDocument();
  });

  it('should render actions', () => {
    render(
      <Card title="Title" actions={<button>Edit</button>}>
        Content
      </Card>
    );
    expect(screen.getByRole('button', { name: 'Edit' })).toBeInTheDocument();
  });
});

describe('StatCard', () => {
  it('should render label and value', () => {
    render(<StatCard label="Revenue" value="$10,000" />);
    expect(screen.getByText('Revenue')).toBeInTheDocument();
    expect(screen.getByText('$10,000')).toBeInTheDocument();
  });

  it('should render change when provided', () => {
    render(<StatCard label="Revenue" value="$10,000" change={5.5} />);
    expect(screen.getByText(/5\.50%/)).toBeInTheDocument();
  });

  it('should render change label when provided', () => {
    render(<StatCard label="Revenue" value="$10,000" change={5} changeLabel="today" />);
    expect(screen.getByText('today')).toBeInTheDocument();
  });
});

describe('LoadingState', () => {
  it('should render default message', () => {
    render(<LoadingState />);
    expect(screen.getByText('Loading...')).toBeInTheDocument();
  });

  it('should render custom message', () => {
    render(<LoadingState message="Please wait..." />);
    expect(screen.getByText('Please wait...')).toBeInTheDocument();
  });
});

describe('ErrorState', () => {
  it('should render error title and message', () => {
    render(<ErrorState message="Something went wrong" />);
    expect(screen.getByText('Error')).toBeInTheDocument();
    expect(screen.getByText('Something went wrong')).toBeInTheDocument();
  });

  it('should render custom title', () => {
    render(<ErrorState title="Network Error" message="Failed to connect" />);
    expect(screen.getByText('Network Error')).toBeInTheDocument();
  });

  it('should render retry button when onRetry provided', () => {
    const onRetry = vi.fn();
    render(<ErrorState message="Error" onRetry={onRetry} />);

    const button = screen.getByRole('button', { name: 'Try Again' });
    expect(button).toBeInTheDocument();

    button.click();
    expect(onRetry).toHaveBeenCalledTimes(1);
  });
});

describe('EmptyState', () => {
  it('should render title and message', () => {
    render(<EmptyState title="No data" message="There is no data to display" />);
    expect(screen.getByText('No data')).toBeInTheDocument();
    expect(screen.getByText('There is no data to display')).toBeInTheDocument();
  });

  it('should render action button when provided', () => {
    const onClick = vi.fn();
    render(
      <EmptyState
        title="No items"
        message="Get started by adding an item"
        action={{ label: 'Add Item', onClick }}
      />
    );

    const button = screen.getByRole('button', { name: 'Add Item' });
    expect(button).toBeInTheDocument();

    button.click();
    expect(onClick).toHaveBeenCalledTimes(1);
  });
});
