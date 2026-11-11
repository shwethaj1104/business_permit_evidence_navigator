import type { ProfileField } from '../../../common/types/api';

// Keep the supported profile fields consistent in both workspace tabs.
export const profileFields: { key: ProfileField; label: string; question: string }[] = [
  { key: 'emirate', label: 'Emirate', question: 'Where will your business be based?' },
  {
    key: 'jurisdiction',
    label: 'Jurisdiction',
    question: 'Which jurisdiction are you setting up in?',
  },
  { key: 'activity', label: 'Business Activity', question: 'What will your business do?' },
  {
    key: 'application_type',
    label: 'Application Type',
    question: 'What type of application do you need?',
  },
  {
    key: 'legal_structure',
    label: 'Legal Structure',
    question: 'Which legal structure are you considering?',
  },
];
