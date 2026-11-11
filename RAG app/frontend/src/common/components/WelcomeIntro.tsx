import type { ReactNode } from 'react';
import { ArrowRight } from 'lucide-react';
import { EvidenceJourney } from './EvidenceJourney';
import './WelcomeIntro.css';

// Give every new conversation one clear starting point without extra cards or instructions.
export function WelcomeIntro({ onPrompt, visual, description = 'Reviewed guidance for UAE mainland IT.' }: { onPrompt: (message: string) => void; visual?: ReactNode; description?: string }) {
  return (
    <section className="welcome-intro" aria-label="Start a conversation">
      {visual ?? <EvidenceJourney compact showLabels={false} />}
      <h1>Start with clarity.</h1>
      <p>{description}</p>
      <button
        type="button"
        onClick={() => onPrompt('Help me prepare a UAE mainland software company checklist')}
      >
        Create my checklist <ArrowRight size={16} aria-hidden="true" />
      </button>
    </section>
  );
}
