import { useRef, useState } from 'react';
import { MoreHorizontal, Pencil, Trash2 } from 'lucide-react';
import type { ConversationSummary } from '../../../common/types/api';
import { Button } from '../../../common/components/Button';

// Keep navigation, accessible actions, and inline title editing separate for each saved chat.
export function SavedChatItem({
  chat,
  selected,
  busy,
  onSelect,
  onRename,
  onDelete,
}: {
  chat: ConversationSummary;
  selected: boolean;
  busy: boolean;
  onSelect: () => void;
  onRename: (title: string) => Promise<void>;
  onDelete: () => Promise<void>;
}) {
  const [editing, setEditing] = useState(false);
  const [title, setTitle] = useState(chat.title);
  const menu = useRef<HTMLDetailsElement>(null);
  return (
    <div className={`saved-chat-row ${selected ? 'selected' : ''}`}>
      {editing ? (
        <form
          className="chat-rename-form"
          onSubmit={async (event) => {
            event.preventDefault();
            try {
              await onRename(title.trim());
              setEditing(false);
            } catch {
              /* Parent displays the safe API error. */
            }
          }}
        >
          <input
            aria-label="Chat title"
            value={title}
            maxLength={80}
            autoFocus
            disabled={busy}
            onChange={(event) => setTitle(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === 'Escape') setEditing(false);
            }}
          />
          <Button type="submit" disabled={busy || !title.trim()}>
            Save
          </Button>
          <button type="button" disabled={busy} onClick={() => setEditing(false)}>
            Cancel
          </button>
        </form>
      ) : (
        <>
          <button
            className="saved-chat"
            title={chat.title}
            aria-current={selected ? 'true' : undefined}
            disabled={busy}
            onClick={onSelect}
          >
            <strong>{chat.title}</strong>
          </button>
          <details className="chat-actions" ref={menu}>
            <summary
              aria-label={`Actions for ${chat.title}`}
              onClick={(event) => {
                if (busy) event.preventDefault();
              }}
            >
              <MoreHorizontal size={18} />
            </summary>
            <div className="chat-actions-menu">
              <button
                disabled={busy}
                onClick={() => {
                  if (menu.current) menu.current.open = false;
                  setTitle(chat.title);
                  setEditing(true);
                }}
              >
                <Pencil size={14} /> Rename
              </button>
              <button
                className="delete-chat"
                disabled={busy}
                onClick={async () => {
                  if (menu.current) menu.current.open = false;
                  if (!window.confirm(`Delete “${chat.title}” and its messages?`)) return;
                  try {
                    await onDelete();
                  } catch {
                    /* Parent displays the safe API error. */
                  }
                }}
              >
                <Trash2 size={14} /> Delete
              </button>
            </div>
          </details>
        </>
      )}
    </div>
  );
}
