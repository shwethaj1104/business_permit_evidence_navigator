import { useDispatch, useSelector } from 'react-redux';
import type { AppDispatch, RootState } from './index';

// Give components typed access to dispatch and selectors.
export const useAppDispatch = useDispatch.withTypes<AppDispatch>();
export const useAppSelector = useSelector.withTypes<RootState>();
