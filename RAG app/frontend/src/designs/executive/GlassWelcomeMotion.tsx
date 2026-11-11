import { useEffect, useRef, useState } from 'react';

// Explain the evidence journey with gentle motion that stops when hidden.
export function GlassWelcomeMotion({ scene = 'welcome' }: { scene?: 'welcome' | 'knowledge' }) {
  const root = useRef<HTMLDivElement>(null);
  const [visible, setVisible] = useState(true);
  const [tabVisible, setTabVisible] = useState(() => !document.hidden);
  useEffect(() => {
    const observer = new IntersectionObserver(([entry]) => setVisible(entry.isIntersecting));
    if (root.current) observer.observe(root.current);
    const update = () => setTabVisible(!document.hidden);
    document.addEventListener('visibilitychange', update);
    return () => {
      observer.disconnect();
      document.removeEventListener('visibilitychange', update);
    };
  }, []);
  return (
    <div
      ref={root}
      className={`glass-welcome-motion motion-${scene} ${!visible || !tabVisible ? 'motion-is-paused' : ''}`}
    >
      <div className="glass-motion-art" aria-hidden="true">
        <div className="glass-motion-halo" />
        <svg viewBox="0 0 300 150" fill="none" focusable="false">
          <path
            d="M64 92C106 92 100 58 150 58s44 34 87 34"
            stroke="currentColor"
            strokeOpacity=".25"
            strokeDasharray="3 6"
          />
          <g className="motion-source">
            <rect
              x="30"
              y="42"
              width="51"
              height="69"
              rx="10"
              fill="var(--surface)"
              stroke="currentColor"
              strokeOpacity=".35"
            />
            <path
              d="M42 61h27M42 71h20M42 81h27M42 91h15"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
            />
          </g>
          <g className="motion-review">
            <rect
              x="119"
              y="25"
              width="63"
              height="66"
              rx="20"
              fill="var(--accent-soft)"
              stroke="currentColor"
              strokeOpacity=".35"
            />
            <path
              d="m136 56 11 11 19-22"
              stroke="currentColor"
              strokeWidth="3"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
            <circle cx="172" cy="34" r="4" fill="currentColor" />
          </g>
          <g className="motion-guidance">
            <rect
              x="218"
              y="42"
              width="51"
              height="69"
              rx="10"
              fill="var(--surface)"
              stroke="currentColor"
              strokeOpacity=".35"
            />
            <path
              d="m228 60 3 3 5-6m-8 18 3 3 5-6m-8 18 3 3 5-6M242 61h15M242 76h15M242 91h10"
              stroke="currentColor"
              strokeWidth="1.8"
              strokeLinecap="round"
            />
          </g>
        </svg>
      </div>
    </div>
  );
}
