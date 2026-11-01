import { configureStore } from '@reduxjs/toolkit';
import { setupListeners } from '@reduxjs/toolkit/query';
import { rootReducer } from './rootReducer';
import { baseApi } from '../common/api/baseApi';

// Register API middleware once and enable focus/reconnect-aware query behavior.
export const store = configureStore({
  reducer: rootReducer,
  middleware: (getDefault) => getDefault().concat(baseApi.middleware),
});
setupListeners(store.dispatch);
export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
