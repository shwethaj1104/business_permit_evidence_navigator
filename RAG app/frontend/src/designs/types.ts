import type { ReactNode } from 'react';

export type WorkspaceTab = 'chat' | 'updates';
export interface DesignShellProps {
  tab: WorkspaceTab;
  onTabChange: (tab: WorkspaceTab) => void;
  children: ReactNode;
  notices?: ReactNode;
}
export interface DesignWelcomeProps {
  onPrompt: (message: string) => void;
}
