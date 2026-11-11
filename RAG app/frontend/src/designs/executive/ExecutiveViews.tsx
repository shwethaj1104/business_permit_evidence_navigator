import { GlassEvidenceReader } from './GlassEvidenceReader';
import { GlassWelcomeMotion } from './GlassWelcomeMotion';
import { sourceDisplayTitle } from '../../common/utils/sourceTitle';
import { ChatAtmosphere } from '../../common/components/ChatAtmosphere';
import { useSelectionMotion } from '../../common/hooks/useSelectionMotion';
import { RequestActivity } from '../../common/components/RequestActivity';
import { SourceRetry } from '../../common/components/SourceRetry';
import { useEffect, useState } from 'react';
import {
  ChevronDown,
  ChevronLeft,
  Clock3,
  FileText,
  Globe,
  History,
  Layers,
  MessageSquare,
  Plus,
  Search,
  SendHorizontal,
  ShieldCheck,
  SlidersHorizontal,
  RefreshCw,
  PanelLeftClose,
} from 'lucide-react';
import type { ChatWorkspaceModel } from '../../features/checklist-chat/components/useChatWorkspace';
import type { KnowledgeWorkspaceModel } from '../../features/knowledge-updates/components/useKnowledgeWorkspace';
import type { Source } from '../../common/types/api';
import { AnswerCard } from '../../features/checklist-chat/components/AnswerCard';
import { SourceLink } from '../../common/components/SourceLink';
import { StatusBadge } from '../../common/components/StatusBadge';
import { Notice } from '../../common/components/Notice';
import { formatReviewDate } from '../../common/utils/format';
import { ExecutiveWelcome } from './ExecutiveDesign';

// Compose saved conversations, clear messages and a grounded input as an independent glass workspace.
export function ExecutiveChatView({ model }: { model: ChatWorkspaceModel }) {
  return (
    <section className="glass-chat">
      <aside
        className={`glass-conversations ${model.historyOpen ? 'is-open' : ''}`}
        onKeyDown={(event) => {
          if (event.key === 'Escape') {
            event.preventDefault();
            model.setHistoryOpen(false);
            document
              .querySelector<HTMLButtonElement>('[aria-label="Open conversations"]')
              ?.focus({ preventScroll: true });
          }
        }}
      >
        <div className="glass-rail-heading">
          <span>
            <MessageSquare size={15} />
            Conversations
          </span>
          <button
            className="glass-icon-button glass-mobile-only"
            aria-label="Close conversations"
            onClick={() => {
              model.setHistoryOpen(false);
              document
                .querySelector<HTMLElement>('[aria-label="Open conversations"]')
                ?.focus({ preventScroll: true });
            }}
          >
            <PanelLeftClose size={17} />
          </button>
        </div>
        <button className="glass-new-chat" onClick={model.newChat} disabled={model.isLoading}>
          <Plus size={17} />
          New conversation
        </button>
        <div className="glass-history-scroll">{model.history}</div>
        <div className="glass-rail-foot">
          <ShieldCheck size={16} />
          <span>
            Reviewed evidence.
            <br />
            Clearer preparation.
          </span>
        </div>
      </aside>
      <div className="glass-conversation">
        <ChatAtmosphere />
        <header className="glass-thread-heading">
          <div>
            <span className="glass-crumb">YOUR WORKSPACE</span>
            <h2>Business assistant</h2>
          </div>
          <div className="glass-thread-meta">
            <span>
              <ShieldCheck size={14} />
              Evidence-backed guidance
            </span>
            <button
              className="glass-icon-button glass-mobile-only"
              aria-label="Open conversations"
              onClick={() => {
                model.setHistoryOpen(true);
                requestAnimationFrame(() =>
                  document
                    .querySelector<HTMLElement>('.glass-conversations button')
                    ?.focus({ preventScroll: true }),
                );
              }}
            >
              <History size={19} />
            </button>
          </div>
        </header>
        <div className="chat-history glass-message-scroll" aria-live="polite">
          {model.conversation?.has_older && (
            <button
              className="glass-secondary"
              disabled={model.loadingHistory || model.isLoading}
              onClick={model.loadEarlier}
            >
              Load earlier messages
            </button>
          )}
          {model.loadingHistory && !model.conversation && (
            <p role="status" className="glass-loading">
              Loading conversation…
            </p>
          )}
          {!model.loadingHistory && !model.conversation?.messages.length && (
            <ExecutiveWelcome onPrompt={(message) => void model.submit(message)} />
          )}
          {model.conversation?.messages.map((message) => (
            <article
              key={message.id}
              className={`glass-message glass-message-${message.role}`}
              ref={message.id === model.newestMessageId ? model.newest : undefined}
            >
              <div className="glass-message-author">
                {message.role === 'user' ? (
                  'You'
                ) : (
                  <>
                    <span className="glass-author-mark">
                      <img src="/favicon.svg" width="18" height="18" alt="" />
                    </span>
                    Permit Navigator
                  </>
                )}
              </div>
              {message.answer ? (
                <AnswerCard answer={message.answer} profilePrompt={model.profilePrompt(message)} />
              ) : (
                <p>{message.text}</p>
              )}
            </article>
          ))}
          {model.isLoading && (
            <div className="glass-thinking" role="status">
              <RequestActivity text="Preparing your response…" />
            </div>
          )}
          {model.error && <Notice error>{model.error}</Notice>}
          <div ref={model.end} />
        </div>
        <div className="glass-composer-area">
          <form
            className="glass-composer"
            data-input-invitation={
              (!model.loadingHistory &&
                !model.isLoading &&
                !model.conversation?.messages.length &&
                !model.text.length) ||
              undefined
            }
            onSubmit={(event) => {
              event.preventDefault();
              void model.submit(model.text);
            }}
          >
            <textarea
              ref={model.input}
              aria-label="Your licensing question"
              placeholder="Ask about your business setup…"
              value={model.text}
              onChange={(event) => model.setText(event.target.value)}
              disabled={model.isLoading || model.loadingHistory}
              rows={1}
              maxLength={4000}
              onKeyDown={(event) => {
                if (event.key === 'Enter' && !event.shiftKey && !event.nativeEvent.isComposing) {
                  event.preventDefault();
                  void model.submit(model.text);
                }
              }}
            />
            <button
              type="submit"
              aria-label="Send question"
              disabled={!model.text.trim() || model.isLoading || model.loadingHistory}
            >
              <SendHorizontal size={19} />
            </button>
          </form>
        </div>
      </div>
    </section>
  );
}

// Classify the latest capture separately from the source's available published evidence.
function captureLabel(source: Source) {
  if (source.last_capture_status === 'failed') return 'Capture failed';
  if (source.latest_version_status === 'pending') return 'Review';
  if (source.active_version_id) return 'Published';
  return source.latest_version_id ? 'Captured' : 'Registered';
}

// Present a searchable document library and an independent reading pane with real review controls.
export function ExecutiveKnowledgeView({ model }: { model: KnowledgeWorkspaceModel }) {
  useSelectionMotion(model.selected?.id, '.glass-document-reader');
  const [query, setQuery] = useState('');
  const [filter, setFilter] = useState<'all' | 'review' | 'published' | 'failed'>('all');
  const [sourceId, setSourceId] = useState<string | null>(null);
  const [readerOpen, setReaderOpen] = useState(false);
  const [contextOpen, setContextOpen] = useState(!model.profile);
  useEffect(() => {
    setSourceId(null);
    setReaderOpen(false);
    setQuery('');
  }, [model.profile?.id]);
  const filtered = model.sources.filter(
    (source) =>
      (!query ||
        `${sourceDisplayTitle(source, model.versions.find((version) => version.id === source.latest_version_id)?.title)} ${source.url}`
          .toLowerCase()
          .includes(query.toLowerCase())) &&
      (filter === 'all' ||
        (filter === 'review' && source.latest_version_status === 'pending') ||
        (filter === 'published' && !!source.active_version_id) ||
        (filter === 'failed' && source.last_capture_status === 'failed')),
  );
  const source = model.sources.find((row) => row.id === sourceId);
  const version = source && model.selected?.source_id === source.id ? model.selected : undefined;
  // Open the source's newest capture without changing any approval state.
  function openSource(row: Source) {
    setSourceId(row.id);
    setReaderOpen(true);
    model.selectVersion(row.latest_version_id ?? row.active_version_id);
  }
  return (
    <section className="glass-knowledge" aria-label="Knowledge workspace">
      <section className="glass-context">
        <div className="glass-context-header">
          <button
            className="glass-context-trigger"
            aria-expanded={contextOpen}
            onClick={() => setContextOpen(!contextOpen)}
          >
            <SlidersHorizontal size={17} />
            <span>Business context</span>
            <ChevronDown size={17} />
          </button>
          <div className="glass-library-options">
            <div className="glass-discovery-option">
              <label>
                <input
                  type="checkbox"
                  checked={model.discover}
                  disabled={!model.profile || model.running || model.isLoading}
                  onChange={(event) => model.setDiscover(event.target.checked)}
                />
                Discover additional official sources
              </label>
              {model.profile && (
                <span>
                  {model.discover
                    ? 'Find new URLs and refresh registered sources.'
                    : 'Refresh registered URLs only.'}
                </span>
              )}
            </div>
            <button
              className="glass-primary"
              onClick={model.sync}
              disabled={!model.profile || model.running || model.isLoading}
            >
              <RefreshCw size={16} className={model.running ? 'spin' : ''} />
              {model.running
                ? 'Syncing sources'
                : model.isLoading
                  ? 'Starting sync…'
                  : 'Sync official sources'}
            </button>
          </div>
        </div>
        {contextOpen && (
          <div
            className="glass-context-fields"
            onKeyDown={(event) => {
              if (event.key === 'Escape') {
                event.preventDefault();
                setContextOpen(false);
                document
                  .querySelector<HTMLButtonElement>('.glass-context-trigger')
                  ?.focus({ preventScroll: true });
              }
            }}
          >
            {model.profileControls}
          </div>
        )}
      </section>
      {model.error && <Notice error>{model.error}</Notice>}
      <div className={`glass-document-workspace ${readerOpen ? 'reader-open' : ''}`}>
        <aside className="glass-document-list">
          <div className="glass-document-toolbar">
            <label className="glass-search">
              <Search size={17} />
              <input
                value={query}
                onChange={(event) => setQuery(event.target.value)}
                placeholder="Find a source…"
                aria-label="Search official sources"
                disabled={!model.profile}
              />
            </label>
            <div className="glass-library-tabs" role="group" aria-label="Filter document library">
              {(['all', 'review', 'published', 'failed'] as const).map((value) => (
                <button
                  key={value}
                  aria-pressed={filter === value}
                  onClick={() => setFilter(value)}
                >
                  {value === 'all'
                    ? 'All sources'
                    : value === 'review'
                      ? 'Needs review'
                      : value === 'published'
                        ? 'Published'
                        : 'Failed'}
                </button>
              ))}
            </div>
            <span className="glass-result-count" role="status">
              {model.profile
                ? `${filtered.length} source${filtered.length === 1 ? '' : 's'}`
                : 'Select a profile to load sources'}
            </span>
          </div>
          <div className="glass-source-list">
            {model.sourcesLoading && (
              <p className="glass-loading" role="status">
                Loading official sources…
              </p>
            )}
            {filtered.map((row) => (
              <button
                className={`glass-source-item ${sourceId === row.id ? 'selected' : ''}`}
                key={row.id}
                onClick={() => openSource(row)}
                aria-pressed={sourceId === row.id}
              >
                <span className="glass-file-icon">
                  <FileText size={20} />
                </span>
                <span className="glass-file-description">
                  <strong>
                    {sourceDisplayTitle(
                      row,
                      model.versions.find((version) => version.id === row.latest_version_id)?.title,
                    )}
                  </strong>
                  <span>{new URL(row.url).hostname}</span>
                  <small>
                    {row.last_checked_at
                      ? `Checked ${formatReviewDate(row.last_checked_at)}`
                      : `Registered ${formatReviewDate(row.registered_at)}`}
                  </small>
                </span>
                <span
                  className={`glass-source-state state-${row.last_capture_status === 'failed' ? 'failed' : row.latest_version_status === 'pending' ? 'review' : row.active_version_id ? 'published' : 'registered'}`}
                >
                  {captureLabel(row)}
                </span>
              </button>
            ))}
            {model.profile && model.sourceFailed && (
              <SourceRetry onRetry={model.retrySources} busy={model.sourcesLoading} />
            )}
            {model.profile && !model.sourceFailed && !model.sourcesLoading && !filtered.length && (
              <div className="glass-library-empty">
                <FileText size={28} />
                <strong>
                  {query || filter !== 'all'
                    ? 'No matching sources'
                    : 'Your library is ready to fill'}
                </strong>
                <p>
                  {query || filter !== 'all'
                    ? 'Try another search or show all sources.'
                    : 'Sync official sources to capture evidence for review.'}
                </p>
                {(query || filter !== 'all') && (
                  <button
                    className="glass-secondary"
                    onClick={() => {
                      setQuery('');
                      setFilter('all');
                    }}
                  >
                    Clear filters
                  </button>
                )}
              </div>
            )}
            {!model.profile && (
              <div className="glass-library-empty">
                <Layers size={28} />
                <strong>Set your business context</strong>
                <p>Choose your emirate and activity above to open the relevant source library.</p>
              </div>
            )}
          </div>
          {model.latest && (
            <details className="glass-sync-log">
              <summary>
                <span>
                  <Clock3 size={15} />
                  Latest sync
                </span>
                <StatusBadge status={model.latest.status} />
                <ChevronDown size={15} />
              </summary>
              <div>
                <p>Requested {formatReviewDate(model.latest.created_at)}</p>
                {model.latest.outcomes.map((outcome, index) => (
                  <div className="glass-sync-outcome" key={index}>
                    <StatusBadge status={outcome.status} />
                    <p>{outcome.summary}</p>
                  </div>
                ))}
                {model.latest.error && <Notice error>{model.latest.error}</Notice>}
                <button className="glass-text-button" onClick={model.refresh}>
                  Refresh status
                </button>
                {model.running && (
                  <button
                    className="glass-text-button"
                    onClick={model.retry}
                    disabled={model.isLoading}
                  >
                    Retry worker launch
                  </button>
                )}
              </div>
            </details>
          )}
        </aside>
        <section className="glass-document-reader" aria-label="Source reading pane">
          <button className="glass-reader-back" onClick={() => setReaderOpen(false)}>
            <ChevronLeft size={17} />
            Back to sources
          </button>
          {!source ? (
            <div className="glass-reader-empty">
              <GlassWelcomeMotion scene="knowledge" />

              <span className="glass-overline">YOUR EVIDENCE COLLECTION</span>
              <h2>Guidance, brought into focus.</h2>
              <p>Select a source to read its guidance and review what changed.</p>
              <span>
                <ShieldCheck size={15} />
                Only approved evidence informs checklist answers.
              </span>
            </div>
          ) : (
            <>
              <header className="glass-reader-heading">
                <div>
                  <span className="glass-overline">OFFICIAL SOURCE</span>
                  <h2>{sourceDisplayTitle(source, version?.title)}</h2>
                  <SourceLink url={source.url}>Open official website</SourceLink>
                </div>
                <span className="glass-reader-source-state">
                  {version ? (
                    <StatusBadge status={model.isActive ? 'active' : version.status} />
                  ) : (
                    <span>{captureLabel(source)}</span>
                  )}
                </span>
              </header>
              {version && source.last_capture_error && (
                <Notice error>
                  Latest capture failed: {source.last_capture_error} Previously approved evidence
                  may remain available.
                </Notice>
              )}
              {model.detailLoading ? (
                <div className="glass-reader-registration" role="status">
                  Loading captured document…
                </div>
              ) : version ? (
                <GlassEvidenceReader
                  key={version.id}
                  version={version}
                  source={source}
                  model={model}
                />
              ) : (
                <div className="glass-reader-registration">
                  <Globe size={28} />
                  <h3>
                    {source.last_capture_status === 'failed'
                      ? 'This source needs another capture'
                      : 'No captured document yet'}
                  </h3>
                  <p>
                    {source.last_capture_error ??
                      'The source is registered. Sync it to capture content before review.'}
                  </p>
                  <div>
                    <span>Registered {formatReviewDate(source.registered_at)}</span>
                    <span>Last checked {formatReviewDate(source.last_checked_at)}</span>
                  </div>
                  <button
                    className="glass-secondary"
                    onClick={model.sync}
                    disabled={model.running || model.isLoading}
                  >
                    <RefreshCw size={16} />
                    Sync official sources
                  </button>
                </div>
              )}
            </>
          )}
        </section>
      </div>
    </section>
  );
}
