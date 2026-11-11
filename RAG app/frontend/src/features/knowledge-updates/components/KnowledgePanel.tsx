import { useKnowledgeWorkspace } from './useKnowledgeWorkspace';
import { ExecutiveKnowledgeView } from '../../../designs/executive/ExecutiveViews';

// Connect the workspace behavior to the finalized Glass interface.
export function KnowledgePanel() {
  const model = useKnowledgeWorkspace();
  return <ExecutiveKnowledgeView model={model} />;
}
