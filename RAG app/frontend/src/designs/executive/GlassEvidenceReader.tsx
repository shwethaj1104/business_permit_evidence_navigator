import { useId, useState } from 'react';
import {
  ArrowRight,
  BookOpen,
  Check,
  ChevronDown,
  FileClock,
  FileText,
  ShieldCheck,
} from 'lucide-react';
import type { Source, Version } from '../../common/types/api';
import type { KnowledgeWorkspaceModel } from '../../features/knowledge-updates/components/useKnowledgeWorkspace';
import { StatusBadge } from '../../common/components/StatusBadge';
import { formatReviewDate } from '../../common/utils/format';

type ReadingView = 'overview' | 'document' | 'changes';

// Format captured paragraphs and explicit headings without generating or changing requirements.
function CapturedText({ text }: { text: string }) {
  const blocks = text.split(/\n\s*\n/).filter((block) => block.trim());
  return (
    <div className="glass-reading-prose">
      {blocks.map((block, index) => {
        const lines = block.trim().split('\n');
        if (lines.every((line) => /^\s*(?:[-•*]|\d+[.)])\s+/.test(line)))
          return (
            <ul key={index}>
              {lines.map((line, row) => (
                <li key={row}>{line.replace(/^\s*(?:[-•*]|\d+[.)])\s+/, '')}</li>
              ))}
            </ul>
          );
        if (/^#{1,6}\s+/.test(lines[0]))
          return (
            <section key={index}>
              <h3>{lines[0].replace(/^#{1,6}\s+/, '')}</h3>
              {lines.length > 1 && <p>{lines.slice(1).join('\n')}</p>}
            </section>
          );
        if (lines[0].length < 100 && lines[0].endsWith(':') && lines.length > 1)
          return (
            <section key={index}>
              <h3>{lines[0]}</h3>
              <p>{lines.slice(1).join('\n')}</p>
            </section>
          );
        return <p key={index}>{block}</p>;
      })}
    </div>
  );
}

// Separate reading, change assessment and provenance while preserving every captured detail.
export function GlassEvidenceReader({
  version,
  source,
  model,
}: {
  version: Version;
  source: Source;
  model: KnowledgeWorkspaceModel;
}) {
  const [view, setView] = useState<ReadingView>('overview');
  const panel = useId();
  const preview =
    version.text.length > 480
      ? version.text.slice(0, 480).replace(/\s+\S*$/, '') + '…'
      : version.text;
  const views = [
    { id: 'overview', label: 'Overview', icon: BookOpen },
    { id: 'document', label: 'Document', icon: FileText },
    { id: 'changes', label: 'Changes', icon: FileClock },
  ] as const;
  return (
    <div className="glass-evidence-story">
      <div className="glass-reading-tabs" role="group" aria-label="Evidence reading views">
        {views.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            type="button"
            aria-pressed={view === id}
            aria-controls={panel}
            onClick={() => setView(id)}
          >
            <Icon size={15} />
            {label}
          </button>
        ))}
      </div>
      <div className="glass-provenance-strip">
        <span>
          Captured <strong>{formatReviewDate(version.fetched_at)}</strong>
        </span>
        <span>
          {version.previous_version_id
            ? `${version.section_changes.length} section changes`
            : 'First captured edition'}
        </span>
      </div>
      <div id={panel} className="glass-reader-view" key={view}>
        {view === 'overview' && (
          <>
            <section className="glass-story-summary">
              <span className="glass-story-label">AT A GLANCE</span>
              <h3>
                {version.previous_version_id
                  ? 'What this edition brings.'
                  : 'Your first look at the evidence.'}
              </h3>
              <p>{version.summary}</p>
            </section>
            <div className="glass-fact-pair">
              <div>
                <span>Published by authority</span>
                <strong>{formatReviewDate(version.source_published_at)}</strong>
              </div>
              <div>
                <span>Updated by authority</span>
                <strong>{formatReviewDate(version.source_updated_at)}</strong>
              </div>
            </div>
            <section className="glass-story-preview">
              <div className="glass-story-section-title">
                <h3>Inside the document</h3>
                <span>Preview</span>
              </div>
              <p>{preview}</p>
              <button
                className="glass-reading-link"
                type="button"
                onClick={() => setView('document')}
              >
                Read captured guidance <ArrowRight size={15} />
              </button>
            </section>
            <button
              type="button"
              className="glass-change-invitation"
              onClick={() => setView('changes')}
            >
              <span className="glass-change-symbol">
                <FileClock size={19} />
              </span>
              <span>
                <strong>Explore this capture</strong>
                <small>
                  {version.section_changes.length} recorded section changes · compare editions
                </small>
              </span>
              <ArrowRight size={16} />
            </button>
          </>
        )}
        {view === 'document' && (
          <section className="glass-reading-paper">
            <div className="glass-story-section-title">
              <h3>Captured guidance</h3>
              <span>Reading view</span>
            </div>
            <CapturedText text={version.text} />
            <details className="glass-reader-disclosure">
              <summary>
                Original captured text <ChevronDown size={15} />
              </summary>
              <pre tabIndex={0} role="region" aria-label="Original captured text">
                {version.text}
              </pre>
            </details>
          </section>
        )}
        {view === 'changes' && (
          <>
            <section className="glass-story-summary">
              <span className="glass-story-label">EDITION NOTES</span>
              <h3>
                {version.previous_version_id
                  ? 'See what changed.'
                  : 'A starting point for future comparisons.'}
              </h3>
              <p>{version.summary}</p>
            </section>
            <div className="glass-change-cards">
              {version.section_changes.length ? (
                version.section_changes.map((change, index) => (
                  <article key={index}>
                    <div>
                      <StatusBadge status={change.status} />
                      <span>{formatReviewDate(change.change_detected_at)}</span>
                    </div>
                    <h4>{change.locator}</h4>
                    {change.previous_change_detected_at && (
                      <p>
                        Previously observed {formatReviewDate(change.previous_change_detected_at)}
                      </p>
                    )}
                  </article>
                ))
              ) : (
                <p className="glass-reading-note">
                  No section-level changes were recorded for this edition.
                </p>
              )}
            </div>
            <details className="glass-reader-disclosure">
              <summary>
                Inspect recorded difference <ChevronDown size={15} />
              </summary>
              <div
                className="glass-readable-diff"
                tabIndex={0}
                role="region"
                aria-label="Recorded text difference"
              >
                {(version.diff || 'No text difference recorded; source metadata may have changed.')
                  .split('\n')
                  .map((line, index) => (
                    <div
                      key={index}
                      className={
                        line.startsWith('+')
                          ? 'diff-added'
                          : line.startsWith('-')
                            ? 'diff-removed'
                            : ''
                      }
                    >
                      {line || ' '}
                    </div>
                  ))}
              </div>
            </details>
            <details className="glass-reader-disclosure">
              <summary>
                Compare full captures <ChevronDown size={15} />
              </summary>
              <div className="glass-edition-comparison">
                <div>
                  <h4>Previous capture</h4>
                  {model.previousLoading ? (
                    <p role="status">Loading previous capture…</p>
                  ) : (
                    <pre tabIndex={0} role="region" aria-label="Previous captured text">
                      {model.previous?.text ?? 'No previous captured edition is available.'}
                    </pre>
                  )}
                </div>
                <div>
                  <h4>This capture</h4>
                  <pre tabIndex={0} role="region" aria-label="Current captured text">
                    {version.text}
                  </pre>
                </div>
              </div>
            </details>
          </>
        )}
      </div>
      <details className="glass-reader-disclosure glass-provenance-disclosure">
        <summary>
          Dates & provenance <ChevronDown size={15} />
        </summary>
        <div className="glass-provenance">
          <dl>
            {[
              ['Source published', version.source_published_at],
              ['Source updated', version.source_updated_at],
              ['Captured by this app', version.fetched_at],
              ['Change observed', version.change_detected_at],
              ['Effective from', version.effective_from],
              ['Reviewed', version.reviewed_at],
              ['Activated', version.activated_at],
            ].map(([label, date]) => (
              <div key={label}>
                <dt>{label}</dt>
                <dd>{formatReviewDate(date)}</dd>
              </div>
            ))}
          </dl>
          <p>
            Capture and observation dates do not establish when the authority published or changed
            its requirements.
          </p>
        </div>
      </details>
      {model.versions.filter((row) => row.source_id === source.id).length > 1 && (
        <details className="glass-reader-disclosure">
          <summary>
            Captured editions <ChevronDown size={15} />
          </summary>
          <div className="glass-version-buttons">
            {model.versions
              .filter((row) => row.source_id === source.id)
              .map((row) => (
                <button
                  type="button"
                  key={row.id}
                  onClick={() => model.selectVersion(row.id)}
                  aria-pressed={row.id === version.id}
                >
                  <span>{formatReviewDate(row.fetched_at)}</span>
                  <StatusBadge
                    status={source.active_version_id === row.id ? 'active' : row.status}
                  />
                </button>
              ))}
          </div>
        </details>
      )}
      <footer className="glass-review-footer">
        <span>
          <ShieldCheck size={16} />
          {model.isActive
            ? 'Available to the assistant'
            : version.status === 'pending'
              ? 'Review before publishing'
              : 'This edition is not active'}
        </span>
        {version.status === 'pending' && (
          <div>
            <button
              type="button"
              className="glass-secondary glass-reject"
              disabled={model.reviewLoading}
              onClick={() => model.review('reject')}
            >
              Reject
            </button>
            <button
              type="button"
              className="glass-primary"
              disabled={model.reviewLoading}
              onClick={() => model.review('approve')}
            >
              <Check size={15} />
              {model.reviewLoading ? 'Saving…' : 'Approve evidence'}
            </button>
          </div>
        )}
      </footer>
    </div>
  );
}
