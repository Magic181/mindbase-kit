import api, { ensureFreshToken } from './index'

export interface Conversation {
  id: number
  notebook_id: number
  title: string
  created_at: string
  updated_at: string
}

export interface DocumentCitation {
  source_type?: 'document'
  document_id: number
  document_name: string
  chunk_id: number
  chunk_text: string
  position: number
  document_source_type?: 'paragraph' | 'page' | 'table' | 'code' | 'image_ocr' | 'image_caption' | 'mixed' | 'text' | string
  metadata?: Record<string, unknown>
}

export interface WebCitation {
  source_type: 'web'
  title: string
  url: string
  content: string
  position: number
}

export type Citation = DocumentCitation | WebCitation
export type SearchMode = 'local' | 'web' | 'hybrid'

export interface Message {
  id: number
  conversation_id: number
  role: 'user' | 'assistant'
  content: string
  citations: Citation[]
  created_at: string
}

export interface SendMessageStreamHandlers {
  onUserMessage?: (message: Message) => void
  onDelta?: (content: string) => void
  onAssistantMessage?: (message: Message) => void
  onError?: (message: string) => void
}

export const chatApi = {
  listConversations: (notebookId: number) =>
    api.get<Conversation[]>(`/notebooks/${notebookId}/conversations/`),
  createConversation: (notebookId: number, title?: string) =>
    api.post<Conversation>(`/notebooks/${notebookId}/conversations/`, { title }),
  updateConversation: (conversationId: number, title: string) =>
    api.patch<Conversation>(`/conversations/${conversationId}/`, { title }),
  deleteConversation: (conversationId: number) =>
    api.delete(`/conversations/${conversationId}/`),
  listMessages: (conversationId: number) =>
    api.get<Message[]>(`/conversations/${conversationId}/messages/`),
  sendMessage: (
    conversationId: number,
    content: string,
    searchMode: SearchMode = 'local',
  ) =>
    api.post<{
      user_message: Message
      assistant_message: Message
    }>(`/conversations/${conversationId}/messages/send/`, {
      content,
      search_mode: searchMode,
    }),
  sendMessageStream: (
    conversationId: number,
    content: string,
    searchMode: SearchMode = 'local',
    handlers: SendMessageStreamHandlers = {},
  ) => sendMessageStream(conversationId, content, searchMode, handlers),
}

async function sendMessageStream(
  conversationId: number,
  content: string,
  searchMode: SearchMode,
  handlers: SendMessageStreamHandlers,
) {
  await ensureFreshToken().catch(() => {})
  const token = localStorage.getItem('access_token')
  const response = await fetch(`/api/v1/conversations/${conversationId}/messages/send/stream/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: JSON.stringify({
      content,
      search_mode: searchMode,
    }),
  })

  if (!response.ok || !response.body) {
    throw new Error(await streamErrorMessage(response))
  }

  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''

  let reading = true
  while (reading) {
    const { done, value } = await reader.read()
    if (done) {
      reading = false
    } else {
      buffer += decoder.decode(value, { stream: true })
      buffer = parseSseBuffer(buffer, handlers)
    }
  }

  buffer += decoder.decode()
  if (buffer.trim()) {
    parseSseBuffer(`${buffer}\n\n`, handlers)
  }
}

function parseSseBuffer(buffer: string, handlers: SendMessageStreamHandlers) {
  let nextBuffer = buffer.replace(/\r\n/g, '\n')
  let boundary = nextBuffer.indexOf('\n\n')

  while (boundary >= 0) {
    const rawEvent = nextBuffer.slice(0, boundary)
    nextBuffer = nextBuffer.slice(boundary + 2)
    handleSseEvent(rawEvent, handlers)
    boundary = nextBuffer.indexOf('\n\n')
  }

  return nextBuffer
}

function handleSseEvent(rawEvent: string, handlers: SendMessageStreamHandlers) {
  let eventName = 'message'
  const dataLines: string[] = []

  for (const line of rawEvent.split(/\r?\n/)) {
    if (line.startsWith('event:')) {
      eventName = line.slice(6).trim()
    } else if (line.startsWith('data:')) {
      dataLines.push(line.slice(5).trimStart())
    }
  }

  const payload = dataLines.length ? JSON.parse(dataLines.join('\n')) : {}

  if (eventName === 'user_message') {
    handlers.onUserMessage?.(payload as Message)
  } else if (eventName === 'delta') {
    handlers.onDelta?.(String(payload.content || ''))
  } else if (eventName === 'assistant_message') {
    handlers.onAssistantMessage?.(payload as Message)
  } else if (eventName === 'error') {
    handlers.onError?.(String(payload.message || '回答生成失败'))
  }
}

async function streamErrorMessage(response: Response) {
  try {
    const body = await response.text()
    return body || `Request failed with status ${response.status}`
  } catch {
    return `Request failed with status ${response.status}`
  }
}
