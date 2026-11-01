import { baseApi } from '../../../common/api/baseApi';
import type { Conversation, ConversationPage } from '../../../common/types/api';

// Merge cursor pages and new turns without losing already loaded older messages.
function mergeConversation(existing: Conversation, incoming: Conversation): Conversation {
  const messages = [
    ...new Map(
      [...existing.messages, ...incoming.messages].map((message) => [message.id, message]),
    ).values(),
  ].sort((a, b) => a.order - b.order);
  const older =
    incoming.oldest_order !== null &&
    (existing.oldest_order === null || incoming.oldest_order < existing.oldest_order);
  return {
    ...incoming,
    messages,
    has_older: older ? incoming.has_older : existing.has_older,
    oldest_order: messages[0]?.order ?? null,
  };
}

// Keep history, message pagination, and send requests separate from presentation state.
export const chatApi = baseApi.injectEndpoints({
  endpoints: (builder) => ({
    getConversations: builder.infiniteQuery<ConversationPage, string, string | null>({
      infiniteQueryOptions: {
        initialPageParam: null,
        getNextPageParam: (lastPage) => lastPage.next_cursor ?? undefined,
      },
      query: ({ queryArg, pageParam }) => ({
        url: '/chat/conversations',
        params: {
          ...(queryArg === 'all' ? {} : { profile_id: queryArg }),
          ...(pageParam ? { before: pageParam } : {}),
        },
      }),
      providesTags: ['ConversationList'],
    }),
    getConversation: builder.query<Conversation, { id: string; before?: number }>({
      query: ({ id, before }) => ({
        url: `/chat/conversations/${id}`,
        params: before === undefined ? {} : { before },
      }),
      serializeQueryArgs: ({ endpointName, queryArgs }) => `${endpointName}:${queryArgs.id}`,
      merge: (cached, incoming) => mergeConversation(cached, incoming),
      forceRefetch: ({ currentArg, previousArg }) => currentArg?.before !== previousArg?.before,
      providesTags: ['Conversation'],
    }),
    renameConversation: builder.mutation<void, { id: string; title: string }>({
      query: ({ id, title }) => ({
        url: `/chat/conversations/${id}`,
        method: 'PATCH',
        body: { title },
      }),
      invalidatesTags: ['ConversationList'],
    }),
    deleteConversation: builder.mutation<void, string>({
      query: (id) => ({ url: `/chat/conversations/${id}`, method: 'DELETE' }),
      invalidatesTags: ['ConversationList'],
    }),
    sendMessage: builder.mutation<
      Conversation,
      { profile_id: string | null; message: string; conversation_id: string | null }
    >({
      query: (body) => ({ url: '/chat', method: 'POST', body }),
      invalidatesTags: ['ConversationList'],
      async onQueryStarted(_, { dispatch, queryFulfilled }) {
        // Add a returned turn to the server cache while preserving loaded cursor pages.
        try {
          const { data } = await queryFulfilled;
          const patch = dispatch(
            chatApi.util.updateQueryData('getConversation', { id: data.id }, (cached) =>
              mergeConversation(cached, data),
            ),
          );
          if (!patch.patches.length)
            await dispatch(chatApi.util.upsertQueryData('getConversation', { id: data.id }, data));
        } catch {
          /* The mutation exposes the request error to the UI. */
        }
      },
    }),
  }),
});
export const {
  useGetConversationsInfiniteQuery,
  useGetConversationQuery,
  useSendMessageMutation,
  useRenameConversationMutation,
  useDeleteConversationMutation,
} = chatApi;
