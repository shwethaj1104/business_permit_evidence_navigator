import { useEffect, useState } from 'react';

const illustratedSurfaces = new Set<string>();

// Explain the source-to-checklist workflow with a finite, design-specific illustration.
export function EvidenceJourney({
  compact = false,
  showLabels = true,
}: {
  compact?: boolean;
  showLabels?: boolean;
}) {
  const design = 'executive';
  const surface = `${design}:${compact ? 'reader' : 'welcome'}`;
  const [animate] = useState(() => !illustratedSurfaces.has(surface));
  useEffect(() => {
    illustratedSurfaces.add(surface);
  }, [surface]);
  return (
    <figure
      data-animate={animate}
      aria-hidden={showLabels ? undefined : true}
      className={`evidence-journey journey-${design} ${compact ? 'journey-compact' : ''}`}
    >
      <svg viewBox="0 0 320 94" fill="none" aria-hidden="true" focusable="false">
        <>
          <g className="journey-connector">
            <path
              d="M83 55H136M186 55H239"
              stroke="currentColor"
              strokeWidth="1.5"
              strokeDasharray="3 5"
            />
          </g>
          <g className="journey-stage journey-stage-one">
            <rect
              className="journey-back-sheet"
              x="25"
              y="22"
              width="49"
              height="65"
              rx="7"
              transform="rotate(-9 25 22)"
            />
            <rect className="journey-sheet" x="32" y="17" width="49" height="65" rx="7" />
            <path
              d="M44 34h23M44 44h17M44 54h23"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
            />
          </g>
          <g className="journey-stage journey-stage-two">
            <rect className="journey-focus" x="136" y="26" width="49" height="49" rx="15" />
            <path
              d="m148 50 9 9 16-18"
              stroke="currentColor"
              strokeWidth="2.5"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </g>
          <g className="journey-stage journey-stage-three">
            <rect className="journey-sheet" x="239" y="17" width="49" height="65" rx="7" />
            <path
              d="m249 34 3 3 5-6m-8 17 3 3 5-6m-8 17 3 3 5-6M263 34h14M263 48h14M263 62h14"
              stroke="currentColor"
              strokeWidth="1.7"
              strokeLinecap="round"
            />
          </g>
        </>
      </svg>
      {showLabels && (
        <figcaption>
          <span>Official sources</span>
          <span>Human review</span>
          <span>Your checklist</span>
        </figcaption>
      )}
    </figure>
  );
}
