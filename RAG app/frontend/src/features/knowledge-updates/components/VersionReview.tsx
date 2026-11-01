import type { Version } from '../../../common/types/api';
import { useReviewVersionMutation } from '../api/updatesApi';
import { Button } from '../../../common/components/Button';
import { Notice } from '../../../common/components/Notice';
import { StatusBadge } from '../../../common/components/StatusBadge';
import { SourceLink } from '../../../common/components/SourceLink';
import { errorMessage, formatDate } from '../../../common/utils/format';

// Show source changes and explicit dates before a deliberate approval or rejection.
export function VersionReview({
  version,
  previous,
  isActive,
}: {
  version: Version;
  previous?: Version;
  isActive: boolean;
}) {
  const [review, { isLoading, error }] = useReviewVersionMutation();
  return (
    <section className="version-review" id="version-review">
      <div className="section-heading">
        <h3>Review source version</h3>
        <StatusBadge status={isActive ? 'active' : version.status} />
      </div>
      <h4>{version.title}</h4>
      <SourceLink url={version.url}>Open official source</SourceLink>
      <p>{version.summary}</p>
      <div className="date-grid">
        <div>
          <span>Source published</span>
          <strong>{formatDate(version.source_published_at)}</strong>
        </div>
        <div>
          <span>Source updated</span>
          <strong>{formatDate(version.source_updated_at)}</strong>
        </div>
        <div>
          <span>Fetched</span>
          <strong>{formatDate(version.fetched_at)}</strong>
        </div>
        <div>
          <span>Change detected</span>
          <strong>{formatDate(version.change_detected_at)}</strong>
        </div>
        <div>
          <span>Effective from</span>
          <strong>{formatDate(version.effective_from)}</strong>
        </div>
        <div>
          <span>Activated</span>
          <strong>{formatDate(version.activated_at)}</strong>
        </div>
      </div>
      <p className="small muted">
        A check or detection date does not establish when the authority published or changed its
        requirements.
      </p>
      {version.section_changes.length > 0 && (
        <details className="section-history">
          <summary>Section change history</summary>
          {version.section_changes.map((section, index) => (
            <div className="source-row" key={index}>
              <div>
                <strong>{section.locator}</strong>
                <p className="small muted">
                  Change observed: {formatDate(section.change_detected_at)}
                </p>
              </div>
              <StatusBadge status={section.status} />
            </div>
          ))}
          <p className="small muted">
            Unchanged sections keep their previous observed-change date. Renamed headings appear as
            removed/new sections; this is not an exact source edit timestamp.
          </p>
        </details>
      )}
      <div className="comparison">
        <div>
          <h4>Previous captured version</h4>
          <pre>
            {previous?.text ??
              (version.previous_version_id
                ? 'Previous content is outside the current history window; inspect the difference below.'
                : 'First captured version — no previous content.')}
          </pre>
        </div>
        <div>
          <h4>New captured version</h4>
          <pre>{version.text}</pre>
        </div>
      </div>
      <details className="diff">
        <summary>Inspect text difference</summary>
        <pre>{version.diff || 'Text unchanged; source-date metadata changed.'}</pre>
      </details>
      {error && <Notice error>{errorMessage(error)}</Notice>}
      {version.status === 'pending' && (
        <div className="review-actions">
          <Button
            disabled={isLoading}
            onClick={() => review({ id: version.id, action: 'approve' })}
          >
            Approve for chat
          </Button>
          <Button
            className="button-secondary"
            disabled={isLoading}
            onClick={() => review({ id: version.id, action: 'reject' })}
          >
            Reject version
          </Button>
        </div>
      )}
      <p className="small muted">Version {version.id}</p>
    </section>
  );
}
