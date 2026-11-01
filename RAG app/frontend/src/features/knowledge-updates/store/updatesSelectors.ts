import type { RootState } from '../../../store';

// Read local sync-panel preferences without duplicating server job records.
export const selectUpdates = (state: RootState) => state.updates;
