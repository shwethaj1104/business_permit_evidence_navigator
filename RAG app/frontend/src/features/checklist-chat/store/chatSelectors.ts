import type { RootState } from '../../../store';

// Select only client-side conversation navigation state.
export const selectChat = (state: RootState) => state.chat;
