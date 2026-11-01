import { useEffect, useRef, useState } from 'react';
import { skipToken } from '@reduxjs/toolkit/query';
import { ArrowUp, FileCheck2, MessageSquare, Plus } from 'lucide-react';
import { useGetConversationQuery, useSendMessageMutation } from '../api/chatApi';
import { resetConversation, setConversation } from '../store/chatSlice';
import { selectChat } from '../store/chatSelectors';
import { useSelectedProfile } from '../../business-profile/hooks/useSelectedProfile';
import { useGetProfilesQuery } from '../../business-profile/api/profileApi';
import { resetProfile, setProfile } from '../../business-profile/store/profileSlice';
import { ProfileSelectors } from '../../business-profile/components/ProfileSelectors';
import { useAppDispatch, useAppSelector } from '../../../store/hooks';
import { Button } from '../../../common/components/Button';
import { Notice } from '../../../common/components/Notice';
import { errorMessage } from '../../../common/utils/format';
import { AnswerCard } from './AnswerCard';
import { ChatHistory } from './ChatHistory';

// Guide profile selection inside a conversation while keeping saved chats on the left.
export function ChatPanel() {
  const profile = useSelectedProfile();
  const { data: profiles } = useGetProfilesQuery();
  const chat = useAppSelector(selectChat);
  const dispatch = useAppDispatch();
  const [text, setText] = useState('');
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
  const stale = Boolean(chat.profileId && chat.profileId !== profile?.id);
  const newestMessageId = conversation?.messages.at(-1)?.id;
  useEffect(() => {
    end.current?.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }, [newestMessageId, isLoading]);

  // Persist introductory turns without a profile and retrieve evidence only after selection.
  async function submit(message: string) {
    if (!message.trim() || isLoading || loadingHistory) return;
    try {
      const result = await send({
        profile_id: profile?.id ?? null,
        message,
        conversation_id: stale ? null : chat.conversationId,
      }).unwrap();
      dispatch(setConversation({ id: result.id, profileId: result.profile_id }));
      setText('');
      setBefore(undefined);
    } catch {
      /* RTK Query exposes the request error below. */
    }
  }

  // Clear the draft and selections without removing any saved conversation.
  function newChat() {
    dispatch(resetConversation());
    dispatch(resetProfile());
    setBefore(undefined);
    setText('');
    resetSend();
  }

  return (
    <section className="chat-panel">
      <div className="chat-with-history">
        <div className="chat-sidebar">
          <Button className="button-secondary" onClick={newChat} disabled={isLoading}>
            <Plus size={16} /> New chat
          </Button>
          <ChatHistory
            onDeleted={(id) => {
              if (id === chat.conversationId) newChat();
            }}
            selectedId={chat.conversationId}
            busy={isLoading}
            onSelect={(saved) => {
              const savedProfile = profiles?.profiles.find((row) => row.id === saved.profile_id);
              if (saved.profile_id && !savedProfile) return;
              if (savedProfile) dispatch(setProfile(savedProfile));
              else dispatch(resetProfile());
              dispatch(setConversation({ id: saved.id, profileId: saved.profile_id }));
              setBefore(undefined);
              setText('');
              resetSend();
            }}
          />
        </div>
        <div className="chat-thread">
          <header className="panel-header assistant-header">
            <h2>Business setup assistant</h2>
          </header>
          <div className="chat-history" aria-live="polite">
            {conversation?.has_older && (
              <Button
                className="button-secondary"
                disabled={isLoading || loadingHistory}
                onClick={() => setBefore(conversation.oldest_order ?? undefined)}
              >
                {loadingHistory ? 'Loading…' : 'Load earlier messages'}
              </Button>
            )}
            {loadingHistory && !conversation && (
              <p className="small muted">Loading conversation…</p>
            )}
            {stale && (
              <Notice>
                Your business selections changed. Your next message starts a new conversation.
              </Notice>
            )}
            {!loadingHistory && !conversation?.messages.length && (
              <article className="message message-assistant">
                <span className="message-label">Permit Navigator</span>
                <h3>Hello! Let’s get your business started.</h3>
                <p>
                  I’m your UAE business setup assistant. Say hello or tell me what you want to set
                  up. Choose the five options below when you’re ready, and I’ll prepare a checklist
                  using reviewed official evidence.
                </p>
              </article>
            )}
            {conversation?.messages.map((message) => (
              <article className={`message message-${message.role}`} key={message.id}>
                <span className="message-label">
                  {message.role === 'user' ? 'You' : 'Permit Navigator'}
                </span>
                {message.answer ? <AnswerCard answer={message.answer} /> : <p>{message.text}</p>}
              </article>
            ))}
            {(!conversation?.profile_id || stale) && !loadingHistory && (
              <div className="chat-profile-card">
                <ProfileSelectors inline disabled={isLoading} />
                <Button
                  disabled={!profile || isLoading}
                  onClick={() =>
                    void submit(
                      'Prepare an evidence-backed business setup checklist for my selected profile. Clearly identify any missing activity-specific evidence.',
                    )
                  }
                >
                  <FileCheck2 size={17} /> Generate my checklist
                </Button>
              </div>
            )}
            {isLoading && (
              <p className="muted pending">
                {profile
                  ? 'Retrieving approved evidence and preparing your answer…'
                  : 'Preparing your welcome…'}
              </p>
            )}
            {(error || historyError) && (
              <Notice error>{errorMessage(error || historyError)}</Notice>
            )}
            <div ref={end} />
          </div>
          <form
            className="composer"
            onSubmit={(event) => {
              event.preventDefault();
              void submit(text);
            }}
          >
            <div className="composer-input">
              <MessageSquare size={18} />
              <textarea
                aria-label="Your licensing question"
                placeholder={
                  profile
                    ? 'Ask about requirements, documents, or next steps…'
                    : 'Say hello or ask how to start your business…'
                }
                value={text}
                onChange={(event) => setText(event.target.value)}
                disabled={isLoading || loadingHistory}
                rows={2}
                maxLength={4000}
              />
              <Button
                type="submit"
                aria-label="Send question"
                disabled={!text.trim() || isLoading || loadingHistory}
              >
                <ArrowUp size={19} />
              </Button>
            </div>
            <p>
              Database-only guidance · No live web search in chat · Preparation assistance, not
              confirmation of eligibility
            </p>
          </form>
        </div>
      </div>
    </section>
  );
}
