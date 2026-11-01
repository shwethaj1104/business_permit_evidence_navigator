import type { RootState } from '../../../store';

// Read shared selections from the central store.
export const selectProfileSelection = (state: RootState) => state.profile;
