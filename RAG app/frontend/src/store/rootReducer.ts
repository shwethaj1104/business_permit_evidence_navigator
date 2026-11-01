import { combineReducers } from '@reduxjs/toolkit';
import { baseApi } from '../common/api/baseApi';
import profile from '../features/business-profile/store/profileSlice';
import chat from '../features/checklist-chat/store/chatSlice';
import updates from '../features/knowledge-updates/store/updatesSlice';

// Assemble feature state and the shared RTK Query cache in one root reducer.
export const rootReducer = combineReducers({
  profile,
  chat,
  updates,
  [baseApi.reducerPath]: baseApi.reducer,
});
