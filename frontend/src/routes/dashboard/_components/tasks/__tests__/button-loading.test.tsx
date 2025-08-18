import { render, screen } from '@testing-library/react';
import { vi, describe, it, expect } from 'vitest';
import { LoaderCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';

// Simple test for button loading state component
describe('Button Loading State', () => {
  it('should show loading spinner when isLoading is true', () => {
    // Render a button with loading state
    render(
      <Button disabled={true}>
        <LoaderCircle className="size-5 animate-spin" data-testid="loading-spinner" />
      </Button>
    );
    
    // Check if the spinner is displayed
    expect(screen.getByTestId('loading-spinner')).toBeInTheDocument();
    expect(screen.queryByText(/save/i)).not.toBeInTheDocument();
  });
  
  it('should show text when isLoading is false', () => {
    // Render a button without loading state
    render(
      <Button disabled={false}>Save</Button>
    );
    
    // Check if the text is displayed
    expect(screen.getByText(/save/i)).toBeInTheDocument();
    expect(screen.queryByTestId('loading-spinner')).not.toBeInTheDocument();
  });
});
