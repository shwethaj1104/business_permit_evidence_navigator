import type { Source } from '../../../common/types/api';
import { SourceLink } from '../../../common/components/SourceLink';
import { StatusBadge } from '../../../common/components/StatusBadge';
import { Button } from '../../../common/components/Button';
import { formatDate } from '../../../common/utils/format';

// Show whether a URL has usable evidence and link directly to reviewable versions.
export function SourceFreshnessRow({
  source,
  onReview,
}: {
  source: Source;
  onReview: (id: string) => void;
}) {
  const pending = source.latest_version_status === 'pending';
  const status = source.active_version_id
    ? 'active'
    : pending
      ? 'pending'
      : source.last_capture_status === 'failed'
        ? 'failed'
        : (source.latest_version_status ?? 'registered');
  return (
    <div className="source-row">
      <div>
        <SourceLink url={source.url}>{source.title}</SourceLink>
        <p className="small muted">
          Last successful check: {formatDate(source.last_successful_fetch_at)}
        </p>
        {source.last_capture_error && (
          <p className="small source-capture-error">
            Latest capture failed: {source.last_capture_error}
          </p>
        )}
        {!source.latest_version_id && (
          <p className="small muted">
            No captured document to review yet. A successful capture is required before approval.
          </p>
        )}
      </div>
      <div className="source-actions">
        <StatusBadge status={status} />
        {pending && source.latest_version_id && (
          <Button className="button-secondary" onClick={() => onReview(source.latest_version_id!)}>
            Review version
          </Button>
        )}
      </div>
    </div>
  );
}
