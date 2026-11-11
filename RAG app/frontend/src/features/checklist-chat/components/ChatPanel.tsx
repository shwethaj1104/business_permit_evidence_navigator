import { useChatWorkspace } from './useChatWorkspace';
import { ExecutiveChatView } from '../../../designs/executive/ExecutiveViews';

// Connect the workspace behavior to the finalized Glass interface.
export function ChatPanel() {
  const model = useChatWorkspace();
  return <ExecutiveChatView model={model} />;
}
