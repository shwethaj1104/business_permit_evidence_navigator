import { useEffect, useRef, useState } from 'react';
import { useWorkspaceInteractions } from '../common/hooks/useWorkspaceInteractions';
import { useHealthQuery } from '../common/api/baseApi';
import { Notice } from '../common/components/Notice';
import { errorMessage } from '../common/utils/format';
import { ChatPanel } from '../features/checklist-chat/components/ChatPanel';
import { KnowledgePanel } from '../features/knowledge-updates/components/KnowledgePanel';
import { ExecutiveDesign } from '../designs/executive/ExecutiveDesign';
import type { WorkspaceTab } from '../designs/types';

// Render the finalized Glass Workspace with shared chat and knowledge behavior.
export function App() {
  useWorkspaceInteractions();
  // Remove obsolete preview choices from existing bookmarks without disrupting evidence anchors.
  useEffect(() => {
    const url = new URL(window.location.href);
    if (url.searchParams.has('design')) {
      url.searchParams.delete('design');
      window.history.replaceState(window.history.state, '', url);
    }
    try {
      localStorage.removeItem('permit-navigator-design-preview');
    } catch {
      // The finalized workspace also works when browser storage is unavailable.
    }
  }, []);
  const [tab, setTab] = useState<WorkspaceTab>('chat');
  const previousTab = useRef(tab);
  const { data: health, error } = useHealthQuery();
  useEffect(() => {
    document.title = `${tab === 'chat' ? 'Assistant' : 'Knowledge'} · Permit Navigator`;
    if (previousTab.current !== tab)
      document.getElementById('workspace-main')?.focus({ preventScroll: true });
    previousTab.current = tab;
  }, [tab]);
  const notices =
    error || health?.status === 'setup_required' ? (
      <>
        {error && <Notice error>{errorMessage(error)}</Notice>}
        {health?.status === 'setup_required' && (
          <Notice>
            {health.message ?? 'Connection setup is required. Contact the workspace administrator.'}
          </Notice>
        )}
      </>
    ) : undefined;
  return (
    <div className={`design-preview design-preview-${tab}`}>
      <ExecutiveDesign tab={tab} onTabChange={setTab} notices={notices}>
        {tab === 'chat' ? <ChatPanel /> : <KnowledgePanel />}
      </ExecutiveDesign>
    </div>
  );
}
