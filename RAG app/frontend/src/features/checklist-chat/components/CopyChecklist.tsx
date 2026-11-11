import { useState } from 'react';
import { Check, Copy } from 'lucide-react';
import type { Answer } from '../../../common/types/api';

// Copy the generated checklist together with its caveats and traceable source links.
export function CopyChecklist({ answer }: { answer: Answer }) {
  const [state, setState] = useState<'idle' | 'copying' | 'copied' | 'error'>('idle');
  async function copy() {
    setState('copying');
    const text = [
      answer.message,
      ...answer.items.map(
        (item, index) =>
          `${index + 1}. ${item.title}\n${item.detail}${item.condition ? `\nApplies when: ${item.condition}` : ''}`,
      ),
      ...(answer.gaps.length ? ['Still to confirm', ...answer.gaps] : []),
      ...(answer.citations.length
        ? [
            'Sources',
            ...answer.citations.map(
              (citation) => `${citation.title}: ${citation.url} (version ${citation.version_id})`,
            ),
          ]
        : []),
    ].join('\n\n');
    try {
      await navigator.clipboard.writeText(text);
      setState('copied');
    } catch {
      setState('error');
    }
  }
  return (
    <div className="checklist-tools">
      <button type="button" onClick={() => void copy()} disabled={state === 'copying'}>
        {state === 'copied' ? (
          <Check size={15} aria-hidden="true" />
        ) : (
          <Copy size={15} aria-hidden="true" />
        )}
        {state === 'copied'
          ? 'Copied with sources'
          : state === 'copying'
            ? 'Copying…'
            : 'Copy checklist'}
      </button>
      <span className="checklist-copy-feedback" role="status">
        {state === 'copied' ? 'Checklist and source links copied.' : ''}
      </span>
      {state === 'error' && (
        <p role="alert">
          Clipboard access is unavailable. Select the checklist text to copy it manually.
        </p>
      )}
    </div>
  );
}
