import { titleCaseLabel } from '../utils/format';

// Provide a reusable, text-labeled status indicator.
export function StatusBadge({ status }: { status: string }) {
  return <span className={`badge badge-${status}`}>{titleCaseLabel(status)}</span>;
}
