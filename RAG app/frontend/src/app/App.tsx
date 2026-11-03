import { useState } from 'react';
import { BookOpenCheck, MessagesSquare, Database } from 'lucide-react';
import { useHealthQuery } from '../common/api/baseApi';
import { Notice } from '../common/components/Notice';
import { errorMessage } from '../common/utils/format';
import { ProfileSelectors } from '../features/business-profile/components/ProfileSelectors';
import { ChatPanel } from '../features/checklist-chat/components/ChatPanel';
import { KnowledgePanel } from '../features/knowledge-updates/components/KnowledgePanel';

// Compose the local workspace without authentication or background source syncing.
export function App() {
  const [tab, setTab] = useState<'chat' | 'updates'>('chat');
  const { data: health, error } = useHealthQuery();
  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="brand">
          <span className="brand-icon">
            <BookOpenCheck size={23} />
          </span>
          <div>
            <strong>Permit Navigator DEPLOYED CI/CD</strong>
            <span>UAE BUSINESS SETUP ASSISTANT</span>
          </div>
        </div>
      </header>
      <nav className="tabs" aria-label="Workspace tabs">
        <button
          className={tab === 'chat' ? 'active' : ''}
          aria-current={tab === 'chat' ? 'page' : undefined}
          onClick={() => setTab('chat')}
        >
          <MessagesSquare size={17} /> Checklist assistant
        </button>
        <button
          className={tab === 'updates' ? 'active' : ''}
          aria-current={tab === 'updates' ? 'page' : undefined}
          onClick={() => setTab('updates')}
        >
          <Database size={17} /> Knowledge updates
        </button>
      </nav>
      {error && <Notice error>{errorMessage(error)}</Notice>}
      {health?.status === 'setup_required' && (
        <Notice>
          <strong>Finish connection setup.</strong>{' '}
          {health.message ?? 'Add OPENAI_API_KEY to the root .env.'} Restart the backend after
          editing credentials. The profile controls and UI are available now.
        </Notice>
      )}
      <main className={`workspace ${tab === 'chat' ? 'workspace-chat' : ''}`}>
        {tab === 'chat' ? (
          <ChatPanel />
        ) : (
          <>
            <ProfileSelectors />
            <KnowledgePanel />
          </>
        )}
      </main>
      <footer>
        Built around official evidence <span>React · FastAPI · MongoDB Atlas · OpenAI</span>
      </footer>
    </div>
  );
}
