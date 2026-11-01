// Display date-only source metadata without inventing a time or timezone.
export function formatDate(value?: string | null): string {
  if (!value) return 'Not stated';
  if (/^\d{4}-\d{2}-\d{2}$/.test(value)) return value;
  const date = new Date(value);
  return Number.isNaN(date.getTime())
    ? value
    : date.toLocaleString(undefined, { dateStyle: 'medium', timeStyle: 'short' });
}

// Convert safe backend and transport errors to an actionable UI message.
export function errorMessage(error: unknown): string {
  if (error && typeof error === 'object' && 'data' in error) {
    const data = error.data;
    if (data && typeof data === 'object' && 'detail' in data && typeof data.detail === 'string')
      return data.detail;
  }
  return 'Could not complete the request. Check the backend is running and try again.';
}

// Permit only HTTPS source links when rendering backend-provided evidence.
export function safeSourceUrl(value: string): string | undefined {
  try {
    const url = new URL(value);
    return url.protocol === 'https:' ? url.href : undefined;
  } catch {
    return undefined;
  }
}
