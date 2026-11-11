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

// Capitalise compact UI labels without changing stored values or existing acronyms.
export function titleCaseLabel(value: string): string {
  return value.replaceAll('_', ' ').replace(/\b[a-z]/g, (letter) => letter.toUpperCase());
}

// Show review dates consistently in DD/MM/YYYY; preserve date-only authority metadata.
export function formatReviewDate(value?: string | null): string {
  if (!value) return 'Not stated';
  const dateOnly = /^(\d{4})-(\d{2})-(\d{2})$/.exec(value);
  if (dateOnly) return `${dateOnly[3]}/${dateOnly[2]}/${dateOnly[1]}`;
  const date = new Date(value);
  return Number.isNaN(date.getTime())
    ? 'Not stated'
    : new Intl.DateTimeFormat('en-GB', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        timeZone: 'Asia/Dubai',
      }).format(date);
}
