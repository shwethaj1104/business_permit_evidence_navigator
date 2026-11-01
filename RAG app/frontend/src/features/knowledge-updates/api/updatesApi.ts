import { baseApi } from '../../../common/api/baseApi';
import type { Source, SyncJob, Version, VersionSummary } from '../../../common/types/api';

// Keep source sync, polling, and review HTTP definitions in one feature API module.
export const updatesApi = baseApi.injectEndpoints({
  endpoints: (builder) => ({
    getSources: builder.query<Source[], string>({
      query: (profile_id) => ({ url: '/knowledge/sources', params: { profile_id } }),
      providesTags: ['Sources'],
    }),
    getVersions: builder.query<VersionSummary[], string>({
      query: (profile_id) => ({ url: '/knowledge/versions', params: { profile_id } }),
      providesTags: ['Versions'],
    }),
    getVersion: builder.query<Version, string>({
      query: (id) => `/knowledge/versions/${id}`,
      providesTags: ['Versions'],
    }),
    getJobs: builder.query<SyncJob[], string>({
      query: (profile_id) => ({ url: '/knowledge/jobs', params: { profile_id } }),
      providesTags: ['Jobs'],
    }),
    startSync: builder.mutation<SyncJob, { profile_id: string; discover: boolean }>({
      query: (body) => ({ url: '/knowledge/sync', method: 'POST', body }),
      invalidatesTags: ['Jobs', 'Sources'],
    }),
    reviewVersion: builder.mutation<Version, { id: string; action: 'approve' | 'reject' }>({
      query: ({ id, action }) => ({
        url: `/knowledge/versions/${id}/review`,
        method: 'POST',
        body: { action },
      }),
      invalidatesTags: ['Versions', 'Sources'],
    }),
  }),
});
export const {
  useGetSourcesQuery,
  useGetVersionsQuery,
  useGetVersionQuery,
  useGetJobsQuery,
  useStartSyncMutation,
  useReviewVersionMutation,
} = updatesApi;
