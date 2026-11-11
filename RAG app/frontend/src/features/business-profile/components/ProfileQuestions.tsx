import { useId } from 'react';
import { ArrowUpRight, Check } from 'lucide-react';
import { useGetProfilesQuery } from '../api/profileApi';
import { profileFields } from '../constants/profileFields';
import { useSelectedProfile } from '../hooks/useSelectedProfile';
import { selectProfileSelection } from '../store/profileSelectors';
import { setField } from '../store/profileSlice';
import { useAppDispatch, useAppSelector } from '../../../store/hooks';
import { Button } from '../../../common/components/Button';
import { Notice } from '../../../common/components/Notice';
import { errorMessage } from '../../../common/utils/format';
import type { Profile } from '../../../common/types/api';

// Collect all five answers as single-choice groups within one assistant message.
export function ProfileQuestions({
  disabled,
  onConfirm,
}: {
  disabled: boolean;
  onConfirm: (profile: Profile) => void;
}) {
  const id = useId();
  const { data, error, isLoading } = useGetProfilesQuery();
  const selection = useAppSelector(selectProfileSelection);
  const profile = useSelectedProfile();
  const dispatch = useAppDispatch();
  const count = profileFields.filter(({ key }) => selection[key]).length;
  return (
    <form
      className="profile-questions"
      onSubmit={(event) => {
        event.preventDefault();
        if (profile && !disabled) onConfirm(profile);
      }}
    >
      {error && <Notice error>{errorMessage(error)}</Notice>}
      {profileFields.map(({ key, label, question }, index) => (
        <fieldset key={key} disabled={disabled || isLoading}>
          <legend>
            <span className="question-number">0{index + 1}</span>
            {question}
          </legend>
          <span className="question-category">{label}</span>
          <div className="question-options">
            {[...new Set(data?.profiles.map((row) => row[key]) ?? [])].map((value) => (
              <label
                className={`radio-option ${selection[key] === value ? 'chosen' : ''}`}
                key={value}
              >
                <input
                  type="radio"
                  name={`${id}-${key}`}
                  value={value}
                  checked={selection[key] === value}
                  onChange={() => dispatch(setField({ field: key, value }))}
                />
                <span>{value}</span>
                <Check className="radio-check" size={13} aria-hidden="true" />
              </label>
            ))}
          </div>
        </fieldset>
      ))}
      <div className="question-actions">
        <span aria-live="polite">{count}/5 answered</span>
        <Button type="submit" disabled={!profile || disabled}>
          Prepare my checklist <ArrowUpRight size={16} />
        </Button>
      </div>
    </form>
  );
}
