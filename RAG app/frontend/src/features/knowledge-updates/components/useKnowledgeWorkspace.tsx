import { useEffect, useRef, useState } from 'react';
import { skipToken } from '@reduxjs/toolkit/query';
import {
  useGetSourcesQuery,
  useGetVersionsQuery,
  useGetVersionQuery,
  useGetJobsQuery,
  useStartSyncMutation,
  useReviewVersionMutation,
} from '../api/updatesApi';
import { selectVersion, setDiscovery } from '../store/updatesSlice';
import { selectUpdates } from '../store/updatesSelectors';
import { useSelectedProfile } from '../../business-profile/hooks/useSelectedProfile';
import { ProfileSelectors } from '../../business-profile/components/ProfileSelectors';
import { useAppDispatch, useAppSelector } from '../../../store/hooks';
import { baseApi } from '../../../common/api/baseApi';
import { errorMessage } from '../../../common/utils/format';

// Keep source capture, polling and approval behavior independent from visual layouts.
export function useKnowledgeWorkspace() {
  const profile = useSelectedProfile();
  const dispatch = useAppDispatch();
  const { discover, selectedVersionId } = useAppSelector(selectUpdates);
  const previousProfile = useRef(profile?.id);
  useEffect(() => {
    if (previousProfile.current !== profile?.id) dispatch(selectVersion(null));
    previousProfile.current = profile?.id;
  }, [dispatch, profile?.id]);
  const scope = profile?.id ?? skipToken;
  const {
    currentData: sources = [],
    error: sourceError,
    isFetching: sourcesLoading,
    refetch: refreshSources,
  } = useGetSourcesQuery(scope);
  const {
    currentData: versions = [],
    error: versionError,
    isFetching: versionsLoading,
    refetch: refreshVersions,
  } = useGetVersionsQuery(scope);
  const [pollingInterval, setPollingInterval] = useState(0);
  const {
    currentData: jobs = [],
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
  const {
    currentData: selected,
    error: detailError,
    isFetching: detailLoading,
  } = useGetVersionQuery(selectedVersionId ?? skipToken);
  const {
    currentData: previous,
    error: previousError,
    isFetching: previousLoading,
  } = useGetVersionQuery(selected?.previous_version_id ?? skipToken);

  const [review, { isLoading: reviewLoading, error: reviewError }] = useReviewVersionMutation();
  return {
    profile,
    sources,
    versions,
    jobs,
    latest,
    running,
    isLoading,
    discover,
    sourcesLoading,
    sourceFailed: Boolean(sourceError),
    // Reload saved evidence without triggering a paid capture or discovery job.
    retrySources: () => {
      if (profile) {
        void refreshSources();
        void refreshVersions();
      }
    },
    detailLoading,
    previousLoading,
    versionsLoading,
    profileControls: <ProfileSelectors disabled={running || isLoading} />,
    selected: selected?.profile_id === profile?.id ? selected : undefined,
    previous: previous?.profile_id === profile?.id ? previous : undefined,
    selectedVersionId,
    isActive: sources.some((source) => source.active_version_id === selected?.id),
    setDiscover: (value: boolean) => dispatch(setDiscovery(value)),
    selectVersion: (id: string | null) => dispatch(selectVersion(id)),
    sync: () => {
      if (profile && !running && !isLoading) void sync({ profile_id: profile.id, discover });
    },
    retry: () => {
      if (profile && !isLoading)
        void sync({ profile_id: profile.id, discover: latest?.discover ?? discover });
    },
    refresh: () => {
      if (profile) void refreshJobs();
    },
    review: (action: 'approve' | 'reject') => {
      if (selected && profile && selected.profile_id === profile.id)
        void review({ id: selected.id, action });
    },
    reviewLoading,
    error:
      error ||
      sourceError ||
      versionError ||
      jobsError ||
      detailError ||
      previousError ||
      reviewError
        ? errorMessage(
            error ||
              sourceError ||
              versionError ||
              jobsError ||
              detailError ||
              previousError ||
              reviewError,
          )
        : null,
  };
}
export type KnowledgeWorkspaceModel = ReturnType<typeof useKnowledgeWorkspace>;
