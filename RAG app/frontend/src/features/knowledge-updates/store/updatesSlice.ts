import { createSlice, type PayloadAction } from '@reduxjs/toolkit';

// Keep local comparison selection and discovery preference outside server caches.
const updatesSlice = createSlice({
  name: 'updates',
  initialState: { selectedVersionId: null as string | null, discover: false },
  reducers: {
    selectVersion(state, action: PayloadAction<string | null>) {
      state.selectedVersionId = action.payload;
    },
    setDiscovery(state, action: PayloadAction<boolean>) {
      state.discover = action.payload;
    },
  },
});
export const { selectVersion, setDiscovery } = updatesSlice.actions;
export default updatesSlice.reducer;
