import { RequestActivity } from '../../../common/components/RequestActivity';
import { MapPin, Layers, CheckCircle2 } from 'lucide-react';
import { useGetProfilesQuery } from '../api/profileApi';
import { useAppDispatch, useAppSelector } from '../../../store/hooks';
import { setField } from '../store/profileSlice';
import { selectProfileSelection } from '../store/profileSelectors';
import { useSelectedProfile } from '../hooks/useSelectedProfile';
import { SelectField } from '../../../common/components/SelectField';
import { Notice } from '../../../common/components/Notice';
import { errorMessage } from '../../../common/utils/format';
import { profileFields as fields } from '../constants/profileFields';

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
  const selectedCount = fields.filter(({ key }) => Boolean(selection[key])).length;
  const nextField = fields.find(({ key }) => !selection[key])?.key;
  return (
    <aside className={`profile-panel ${inline ? 'profile-inline' : ''}`}>
      <div className="eyebrow">
        <MapPin size={15} /> BUSINESS PROFILE
      </div>
      <div className="profile-title-row">
        <h2>{inline ? 'Make it yours.' : 'Your business profile'}</h2>
        <span className={`selection-count ${profile ? 'selection-complete' : ''}`}>
          {profile ? <CheckCircle2 size={13} /> : null}
          {selectedCount}/5
        </span>
      </div>
      <p className="muted">
        {inline
          ? 'Five small details. A more relevant starting point.'
          : 'Choose the business setup you want to keep up to date.'}
      </p>
      <div className="progress-track">
        <div style={{ width: `${(selectedCount / fields.length) * 100}%` }} />
      </div>
      {!profile && (
        <p className="profile-progress-label">{fields.length - selectedCount} selections to go</p>
      )}
      {isLoading && (
        <p role="status">
          <RequestActivity text="Loading business profiles…" />
        </p>
      )}
      {error ? (
        <Notice error>{errorMessage(error)}</Notice>
      ) : (
        fields.map(({ key, label }) => (
          <SelectField
            key={key}
            label={label}
            suggested={key === nextField && !isLoading && !disabled}
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
          <strong>Mainland IT · UAE</strong>

          <p className="small">Verify activity-specific requirements.</p>
        </div>
      </div>
    </aside>
  );
}
