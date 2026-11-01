import type { ConversationSummary } from '../../../common/types/api';
import { MessageSquare } from 'lucide-react';
import {
  useGetConversationsInfiniteQuery,
  useRenameConversationMutation,
  useDeleteConversationMutation,
} from '../api/chatApi';
import { Button } from '../../../common/components/Button';
import { Notice } from '../../../common/components/Notice';
import { errorMessage } from '../../../common/utils/format';

import { SavedChatItem } from './SavedChatItem';

// List all saved conversations through cursor pagination in the left sidebar.
export function ChatHistory({
  onDeleted,
  selectedId,
  busy,
  onSelect,
}: {
  onDeleted: (id: string) => void;
  selectedId: string | null;
  busy: boolean;
  onSelect: (chat: ConversationSummary) => void;
}) {
  const { data, error, isLoading, isFetchingNextPage, fetchNextPage, hasNextPage } =
    useGetConversationsInfiniteQuery('all');
  const [rename, { isLoading: renaming, error: renameError }] = useRenameConversationMutation();
  const [remove, { isLoading: deleting, error: deleteError }] = useDeleteConversationMutation();
  const actionsBusy = busy || renaming || deleting;
  const chats = [
    ...new Map(
      (data?.pages.flatMap((page) => page.conversations) ?? []).map((chat) => [chat.id, chat]),
    ).values(),
  ];
  return (
    <aside className="saved-chats" aria-label="Saved chats">
      <h3>
        <MessageSquare size={15} /> Saved chats
      </h3>
      {isLoading && <p className="small muted">Loading saved chats…</p>}
      {(error || renameError || deleteError) && (
        <Notice error>{errorMessage(error || renameError || deleteError)}</Notice>
      )}
      {!isLoading && !error && chats.length === 0 && (
        <p className="small muted">Your conversations will appear here after the first message.</p>
      )}
      {chats.map((chat) => (
        <SavedChatItem
          key={chat.id}
          chat={chat}
          selected={chat.id === selectedId}
          busy={actionsBusy}
          onSelect={() => onSelect(chat)}
          onRename={async (title) => {
            await rename({ id: chat.id, title }).unwrap();
          }}
          onDelete={async () => {
            await remove(chat.id).unwrap();
            onDeleted(chat.id);
          }}
        />
      ))}
      {hasNextPage && (
        <Button
          className="button-secondary"
          disabled={busy || isFetchingNextPage}
          onClick={() => fetchNextPage()}
        >
          {isFetchingNextPage ? 'Loading…' : 'Load more chats'}
        </Button>
      )}
    </aside>
  );
}
