import { AlertCircle } from 'lucide-react';
import { Alert, AlertDescription } from './ui/alert';

interface FormErrorProps {
  error?: string | null;
  className?: string;
}

/**
 * Display an inline error message in a form
 */
export function FormError({ error, className }: FormErrorProps) {
  if (!error) return null;

  return (
    <Alert variant="destructive" className={className}>
      <AlertCircle className="h-4 w-4" />
      <AlertDescription>{error}</AlertDescription>
    </Alert>
  );
}

interface FieldErrorProps {
  error?: string | null;
  className?: string;
}

/**
 * Display a small error message below a form field
 */
export function FieldError({ error, className }: FieldErrorProps) {
  if (!error) return null;

  return (
    <p className={`text-sm text-destructive flex items-center gap-1 ${className || ''}`}>
      <AlertCircle className="h-3 w-3" />
      {error}
    </p>
  );
}
