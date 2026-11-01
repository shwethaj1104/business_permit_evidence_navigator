import { createSlice, type PayloadAction } from '@reduxjs/toolkit';

// Store only the active conversation reference; RTK Query owns its messages.
const chatSlice = createSlice({
  name: 'chat',
  initialState: { conversationId: null as string | null, profileId: null as string | null },
  reducers: {
    setConversation(state, action: PayloadAction<{ id: string; profileId: string | null }>) {
      state.conversationId = action.payload.id;
      state.profileId = action.payload.profileId;
    },
    resetConversation(state) {
      state.conversationId = null;
      state.profileId = null;
    },
  },
});
export const { setConversation, resetConversation } = chatSlice.actions;
export default chatSlice.reducer;
