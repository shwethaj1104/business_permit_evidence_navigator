// Provide a reusable, text-labeled status indicator.
export function StatusBadge({ status }: { status: string }) {
  return <span className={`badge badge-${status}`}>{status.replaceAll('_', ' ')}</span>;
}
