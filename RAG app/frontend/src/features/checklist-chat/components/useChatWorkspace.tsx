import { useEffect, useLayoutEffect, useRef, useState } from 'react';
import { skipToken } from '@reduxjs/toolkit/query';
import { useGetConversationQuery, useSendMessageMutation } from '../api/chatApi';
import { resetConversation, setConversation, setDraft } from '../store/chatSlice';
import { selectChat } from '../store/chatSelectors';
import { useGetProfilesQuery } from '../../business-profile/api/profileApi';
import { resetProfile, setProfile } from '../../business-profile/store/profileSlice';
import { ProfileQuestions } from '../../business-profile/components/ProfileQuestions';
import { useAppDispatch, useAppSelector } from '../../../store/hooks';
import { errorMessage } from '../../../common/utils/format';
import { ChatHistory } from './ChatHistory';
import type { Message } from '../../../common/types/api';

// Share conversation state and API behavior across independently composed interfaces.
export function useChatWorkspace() {
  const { data: profiles } = useGetProfilesQuery();
  const chat = useAppSelector(selectChat);
  const dispatch = useAppDispatch();
  const text = chat.drafts[chat.conversationId ?? 'new'] ?? '';
  // Preserve an unsent question when switching workspaces or design previews.
  function setText(value: string) {
    dispatch(setDraft({ conversationId: chat.conversationId, text: value }));
  }
  const input = useRef<HTMLTextAreaElement>(null);
  useLayoutEffect(() => {
    // Grow the draft naturally; show an internal scrollbar only for long messages.
    const field = input.current;
    if (!field) return;
    field.style.height = 'auto';
    field.style.height = `${Math.min(field.scrollHeight, 140)}px`;
    field.style.overflowY = field.scrollHeight > 140 ? 'auto' : 'hidden';
  }, [text]);
  const [historyOpen, setHistoryOpen] = useState(false);
  const [before, setBefore] = useState<number | undefined>();
  const [send, { isLoading, error, reset: resetSend }] = useSendMessageMutation();
  const {
    currentData: conversation,
    error: historyError,
    isFetching: loadingHistory,
  } = useGetConversationQuery(
    chat.conversationId ? { id: chat.conversationId, before } : skipToken,
  );
  const end = useRef<HTMLDivElement>(null);
  const newest = useRef<HTMLElement>(null);
  const newestMessageId = conversation?.messages.at(-1)?.id;
  useEffect(() => {
    if (!newestMessageId && !isLoading) return;
    const behavior = window.matchMedia('(prefers-reduced-motion: reduce)').matches
      ? 'instant'
      : 'smooth';
    const scroller = end.current?.closest('.chat-history');
    if (!(scroller instanceof HTMLElement)) return;
    const target = newest.current;
    const top = isLoading
      ? scroller.scrollHeight
      : target
        ? target.getBoundingClientRect().top -
          scroller.getBoundingClientRect().top +
          scroller.scrollTop -
          16
        : scroller.scrollTop;
    scroller.scrollTo({ top, behavior });
  }, [newestMessageId, isLoading]);

  // Persist introductory turns without a profile and retrieve evidence only after selection.
  async function submit(message: string, selectedProfileId: string | null = chat.profileId) {
    if (!message.trim() || isLoading || loadingHistory) return;
    try {
      const result = await send({
        profile_id: selectedProfileId,
        message,
        conversation_id: chat.conversationId,
      }).unwrap();
      dispatch(setConversation({ id: result.id, profileId: result.profile_id }));
      const confirmedProfile = profiles?.profiles.find((row) => row.id === result.profile_id);
      if (confirmedProfile) dispatch(setProfile(confirmedProfile));
      setText('');
      setBefore(undefined);
    } catch {
      /* RTK Query exposes the request error below. */
    }
  }

  // Clear the draft and selections without removing any saved conversation.
  function newChat() {
    if (
      !chat.conversationId &&
      text.trim() &&
      !window.confirm('Discard this unsent draft and start a new chat?')
    )
      return;
    setHistoryOpen(false);
    dispatch(resetConversation());
    dispatch(resetProfile());
    setBefore(undefined);
    dispatch(setDraft({ conversationId: null, text: '' }));
    resetSend();
    requestAnimationFrame(() => input.current?.focus({ preventScroll: true }));
  }

  const history = (
    <ChatHistory
      selectedId={chat.conversationId}
      busy={isLoading}
      onDeleted={(id) => {
        if (id === chat.conversationId) newChat();
      }}
      onSelect={(saved) => {
        const savedProfile = profiles?.profiles.find((row) => row.id === saved.profile_id);
        if (saved.profile_id && !savedProfile) return;
        if (savedProfile) dispatch(setProfile(savedProfile));
        else dispatch(resetProfile());
        dispatch(setConversation({ id: saved.id, profileId: saved.profile_id }));
        setBefore(undefined);
        resetSend();
        setHistoryOpen(false);
      }}
    />
  );
  // Offer all five profile questions together only on the latest assistant request.
  function profilePrompt(message: Message) {
    return message.answer?.profile_questions &&
      message.id === newestMessageId &&
      !chat.profileId ? (
      <ProfileQuestions
        disabled={isLoading}
        onConfirm={(selected) =>
          void submit(
            `Prepare an evidence-backed business setup checklist for this profile: ${selected.emirate}, ${selected.jurisdiction}, ${selected.activity}, ${selected.application_type}, ${selected.legal_structure}. Identify missing evidence.`,
            selected.id,
          )
        }
      />
    ) : undefined;
  }
  return {
    text,
    setText,
    input,
    historyOpen,
    setHistoryOpen,
    history,
    submit,
    newChat,
    isLoading,
    loadingHistory,
    conversation,
    newestMessageId,
    newest,
    end,
    profilePrompt,
    profile: profiles?.profiles.find((row) => row.id === chat.profileId),
    error: error || historyError ? errorMessage(error || historyError) : null,
    loadEarlier: () => setBefore(conversation?.oldest_order ?? undefined),
  };
}
export type ChatWorkspaceModel = ReturnType<typeof useChatWorkspace>;
