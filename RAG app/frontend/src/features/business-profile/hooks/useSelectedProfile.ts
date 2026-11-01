import { useGetProfilesQuery } from '../api/profileApi';
import { selectProfileSelection } from '../store/profileSelectors';
import { useAppSelector } from '../../../store/hooks';
import type { ProfileField } from '../../../common/types/api';

// Resolve a supported profile only after all required dropdowns have a matching selection.
export function useSelectedProfile() {
  const { data } = useGetProfilesQuery();
  const selection = useAppSelector(selectProfileSelection);
  return data?.profiles.find((profile) =>
    (Object.keys(selection) as ProfileField[]).every((key) => selection[key] === profile[key]),
  );
}
