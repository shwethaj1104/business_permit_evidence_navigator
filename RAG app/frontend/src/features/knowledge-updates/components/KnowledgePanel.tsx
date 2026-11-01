import { useEffect, useState } from 'react';
import { skipToken } from '@reduxjs/toolkit/query';
import { Database, RefreshCw, Globe, Clock3 } from 'lucide-react';
import {
  useGetSourcesQuery,
  useGetVersionsQuery,
  useGetVersionQuery,
  useGetJobsQuery,
  useStartSyncMutation,
} from '../api/updatesApi';
import { selectVersion, setDiscovery } from '../store/updatesSlice';
import { selectUpdates } from '../store/updatesSelectors';
import { useSelectedProfile } from '../../business-profile/hooks/useSelectedProfile';
import { useAppDispatch, useAppSelector } from '../../../store/hooks';
import { baseApi } from '../../../common/api/baseApi';
import { Button } from '../../../common/components/Button';
import { Notice } from '../../../common/components/Notice';
import { StatusBadge } from '../../../common/components/StatusBadge';
import { SourceFreshnessRow } from './SourceFreshnessRow';
import { errorMessage, formatDate } from '../../../common/utils/format';
import { VersionReview } from './VersionReview';

// Manage explicit sync actions, bounded active-job polling, and version inspection.
export function KnowledgePanel() {
  const profile = useSelectedProfile();
  const dispatch = useAppDispatch();
  const { discover, selectedVersionId } = useAppSelector(selectUpdates);
  const scope = profile?.id ?? skipToken;
  const { data: sources = [], error: sourceError } = useGetSourcesQuery(scope);
  const { data: versions = [], error: versionError } = useGetVersionsQuery(scope);
  const [pollingInterval, setPollingInterval] = useState(0);
  const {
    data: jobs = [],
    error: jobsError,
    refetch: refreshJobs,
  } = useGetJobsQuery(scope, { pollingInterval, skipPollingIfUnfocused: true });
  const running = jobs.some((job) => ['queued', 'running'].includes(job.status));
  const [sync, { isLoading, error }] = useStartSyncMutation();
  const latest = jobs[0];
  const latestId = latest?.id;
  const latestStatus = latest?.status;
  useEffect(() => {
    setPollingInterval(running ? 2500 : 0);
  }, [running]);
  useEffect(() => {
    if (latestId && latestStatus && !['queued', 'running'].includes(latestStatus))
      dispatch(baseApi.util.invalidateTags(['Versions', 'Sources']));
  }, [dispatch, latestId, latestStatus]);
  const { currentData: selected, error: detailError } = useGetVersionQuery(
    selectedVersionId ?? skipToken,
  );
  const { currentData: previous, error: previousError } = useGetVersionQuery(
    selected?.previous_version_id ?? skipToken,
  );
  const pending = versions.filter((version) => version.status === 'pending').length;
  useEffect(() => {
    if (selected?.id)
      document
        .getElementById('version-review')
        ?.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }, [selected?.id]);

  return (
    <section className="knowledge-panel">
      <header className="panel-header">
        <div>
          <div className="eyebrow">CURATED, NOT CONTINUOUSLY CRAWLED</div>
          <h2>Knowledge updates</h2>
        </div>
        <Button
          disabled={!profile || running || isLoading}
          onClick={() => profile && sync({ profile_id: profile.id, discover })}
        >
          <RefreshCw size={16} className={running ? 'spin' : ''} />{' '}
          {running ? 'Sync in progress' : 'Sync official sources'}
        </Button>
      </header>
      {!profile ? (
        <div className="knowledge-empty">
          <Database size={40} />
          <h3>Choose the scope to sync.</h3>
          <p>Complete the business profile on the left. Both tabs share the same selections.</p>
        </div>
      ) : (
        <>
          <div className="sync-options">
            <label>
              <input
                type="checkbox"
                checked={discover}
                disabled={running}
                onChange={(event) => dispatch(setDiscovery(event.target.checked))}
              />{' '}
              Discover additional official sources
            </label>
            <span className="small muted">
              {discover
                ? 'Uses optional OpenAI web search during this manual sync.'
                : 'Fetch registered URLs only. No search call.'}
            </span>
          </div>
          <div className="stats">
            <div>
              <Globe size={19} />
              <strong>{sources.length}</strong>
              <span>registered sources</span>
            </div>
            <div>
              <Database size={19} />
              <strong>{sources.filter((source) => source.active_version_id).length}</strong>
              <span>active sources</span>
            </div>
            <div>
              <Clock3 size={19} />
              <strong>{pending}</strong>
              <span>awaiting review</span>
            </div>
          </div>
          {(error || sourceError || versionError || jobsError || detailError || previousError) && (
            <Notice error>
              {errorMessage(
                error || sourceError || versionError || jobsError || detailError || previousError,
              )}
            </Notice>
          )}
          {latest && (
            <section className="sync-progress">
              <div className="section-heading">
                <h3>Latest sync</h3>
                <StatusBadge status={latest.status} />
              </div>
              <p className="small muted">
                Requested {formatDate(latest.created_at)} · Attempt {latest.attempts} ·{' '}
                {latest.discover ? 'Discovery + registered sources' : 'Registered sources only'}
              </p>
              {latest.status === 'queued' && (
                <Notice>
                  Waiting for the worker to start. Azure mode starts it on demand; local mode
                  requires your development worker terminal.
                </Notice>
              )}
              {['queued', 'running'].includes(latest.status) && (
                <Button
                  className="button-secondary"
                  disabled={isLoading}
                  onClick={() =>
                    profile && sync({ profile_id: profile.id, discover: latest.discover })
                  }
                >
                  Retry worker launch
                </Button>
              )}
              {latest.error && <Notice error>{latest.error}</Notice>}
              {latest.outcomes.map((outcome, index) => (
                <div className="outcome" key={index}>
                  <StatusBadge status={outcome.status} />
                  <div>
                    <strong>
                      {outcome.url === 'discovery' ? 'Official-source discovery' : outcome.url}
                    </strong>
                    <p>{outcome.summary}</p>
                  </div>
                </div>
              ))}
              <Button className="button-secondary" onClick={() => refreshJobs()}>
                Refresh status
              </Button>
            </section>
          )}
          <section className="source-section">
            <h3>Source freshness</h3>
            {sources.length === 0 ? (
              <p className="muted">
                No sources registered yet. Your first sync will register the pilot sources.
              </p>
            ) : (
              sources.map((source) => (
                <SourceFreshnessRow
                  key={source.id}
                  source={source}
                  onReview={(id) => dispatch(selectVersion(id))}
                />
              ))
            )}
          </section>
          <section>
            <div className="section-heading">
              <h3>Document versions</h3>
              <span className="small muted">{versions.length} captured</span>
            </div>
            {versions.length === 0 && (
              <Notice>
                No captured versions yet. Sync sources, then inspect and approve evidence before
                using chat.
              </Notice>
            )}
            <div className="version-list">
              {versions.map((version) => (
                <button
                  key={version.id}
                  className={`version-row ${selectedVersionId === version.id ? 'selected' : ''}`}
                  onClick={() => dispatch(selectVersion(version.id))}
                >
                  <div>
                    <strong>{version.title}</strong>
                    <p>{version.summary}</p>
                    <span className="small muted">
                      IT / Software development · Detected {formatDate(version.change_detected_at)}
                    </span>
                  </div>
                  <StatusBadge
                    status={
                      sources.some((source) => source.active_version_id === version.id)
                        ? 'active'
                        : version.status
                    }
                  />
                </button>
              ))}
            </div>
          </section>
          {selected && (
            <VersionReview
              key={selected.id}
              version={selected}
              previous={previous}
              isActive={sources.some((source) => source.active_version_id === selected.id)}
            />
          )}
          <p className="footnote">
            Manual sync only. Scheduling is a future enhancement. The pilot source set is not a
            complete activity-specific licensing checklist.
          </p>
        </>
      )}
    </section>
  );
}
