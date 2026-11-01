import { MapPin, Layers } from 'lucide-react';
import { useGetProfilesQuery } from '../api/profileApi';
import { useAppDispatch, useAppSelector } from '../../../store/hooks';
import { setField } from '../store/profileSlice';
import { selectProfileSelection } from '../store/profileSelectors';
import { useSelectedProfile } from '../hooks/useSelectedProfile';
import { SelectField } from '../../../common/components/SelectField';
import { Notice } from '../../../common/components/Notice';
import { errorMessage } from '../../../common/utils/format';
import type { ProfileField } from '../../../common/types/api';

const fields: { key: ProfileField; label: string }[] = [
  { key: 'emirate', label: 'Emirate' },
  { key: 'jurisdiction', label: 'Jurisdiction' },
  { key: 'activity', label: 'Business activity' },
  { key: 'application_type', label: 'Application type' },
  { key: 'legal_structure', label: 'Legal structure' },
];

// Reuse the same scope selector in both tabs and gate actions until complete.
export function ProfileSelectors({
  inline = false,
  disabled = false,
}: {
  inline?: boolean;
  disabled?: boolean;
}) {
  const { data, error, isLoading } = useGetProfilesQuery();
  const selection = useAppSelector(selectProfileSelection);
  const dispatch = useAppDispatch();
  const profile = useSelectedProfile();
  const selectedCount = Object.values(selection).filter(Boolean).length;
  return (
    <aside className={`profile-panel ${inline ? 'profile-inline' : ''}`}>
      <div className="eyebrow">
        <MapPin size={15} /> BUSINESS PROFILE
      </div>
      <h2>Start with your business.</h2>
      <p className="muted">
        Set the context once. Your checklist and source updates use the same profile.
      </p>
      <div className="progress-track">
        <div style={{ width: `${(selectedCount / fields.length) * 100}%` }} />
      </div>
      <p className="small muted">
        {selectedCount} of {fields.length} selected
      </p>
      {error ? (
        <Notice error>{errorMessage(error)}</Notice>
      ) : (
        fields.map(({ key, label }) => (
          <SelectField
            key={key}
            label={label}
            value={selection[key]}
            options={[...new Set(data?.profiles.map((row) => row[key]) ?? [])]}
            disabled={isLoading || disabled}
            onChange={(value) => dispatch(setField({ field: key, value }))}
          />
        ))
      )}
      <div className="scope-note">
        <Layers size={20} />
        <div>
          <strong>One focused pilot</strong>
          <p>Dubai mainland · IT</p>
          <p className="small">
            {profile?.coverage_note ??
              'More activities can be added later. Complete all selections to continue.'}
          </p>
        </div>
      </div>
    </aside>
  );
}
