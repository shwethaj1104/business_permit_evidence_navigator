import { baseApi } from '../../../common/api/baseApi';
import type { Profile } from '../../../common/types/api';

// Load the same server-defined profile options for chat and sync.
export const profileApi = baseApi.injectEndpoints({
  endpoints: (builder) => ({
    getProfiles: builder.query<{ profiles: Profile[] }, void>({ query: () => '/profiles' }),
  }),
});
export const { useGetProfilesQuery } = profileApi;
