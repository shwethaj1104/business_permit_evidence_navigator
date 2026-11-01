import { createSlice, type PayloadAction } from '@reduxjs/toolkit';
import type { ProfileField } from '../../../common/types/api';

type Selection = Record<ProfileField, string>;
const initialState: Selection = {
  emirate: '',
  jurisdiction: '',
  activity: '',
  application_type: '',
  legal_structure: '',
};

// Keep one shared client-side selection without copying fetched profile records.
const profileSlice = createSlice({
  name: 'profile',
  initialState,
  reducers: {
    resetProfile() {
      return initialState;
    },
    setProfile(_state, action: PayloadAction<Selection>) {
      return action.payload;
    },
    setField(state, action: PayloadAction<{ field: ProfileField; value: string }>) {
      state[action.payload.field] = action.payload.value;
    },
  },
});
export const { setField, resetProfile, setProfile } = profileSlice.actions;
export default profileSlice.reducer;
