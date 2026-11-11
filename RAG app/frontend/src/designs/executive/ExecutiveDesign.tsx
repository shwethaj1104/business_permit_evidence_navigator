import { GlassWelcomeMotion } from './GlassWelcomeMotion';
import { WelcomeIntro } from '../../common/components/WelcomeIntro';
import { BookOpen, MessageSquare } from 'lucide-react';
import type { DesignShellProps, DesignWelcomeProps } from '../types';
import './executive.css';
import './executive-knowledge.css';
import './executive-responsive.css';

// Frame the assistant and document library in a restrained frosted workspace.
export function ExecutiveDesign({ tab, onTabChange, children, notices }: DesignShellProps) {
  return (
    <div
      className={`mint-workspace design-root executive-design ${tab === 'chat' ? 'chat-shell' : 'updates-shell'}`}
    >
      <a className="glass-skip" href="#workspace-main">
        Skip to workspace
      </a>
      <header className="glass-header">
        <div className="glass-brand">
          <img src="/favicon.svg" alt="" width="32" height="32" />
          <div>
            <strong>Permit Navigator</strong>
            <span>Business setup workspace</span>
          </div>
        </div>
        <nav aria-label="Workspace navigation">
          <button
            type="button"
            aria-current={tab === 'chat' ? 'page' : undefined}
            onClick={() => onTabChange('chat')}
          >
            <MessageSquare size={17} />
            Assistant
          </button>
          <button
            type="button"
            aria-current={tab === 'updates' ? 'page' : undefined}
            onClick={() => onTabChange('updates')}
          >
            <BookOpen size={17} />
            Knowledge
          </button>
        </nav>
      </header>
      {notices && <div className="glass-notices">{notices}</div>}
      <main
        key={tab}
        id="workspace-main"
        tabIndex={-1}
        className={`workspace ${tab === 'chat' ? 'workspace-chat' : 'workspace-updates'}`}
      >
        {children}
      </main>
    </div>
  );
}

// Introduce the assistant with one concise prompt and a compact finite illustration.
export function ExecutiveWelcome({ onPrompt }: DesignWelcomeProps) {
  return (
    <WelcomeIntro
      onPrompt={onPrompt}
      visual={<GlassWelcomeMotion />}
      description="Reviewed UAE mainland IT guidance."
    />
  );
}
