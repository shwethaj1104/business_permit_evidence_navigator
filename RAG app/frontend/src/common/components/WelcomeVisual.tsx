import { MapPin, Sparkles, Check, MessageCircle } from 'lucide-react';
import { PermitSculpture } from './PermitSculpture';

const emirates = ['DXB', 'AUH', 'SHJ', 'AJM', 'UAQ', 'RAK', 'FUJ'];

// Match each introduction slide to its own lightweight dimensional illustration.
export function WelcomeVisual({ step }: { step: number }) {
  if (step === 2) return <PermitSculpture step={2} />;
  return (
    <div className={`welcome-visual visual-${step}`} aria-hidden="true">
      <div className="visual-floor" />
      {step === 0 ? (
        <div className="conversation-sculpture">
          <div className="floating-bubble bubble-user">
            <MessageCircle size={23} />
            <span className="bubble-stroke" />
          </div>
          <div className="floating-bubble bubble-assistant">
            <Sparkles size={24} />
            <span className="bubble-stroke" />
            <span className="bubble-stroke short" />
            <span className="visual-typing">
              <i />
              <i />
              <i />
            </span>
          </div>
          <span className="bubble-check">
            <Check size={22} />
          </span>
        </div>
      ) : (
        <div className="emirate-sculpture">
          <div className="emirate-ring" />
          <div className="emirate-hub">
            <MapPin size={32} />
            <span>UAE</span>
          </div>
          {emirates.map((emirate, index) => {
            const angle = (index * Math.PI * 2) / emirates.length - Math.PI / 2;
            return (
              <span
                className="emirate-tile"
                key={emirate}
                style={{
                  left: `${50 + Math.cos(angle) * 39}%`,
                  top: `${50 + Math.sin(angle) * 37}%`,
                  animationDelay: `${index * -0.5}s`,
                }}
              >
                {emirate}
              </span>
            );
          })}
        </div>
      )}
    </div>
  );
}
