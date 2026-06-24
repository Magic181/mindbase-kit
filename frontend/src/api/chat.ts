import api from './index'

export interface Conversation {
  id: number
  notebook_id: number
  title: string
  created_at: string
  updated_at: string
}

export interface Citation {
  document_id: number
  document_name: string
  chunk_id: number
  chunk_text: string
  position: number
}

export interface Message {
  id: number
  conversation_id: number
  role: 'user' | 'assistant'
  content: string
  citations: Citation[]
  created_at: string
}

export const chatApi = {
  listConversations: (notebookId: number) =>
    api.get<Conversation[]>(`/notebooks/${notebookId}/conversations/`),
  createConversation: (notebookId: number, title?: string) =>
    api.post<Conversation>(`/notebooks/${notebookId}/conversations/`, { title }),
  listMessages: (conversationId: number) =>
    api.get<Message[]>(`/conversations/${conversationId}/messages/`),
  sendMessage: (conversationId: number, content: string) =>
    api.post<{
      user_message: Message
      assistant_message: Message
    }>(`/conversations/${conversationId}/messages/send/`, { content }),
}

