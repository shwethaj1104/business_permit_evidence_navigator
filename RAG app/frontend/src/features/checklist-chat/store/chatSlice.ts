import { createSlice, type PayloadAction } from '@reduxjs/toolkit';

// Retain active conversation references and unsent drafts; RTK Query owns saved messages.
const chatSlice = createSlice({
  name: 'chat',
  initialState: {
    conversationId: null as string | null,
    profileId: null as string | null,
    drafts: {} as Record<string, string>,
  },
  reducers: {
    setConversation(state, action: PayloadAction<{ id: string; profileId: string | null }>) {
      state.conversationId = action.payload.id;
      state.profileId = action.payload.profileId;
    },
    setDraft(state, action: PayloadAction<{ conversationId: string | null; text: string }>) {
      state.drafts[action.payload.conversationId ?? 'new'] = action.payload.text;
    },
    resetConversation(state) {
      state.conversationId = null;
      state.profileId = null;
    },
  },
});
export const { setConversation, resetConversation, setDraft } = chatSlice.actions;
export default chatSlice.reducer;
