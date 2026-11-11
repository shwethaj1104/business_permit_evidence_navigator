import { FileCheck2, Clock3, AlertCircle, Globe, Archive } from 'lucide-react';
import type { Source } from '../../../common/types/api';
import { sourceGroups, sourceGroup, sourceGroupLabels } from '../utils/sourceStatus';

const icons = {
  active: FileCheck2,
  pending: Clock3,
  failed: AlertCircle,
  registered: Globe,
  inactive: Archive,
};

// Present source counts as a view-only skyline; summary cards own the list filters.
export function EvidenceSkyline({ sources, running }: { sources: Source[]; running: boolean }) {
  const counts = sourceGroups.map(
    (group) => sources.filter((source) => sourceGroup(source) === group).length,
  );
  const maximum = Math.max(1, ...counts);
  return (
    <figure
      className={`evidence-skyline ${running ? 'is-syncing' : ''}`}
      aria-label={`Evidence Skyline: ${sourceGroups.map((group, index) => `${sourceGroupLabels[group]} ${counts[index]}`).join(', ')}`}
    >
      <figcaption className="skyline-heading">
        <h3>Evidence Skyline</h3>
        <span>{sources.length} Sources</span>
      </figcaption>
      {running && (
        <p className="skyline-sync" role="status">
          Syncing Sources…
        </p>
      )}
      <div className="skyline-chart" aria-hidden="true">
        <div className="skyline-grid" />
        {sourceGroups.map((group, index) => {
          const Icon = icons[group];
          const count = counts[index];
          return (
            <div className={`skyline-lane skyline-${group}`} key={group}>
              <div
                className="skyline-column-wrap"
                style={{ height: `${count ? (count / maximum) * 100 : 0}px` }}
              >
                <span className="skyline-count">
                  <Icon size={16} />
                  <strong>{count}</strong>
                </span>
                <div className={`skyline-column ${count ? '' : 'is-zero'}`} />
              </div>
              <span className="skyline-label">{sourceGroupLabels[group]}</span>
            </div>
          );
        })}
      </div>
      <div className="skyline-key" aria-hidden="true">
        <span>0</span>
        <span>Column Height = Source Count</span>
      </div>
    </figure>
  );
}
