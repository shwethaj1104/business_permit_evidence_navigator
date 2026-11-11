import type { Source } from '../../../common/types/api';

export const sourceGroups = ['active', 'pending', 'failed', 'registered', 'inactive'] as const;
export type SourceGroup = (typeof sourceGroups)[number];
export const sourceGroupLabels: Record<SourceGroup, string> = {
  active: 'Active',
  pending: 'Review',
  failed: 'Failed',
  registered: 'Registered',
  inactive: 'Inactive',
};

// Give each source one current state, retaining separate access to its previously active evidence.
export function sourceGroup(source: Source): SourceGroup {
  if (source.last_capture_status === 'failed') return 'failed';
  if (source.latest_version_status === 'pending') return 'pending';
  if (source.active_version_id) return 'active';
  return source.latest_version_id ? 'inactive' : 'registered';
}
