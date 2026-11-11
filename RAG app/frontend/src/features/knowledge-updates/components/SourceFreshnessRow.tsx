import { sourceGroup } from '../utils/sourceStatus';
import type { Source } from '../../../common/types/api';
import { SourceLink } from '../../../common/components/SourceLink';
import { StatusBadge } from '../../../common/components/StatusBadge';
import { Button } from '../../../common/components/Button';
import { formatReviewDate } from '../../../common/utils/format';

// Show whether a URL has usable evidence and link directly to reviewable versions.
export function SourceFreshnessRow({
  source,
  onReview,
  expanded = false,
  onToggle,
}: {
  source: Source;
  onReview: (id: string) => void;
  expanded?: boolean;
  onToggle?: (open: boolean) => void;
}) {
  const pending = source.latest_version_status === 'pending';
  const status = sourceGroup(source);
  const checkedAt =
    source.last_checked_at ?? source.last_capture_at ?? source.last_successful_fetch_at;
  const dateLabel = checkedAt ? 'Checked' : 'Registered';
  const dateValue = checkedAt ?? source.registered_at;
  return (
    <details
      className="source-accordion"
      open={expanded}
      onToggle={(event) => onToggle?.(event.currentTarget.open)}
    >
      <summary>
        <span className="source-title">
          <span>{source.title}</span>
          <span className="source-date">
            {dateLabel}: {formatReviewDate(dateValue)}
          </span>
        </span>
        <StatusBadge status={status} />
        <span className="accordion-plus" aria-hidden="true">
          +
        </span>
      </summary>
      <div className="source-row">
        <div>
          <SourceLink url={source.url}>{source.title}</SourceLink>
          <p className="small muted">
            Last successful check: {formatReviewDate(source.last_successful_fetch_at)}
          </p>
          {source.registered_at && (
            <p className="small muted">Registered: {formatReviewDate(source.registered_at)}</p>
          )}
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
            <Button
              className="button-secondary"
              onClick={() => onReview(source.latest_version_id!)}
            >
              Review version
            </Button>
          )}
        </div>
      </div>
    </details>
  );
}
