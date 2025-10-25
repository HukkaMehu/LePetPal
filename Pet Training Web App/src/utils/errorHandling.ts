import { toast } from 'sonner';
import { APIError } from '../types';

/**
 * Display an error message to the user via toast notification
 */
export function showErrorToast(error: unknown, defaultMessage: string = 'An error occurred') {
  let message = defaultMessage;
  let description: string | undefined;

  if (error instanceof APIError) {
    message = error.message || defaultMessage;
    description = error.details ? JSON.stringify(error.details) : undefined;
  } else if (error instanceof Error) {
    message = error.message || defaultMessage;
  } else if (typeof error === 'string') {
    message = error;
  }

  toast.error(message, description ? { description } : undefined);
}

/**
 * Display a success message to the user via toast notification
 */
export function showSuccessToast(message: string, description?: string) {
  toast.success(message, description ? { description } : undefined);
}

/**
 * Display an info message to the user via toast notification
 */
export function showInfoToast(message: string, description?: string) {
  toast.info(message, description ? { description } : undefined);
}

/**
 * Display a warning message to the user via toast notification
 */
export function showWarningToast(message: string, description?: string) {
  toast.warning(message, description ? { description } : undefined);
}

/**
 * Get a user-friendly error message from an error object
 */
export function getErrorMessage(error: unknown, defaultMessage: string = 'An error occurred'): string {
  if (error instanceof APIError) {
    return error.message || defaultMessage;
  } else if (error instanceof Error) {
    return error.message || defaultMessage;
  } else if (typeof error === 'string') {
    return error;
  }
  return defaultMessage;
}

/**
 * Format validation errors for display
 */
export function formatValidationErrors(errors: Record<string, string[]>): string {
  return Object.entries(errors)
    .map(([field, messages]) => `${field}: ${messages.join(', ')}`)
    .join('\n');
}

/**
 * Check if an error is a network error
 */
export function isNetworkError(error: unknown): boolean {
  if (error instanceof APIError) {
    return error.status === 0 || error.status >= 500;
  }
  if (error instanceof Error) {
    return error.message.toLowerCase().includes('network') || 
           error.message.toLowerCase().includes('fetch');
  }
  return false;
}

/**
 * Check if an error is an authentication error
 */
export function isAuthError(error: unknown): boolean {
  if (error instanceof APIError) {
    return error.status === 401 || error.status === 403;
  }
  return false;
}

/**
 * Handle async operation with error handling and toast notifications
 */
export async function handleAsyncOperation<T>(
  operation: () => Promise<T>,
  options: {
    successMessage?: string;
    errorMessage?: string;
    onSuccess?: (result: T) => void;
    onError?: (error: unknown) => void;
  } = {}
): Promise<T | null> {
  try {
    const result = await operation();
    
    if (options.successMessage) {
      showSuccessToast(options.successMessage);
    }
    
    if (options.onSuccess) {
      options.onSuccess(result);
    }
    
    return result;
  } catch (error) {
    console.error('Operation failed:', error);
    
    showErrorToast(error, options.errorMessage);
    
    if (options.onError) {
      options.onError(error);
    }
    
    return null;
  }
}
