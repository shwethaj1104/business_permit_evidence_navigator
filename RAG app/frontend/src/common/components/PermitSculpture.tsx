import { Check, Sparkles, ShieldCheck, Globe, MessagesSquare } from 'lucide-react';

// Render a CSS 3D permit stack with depth, orbiting evidence, and a reduced-motion fallback.
export function PermitSculpture({ step = 0 }: { step?: number }) {
  const Icon = [Sparkles, Globe, ShieldCheck][step];
  const captions = ['Official evidence', 'Seven emirates', 'Reviewed sources'];
  return (
    <div className={`permit-sculpture sculpture-step-${step}`} aria-hidden="true">
      <div className="sculpture-halo" />
      <div className="permit-stack">
        <div className="permit-layer layer-back" />
        <div className="permit-layer layer-middle" />
        <div className="permit-layer layer-front">
          <span className="permit-emblem">
            <Icon size={28} />
          </span>
          <span className="permit-line long" />
          <span className="permit-line" />
          <span className="permit-line short" />
          <span className="permit-approved">
            <Check size={22} />
          </span>
        </div>
      </div>
      <span className="orbit-chip chip-one">
        <ShieldCheck size={18} /> {captions[step]}
      </span>
      <span className="orbit-chip chip-two">
        <MessagesSquare size={16} />{' '}
        {
          ['Start with a conversation', 'Choose your business profile', 'Trace every next step'][
            step
          ]
        }
      </span>
      <div className="sculpture-shadow" />
    </div>
  );
}
