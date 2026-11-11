import { ExecutiveWelcome } from '../../designs/executive/ExecutiveDesign';
import type { DesignWelcomeProps } from '../../designs/types';

// Introduce the business setup assistant in the finalized Glass Workspace.
export function AssistantWelcome(props: DesignWelcomeProps) {
  return <ExecutiveWelcome {...props} />;
}
