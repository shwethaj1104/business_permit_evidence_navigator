import type { ReactNode } from 'react';
import { safeSourceUrl } from '../utils/format';

// Prevent unsafe URL schemes and isolate external source browsing from chat.
export function SourceLink({ url, children }: { url: string; children: ReactNode }) {
  const href = safeSourceUrl(url);
  return href ? (
    <a href={href} target="_blank" rel="noopener noreferrer">
      {children} ↗
    </a>
  ) : (
    <span>{children}</span>
  );
}
