import {
  createApi,
  fetchBaseQuery,
  type BaseQueryFn,
  type FetchArgs,
  type FetchBaseQueryError,
} from '@reduxjs/toolkit/query/react';
import type { Health } from '../types/api';

const rawBaseQuery = fetchBaseQuery({
  baseUrl: import.meta.env.VITE_API_BASE_URL || '/api/v1',
  timeout: 90000,
});

// Report every failed API operation without printing bodies, query values, or credentials.
const loggedBaseQuery: BaseQueryFn<string | FetchArgs, unknown, FetchBaseQueryError> = async (
  args,
  api,
  extraOptions,
) => {
  const started = performance.now();
  const result = await rawBaseQuery(args, api, extraOptions);
  if (result.error) {
    console.error('[Permit API failed]', {
      endpoint: api.endpoint,
      method: typeof args === 'string' ? 'GET' : (args.method ?? 'GET'),
      status: result.error.status,
      requestId: result.meta?.response?.headers.get('x-request-id') ?? 'unavailable',
      durationMs: Math.round(performance.now() - started),
    });
  }
  return result;
};

// Share one server-state cache and middleware across feature endpoint modules.
export const baseApi = createApi({
  reducerPath: 'api',
  baseQuery: loggedBaseQuery,
  tagTypes: ['Health', 'Sources', 'Versions', 'Jobs', 'Conversation', 'ConversationList'],
  endpoints: (builder) => ({
    health: builder.query<Health, void>({ query: () => '/health', providesTags: ['Health'] }),
  }),
});
export const { useHealthQuery } = baseApi;
