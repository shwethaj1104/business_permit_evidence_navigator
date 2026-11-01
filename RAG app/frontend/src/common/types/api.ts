export interface Profile {
  id: string;
  emirate: string;
  jurisdiction: string;
  activity: string;
  application_type: string;
  legal_structure: string;
  coverage_note: string;
}
export type ProfileField =
  'emirate' | 'jurisdiction' | 'activity' | 'application_type' | 'legal_structure';
export interface Health {
  status: string;
  database_ready: boolean;
  openai_configured: boolean;
  message: string | null;
  model: string;
  embedding_model: string;
}
export interface ChecklistItem {
  title: string;
  detail: string;
  condition: string;
  evidence_ids: string[];
}
export interface Citation {
  id: string;
  source_id: string;
  version_id: string;
  title: string;
  url: string;
  locator: string;
  excerpt: string;
  fetched_at: string;
  last_checked_at: string | null;
  source_published_at: string | null;
  source_updated_at: string | null;
  newer_version_available: boolean;
}
export interface Answer {
  kind: 'checklist' | 'follow_up' | 'gap';
  message: string;
  items: ChecklistItem[];
  gaps: string[];
  citations: Citation[];
}
export interface Message {
  id: string;
  order: number;
  role: 'user' | 'assistant';
  text: string;
  answer: Answer | null;
}
export interface Conversation {
  id: string;
  profile_id: string | null;
  messages: Message[];
  has_older: boolean;
  oldest_order: number | null;
}
export interface Outcome {
  url: string;
  status: string;
  summary: string;
  version_id?: string;
}
export interface SyncJob {
  id: string;
  profile_id: string;
  status: string;
  discover: boolean;
  created_at: string;
  attempts: number;
  outcomes: Outcome[];
  error: string | null;
}
export interface Source {
  id: string;
  title: string;
  url: string;
  profile_id: string;
  active_version_id: string | null;
  latest_version_id: string | null;
  latest_version_status: string | null;
  last_capture_status: string | null;
  last_capture_error: string | null;
  last_checked_at: string | null;
  last_successful_fetch_at: string | null;
}
export interface Version {
  id: string;
  source_id: string;
  profile_id: string;
  title: string;
  url: string;
  status: string;
  summary: string;
  previous_version_id: string | null;
  section_changes: {
    locator: string;
    status: string;
    change_detected_at: string;
    previous_change_detected_at: string | null;
  }[];
  diff: string;
  text: string;
  fetched_at: string;
  change_detected_at: string;
  source_published_at: string | null;
  source_updated_at: string | null;
  effective_from: string | null;
  reviewed_at: string | null;
  activated_at: string | null;
}

export type VersionSummary = Omit<Version, 'text' | 'diff' | 'section_changes'>;

export interface ConversationSummary {
  id: string;
  profile_id: string | null;
  title: string;
  preview: string;
  created_at: string;
  updated_at: string;
}
export interface ConversationPage {
  conversations: ConversationSummary[];
  next_cursor: string | null;
}
