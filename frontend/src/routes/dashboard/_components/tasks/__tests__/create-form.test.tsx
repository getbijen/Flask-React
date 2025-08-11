import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter } from 'react-router-dom';
import { toast } from 'sonner';

// Component imports
import { CreateForm } from '../create-form';

// Mock imports
vi.mock('@/services/queries/tags', () => ({
  useGetTagsQuery: vi.fn(),
}));

vi.mock('@/services/mutations/tasks', () => ({
  useCreateTaskMutation: vi.fn(),
}));

vi.mock('@/stores/auth-store', () => ({
  useAuthStore: vi.fn(),
}));

vi.mock('sonner', () => ({
  toast: {
    success: vi.fn(),
    error: vi.fn(),
  },
}));

// Mock data
const mockTags = [
  { id: 1, name: 'Work' },
  { id: 2, name: 'Personal' },
  { id: 3, name: 'Shopping' },
];

const mockToken = 'mock-jwt-token';

const mockMutation = {
  mutateAsync: vi.fn(),
  isLoading: false,
  error: null,
};

// Test utilities
const renderWithProviders = (component: React.ReactElement) => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });

  return render(
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        {component}
      </BrowserRouter>
    </QueryClientProvider>
  );
};

// Test suite
describe('CreateForm Component', () => {
  let mockUseGetTagsQuery: any;
  let mockUseCreateTaskMutation: any;
  let mockUseAuthStore: any;

  beforeEach(() => {
    // Reset all mocks
    vi.clearAllMocks();

    // Setup mock implementations
    mockUseGetTagsQuery = vi.fn().mockReturnValue({
      data: mockTags,
      isLoading: false,
      error: null,
    });

    mockUseCreateTaskMutation = vi.fn().mockReturnValue(mockMutation);

    mockUseAuthStore = vi.fn().mockReturnValue({
      token: mockToken,
      isLoggedIn: true,
    });

    // Apply mocks
    vi.mocked(require('@/services/queries/tags').useGetTagsQuery).mockImplementation(mockUseGetTagsQuery);
    vi.mocked(require('@/services/mutations/tasks').useCreateTaskMutation).mockImplementation(mockUseCreateTaskMutation);
    vi.mocked(require('@/stores/auth-store').useAuthStore).mockImplementation(mockUseAuthStore);
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('Rendering', () => {
    it('should render all form fields correctly', () => {
      renderWithProviders(<CreateForm />);

      // Check if all form fields are present
      expect(screen.getByLabelText(/title/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/content/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/tag/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/status/i)).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /save/i })).toBeInTheDocument();
    });

    it('should display all available tags in the tag select', () => {
      renderWithProviders(<CreateForm />);

      // Open tag select
      const tagSelect = screen.getByLabelText(/tag/i);
      fireEvent.click(tagSelect);

      // Check if all tags are displayed
      expect(screen.getByText('Work')).toBeInTheDocument();
      expect(screen.getByText('Personal')).toBeInTheDocument();
      expect(screen.getByText('Shopping')).toBeInTheDocument();
    });

    it('should display all status options in the status select', () => {
      renderWithProviders(<CreateForm />);

      // Open status select
      const statusSelect = screen.getByLabelText(/status/i);
      fireEvent.click(statusSelect);

      // Check if all statuses are displayed
      expect(screen.getByText('Pending')).toBeInTheDocument();
      expect(screen.getByText('In Progress')).toBeInTheDocument();
      expect(screen.getByText('Completed')).toBeInTheDocument();
    });
  });

  describe('Form Validation', () => {
    it('should show validation errors for empty required fields', async () => {
      const user = userEvent.setup();
      renderWithProviders(<CreateForm />);

      // Try to submit empty form
      const submitButton = screen.getByRole('button', { name: /save/i });
      await user.click(submitButton);

      // Check for validation errors
      await waitFor(() => {
        expect(screen.getByText(/title is required/i)).toBeInTheDocument();
        expect(screen.getByText(/content is required/i)).toBeInTheDocument();
        expect(screen.getByText(/tag is required/i)).toBeInTheDocument();
        expect(screen.getByText(/status is required/i)).toBeInTheDocument();
      });
    });

    it('should validate title length constraints', async () => {
      const user = userEvent.setup();
      renderWithProviders(<CreateForm />);

      const titleInput = screen.getByLabelText(/title/i);
      
      // Test minimum length
      await user.type(titleInput, '');
      await user.click(screen.getByRole('button', { name: /save/i }));
      
      await waitFor(() => {
        expect(screen.getByText(/title is required/i)).toBeInTheDocument();
      });

      // Test maximum length (40 characters)
      await user.clear(titleInput);
      await user.type(titleInput, 'a'.repeat(41));
      await user.click(screen.getByRole('button', { name: /save/i }));
      
      await waitFor(() => {
        expect(screen.getByText(/max length is 40 characters/i)).toBeInTheDocument();
      });
    });

    it('should validate content length constraints', async () => {
      const user = userEvent.setup();
      renderWithProviders(<CreateForm />);

      const contentInput = screen.getByLabelText(/content/i);
      
      // Test minimum length
      await user.type(contentInput, '');
      await user.click(screen.getByRole('button', { name: /save/i }));
      
      await waitFor(() => {
        expect(screen.getByText(/content is required/i)).toBeInTheDocument();
      });

      // Test maximum length (600 characters)
      await user.clear(contentInput);
      await user.type(contentInput, 'a'.repeat(601));
      await user.click(screen.getByRole('button', { name: /save/i }));
      
      await waitFor(() => {
        expect(screen.getByText(/max length is 600 characters/i)).toBeInTheDocument();
      });
    });
  });

  describe('Form Submission', () => {
    it('should submit form with valid data successfully', async () => {
      const user = userEvent.setup();
      const mockMutateAsync = vi.fn().mockResolvedValue(undefined);
      
      mockMutation.mutateAsync = mockMutateAsync;
      
      renderWithProviders(<CreateForm />);

      // Fill in form data
      await user.type(screen.getByLabelText(/title/i), 'Test Task');
      await user.type(screen.getByLabelText(/content/i), 'Test content for the task');
      
      // Select tag
      const tagSelect = screen.getByLabelText(/tag/i);
      await user.click(tagSelect);
      await user.click(screen.getByText('Work'));
      
      // Select status
      const statusSelect = screen.getByLabelText(/status/i);
      await user.click(statusSelect);
      await user.click(screen.getByText('Pending'));

      // Submit form
      const submitButton = screen.getByRole('button', { name: /save/i });
      await user.click(submitButton);

      // Verify mutation was called with correct data
      await waitFor(() => {
        expect(mockMutateAsync).toHaveBeenCalledWith({
          token: mockToken,
          formData: {
            title: 'Test Task',
            content: 'Test content for the task',
            tagId: '1',
            status: 'PENDING',
          },
        });
      });

      // Verify success toast was shown
      expect(toast.success).toHaveBeenCalledWith('Task successfully created');
    });

    it('should show loading state during submission', async () => {
      const user = userEvent.setup();
      const mockMutateAsync = vi.fn().mockImplementation(() => new Promise(resolve => setTimeout(resolve, 100)));
      
      mockMutation.mutateAsync = mockMutateAsync;
      mockMutation.isLoading = true;
      
      renderWithProviders(<CreateForm />);

      // Fill in form data
      await user.type(screen.getByLabelText(/title/i), 'Test Task');
      await user.type(screen.getByLabelText(/content/i), 'Test content');
      
      // Select tag and status
      const tagSelect = screen.getByLabelText(/tag/i);
      await user.click(tagSelect);
      await user.click(screen.getByText('Work'));
      
      const statusSelect = screen.getByLabelText(/status/i);
      await user.click(statusSelect);
      await user.click(screen.getByText('Pending'));

      // Submit form
      const submitButton = screen.getByRole('button', { name: /save/i });
      await user.click(submitButton);

      // Check loading state
      expect(screen.getByTestId('loader')).toBeInTheDocument();
      expect(submitButton).toBeDisabled();
    });

    it('should reset form after successful submission', async () => {
      const user = userEvent.setup();
      const mockMutateAsync = vi.fn().mockResolvedValue(undefined);
      
      mockMutation.mutateAsync = mockMutateAsync;
      
      renderWithProviders(<CreateForm />);

      // Fill in form data
      await user.type(screen.getByLabelText(/title/i), 'Test Task');
      await user.type(screen.getByLabelText(/content/i), 'Test content');
      
      // Select tag and status
      const tagSelect = screen.getByLabelText(/tag/i);
      await user.click(tagSelect);
      await user.click(screen.getByText('Work'));
      
      const statusSelect = screen.getByLabelText(/status/i);
      await user.click(statusSelect);
      await user.click(screen.getByText('Pending'));

      // Submit form
      const submitButton = screen.getByRole('button', { name: /save/i });
      await user.click(submitButton);

      // Verify form was reset
      await waitFor(() => {
        expect(screen.getByLabelText(/title/i)).toHaveValue('');
        expect(screen.getByLabelText(/content/i)).toHaveValue('');
        expect(screen.getByLabelText(/tag/i)).toHaveValue('');
        expect(screen.getByLabelText(/status/i)).toHaveValue('');
      });
    });
  });

  describe('Error Handling', () => {
    it('should handle mutation errors gracefully', async () => {
      const user = userEvent.setup();
      const mockMutateAsync = vi.fn().mockRejectedValue(new Error('API Error'));
      
      mockMutation.mutateAsync = mockMutateAsync;
      
      renderWithProviders(<CreateForm />);

      // Fill in form data
      await user.type(screen.getByLabelText(/title/i), 'Test Task');
      await user.type(screen.getByLabelText(/content/i), 'Test content');
      
      // Select tag and status
      const tagSelect = screen.getByLabelText(/tag/i);
      await user.click(tagSelect);
      await user.click(screen.getByText('Work'));
      
      const statusSelect = screen.getByLabelText(/status/i);
      await user.click(statusSelect);
      await user.click(screen.getByText('Pending'));

      // Submit form
      const submitButton = screen.getByRole('button', { name: /save/i });
      await user.click(submitButton);

      // Verify error was handled
      await waitFor(() => {
        expect(mockMutateAsync).toHaveBeenCalled();
      });
    });
  });

  describe('Accessibility', () => {
    it('should have proper form labels and associations', () => {
      renderWithProviders(<CreateForm />);

      // Check label associations
      expect(screen.getByLabelText(/title/i)).toHaveAttribute('id');
      expect(screen.getByLabelText(/content/i)).toHaveAttribute('id');
      expect(screen.getByLabelText(/tag/i)).toHaveAttribute('id');
      expect(screen.getByLabelText(/status/i)).toHaveAttribute('id');
    });

    it('should disable form fields during submission', async () => {
      const user = userEvent.setup();
      mockMutation.isLoading = true;
      
      renderWithProviders(<CreateForm />);

      // Check if fields are disabled
      expect(screen.getByLabelText(/title/i)).toBeDisabled();
      expect(screen.getByLabelText(/content/i)).toBeDisabled();
      expect(screen.getByLabelText(/tag/i)).toBeDisabled();
      expect(screen.getByLabelText(/status/i)).toBeDisabled();
      expect(screen.getByRole('button', { name: /save/i })).toBeDisabled();
    });
  });
}); 