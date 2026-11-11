import { useId, type ReactNode } from 'react';
import { FileText } from 'lucide-react';
import { CopyChecklist } from './CopyChecklist';
import type { Answer } from '../../../common/types/api';
import { SourceLink } from '../../../common/components/SourceLink';
import { formatDate } from '../../../common/utils/format';

// Render checklist evidence as expandable citations rather than unsanitized model HTML.
export function AnswerCard({
  answer,
  profilePrompt,
}: {
  answer: Answer;
  profilePrompt?: ReactNode;
}) {
  const answerId = useId();
  return (
    <div className="answer-body">
      <p>{answer.message}</p>
      {profilePrompt}
      {answer.items.length > 0 && (
        <ol className="checklist">
          {answer.items.map((item, index) => (
            <li key={index}>
              <span className="check-number">{index + 1}</span>
              <div>
                <strong>{item.title}</strong>
                <p>{item.detail}</p>
                {item.condition && <p className="small muted">Applies when: {item.condition}</p>}
                <div className="citation-chips">
                  {item.evidence_ids.map((id) => (
                    <a
                      key={id}
                      href={`#evidence-${answerId}-${id}`}
                      onClick={(event) => {
                        // Reveal the cited source before moving keyboard focus within the chat.
                        const target = document.getElementById(`evidence-${answerId}-${id}`);
                        if (!(target instanceof HTMLDetailsElement)) return;
                        event.preventDefault();
                        target.open = true;
                        target.querySelector('summary')?.focus({ preventScroll: true });
                        const scroller = target.closest('.chat-history');
                        if (scroller instanceof HTMLElement)
                          scroller.scrollTo({
                            top:
                              target.getBoundingClientRect().top -
                              scroller.getBoundingClientRect().top +
                              scroller.scrollTop -
                              16,
                            behavior: 'instant',
                          });
                        window.history.replaceState(null, '', `#${target.id}`);
                      }}
                    >
                      Source {answer.citations.findIndex((row) => row.id === id) + 1}
                    </a>
                  ))}
                </div>
              </div>
            </li>
          ))}
        </ol>
      )}
      {answer.gaps.length > 0 && (
        <div className="gaps">
          <strong>Still to confirm</strong>
          <ul>
            {answer.gaps.map((gap, index) => (
              <li key={index}>{gap}</li>
            ))}
          </ul>
        </div>
      )}
      {answer.items.length > 0 && <CopyChecklist answer={answer} />}
      {answer.citations.length > 0 && (
        <div className="evidence-list">
          <h4>
            <FileText size={15} /> Supporting evidence
          </h4>
          {answer.citations.map((citation, index) => (
            <details key={citation.id} id={`evidence-${answerId}-${citation.id}`}>
              <summary>
                {index + 1}. {citation.title} · {citation.locator}
              </summary>
              <SourceLink url={citation.url}>Official source</SourceLink>
              {citation.newer_version_available && (
                <p className="gaps">
                  A newer captured version exists but is not active. This answer uses the cited
                  approved version; check Knowledge Updates.
                </p>
              )}
              <blockquote>{citation.excerpt}</blockquote>
              <p className="small muted">
                Published: {formatDate(citation.source_published_at)} · Source updated:{' '}
                {formatDate(citation.source_updated_at)}
              </p>
              <p className="small muted">
                Fetched: {formatDate(citation.fetched_at)} · Last successful check:{' '}
                {formatDate(citation.last_checked_at)}
              </p>
              <p className="small muted">Evidence version: {citation.version_id}</p>
            </details>
          ))}
        </div>
      )}
    </div>
  );
}
