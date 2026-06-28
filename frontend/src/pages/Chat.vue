<template>
  <div class="flex h-full">
    <aside class="hidden w-64 shrink-0 border-r border-line bg-surface-secondary md:block">
      <div class="px-4 py-4">
        <p class="text-sm font-medium text-content">会话</p>
        <p class="mt-1 text-xs text-content-secondary">{{ notebookDisplayLabel }}</p>
      </div>
      <div class="px-3 pb-2">
        <button
          class="gemini-btn gemini-btn-tonal w-full"
          :disabled="creatingConversation"
          @click="createConversation()"
        >
          <span class="text-base leading-none">+</span>
          {{ creatingConversation ? '创建中...' : '新会话' }}
        </button>
      </div>
      <div class="max-h-[calc(100vh-130px)] overflow-y-auto px-2 pb-2">
        <div
          v-for="c in conversations"
          :key="c.id"
          class="group mb-1 flex min-h-[44px] items-center gap-1 rounded-pill px-1 transition-colors"
          :class="c.id === activeConversationId ? 'bg-primary-soft' : 'hover:bg-surface-hover'"
        >
          <form
            v-if="editingConversationId === c.id"
            class="flex min-w-0 flex-1 items-center gap-1"
            @submit.prevent="saveConversationTitle(c)"
          >
            <input
              v-model="editingConversationTitle"
              class="min-w-0 flex-1 rounded-pill border border-primary/30 bg-surface-elevated px-3 py-1.5 text-sm text-content outline-none focus:border-primary focus:ring-2 focus:ring-primary-soft"
              maxlength="100"
              autofocus
              @keydown.esc.prevent="cancelEditingConversation"
            />
            <button
              type="submit"
              class="gemini-btn gemini-btn-tonal gemini-btn-sm shrink-0"
              :disabled="renamingConversation"
            >
              保存
            </button>
          </form>
          <button
            v-else
            class="min-w-0 flex-1 truncate px-4 py-2 text-left text-sm"
            :class="c.id === activeConversationId ? 'font-medium text-primary' : 'text-content-secondary hover:text-content'"
            @click="selectConversation(c.id)"
          >
            {{ c.title || '未命名会话' }}
          </button>
          <button
            v-if="editingConversationId !== c.id"
            class="gemini-btn gemini-btn-ghost gemini-btn-sm shrink-0 opacity-0 group-hover:opacity-100"
            :disabled="renamingConversation"
            @click="startEditingConversation(c)"
          >
            编辑
          </button>
          <button
            v-if="editingConversationId !== c.id"
            class="gemini-btn gemini-btn-danger gemini-btn-sm mr-1 shrink-0 opacity-0 group-hover:opacity-100"
            :disabled="deletingConversation || renamingConversation"
            @click="openDeleteConversation(c)"
          >
            删除
          </button>
        </div>
      </div>
    </aside>

    <div class="flex flex-1 flex-col">
      <header class="flex h-16 shrink-0 items-center justify-between px-6">
        <div class="min-w-0">
          <h2 class="truncate text-lg font-semibold tracking-tight">
            <span class="gemini-gradient-text">AI 对话</span>
          </h2>
          <p class="truncate text-xs text-content-secondary">
            {{ headerHint }}
          </p>
        </div>
        <div class="flex shrink-0 items-center gap-2 md:hidden">
          <button
            class="gemini-btn gemini-btn-ghost"
            @click="createConversation()"
          >
            新会话
          </button>
          <button
            v-if="activeConversation"
            class="gemini-btn gemini-btn-danger"
            :disabled="deletingConversation"
            @click="openDeleteConversation(activeConversation)"
          >
            删除
          </button>
        </div>
      </header>

      <div class="relative min-h-0 flex-1">
        <div
          ref="messagesViewport"
          class="h-full space-y-4 overflow-y-auto p-6"
          @scroll="handleMessagesScroll"
        >
          <div
            v-if="loadingMessages"
            class="flex h-full items-center justify-center text-sm text-content-secondary"
          >
            加载中...
          </div>

          <div
            v-else-if="messages.length === 0"
            class="flex h-full flex-col items-center justify-center text-center"
          >
            <div class="mb-5 flex h-12 w-12 items-center justify-center rounded-2xl bg-primary-soft text-primary">
              <svg viewBox="0 0 24 24" class="h-6 w-6" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
              </svg>
            </div>
            <p class="text-lg font-semibold text-content">开始新的对话</p>
            <p class="mt-2 max-w-md text-sm text-content-secondary">
              {{ emptyStateHint }}
            </p>
          </div>

          <div v-else class="space-y-5">
            <div
              v-for="msg in messages"
              :key="msg.id"
              :ref="(el) => setMessageElement(msg.id, el)"
              class="flex scroll-mt-6 gap-3"
              :class="msg.role === 'user' ? 'justify-end' : 'justify-start'"
            >
              <div
                v-if="msg.role === 'assistant'"
                class="ai-avatar mt-0.5"
              >
                <svg viewBox="0 0 24 24" class="h-4 w-4" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M12 3l1.35 4.15L17.5 8.5l-4.15 1.35L12 14l-1.35-4.15L6.5 8.5l4.15-1.35L12 3z" />
                  <path d="M18 13l.75 2.25L21 16l-2.25.75L18 19l-.75-2.25L15 16l2.25-.75L18 13z" />
                  <path d="M6 14l.55 1.45L8 16l-1.45.55L6 18l-.55-1.45L4 16l1.45-.55L6 14z" />
                </svg>
              </div>
              <div
                class="min-w-0"
                :class="msg.role === 'user' ? 'max-w-[80%]' : 'max-w-[min(880px,calc(100%-44px))]'"
              >
                <div
                  v-if="msg.role === 'user'"
                  class="whitespace-pre-wrap break-words rounded-2xl bg-primary px-4 py-3 text-sm leading-7 text-primary-contrast shadow-gsm"
                >
                  {{ msg.content }}
                </div>
                <div
                  v-else
                  class="assistant-message rounded-2xl bg-surface-elevated px-5 py-4 text-content shadow-gsm"
                >
                  <div
                    class="markdown-body"
                    v-html="renderMarkdown(msg.content)"
                  />
                </div>

                <CitationList
                  v-if="msg.role === 'assistant'"
                  :citations="msg.citations || []"
                />
              </div>
            </div>

            <div v-if="sending && !streamingAssistantId" class="flex items-center gap-3">
              <div class="ai-avatar">
                <svg viewBox="0 0 24 24" class="h-4 w-4" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M12 3l1.35 4.15L17.5 8.5l-4.15 1.35L12 14l-1.35-4.15L6.5 8.5l4.15-1.35L12 3z" />
                  <path d="M18 13l.75 2.25L21 16l-2.25.75L18 19l-.75-2.25L15 16l2.25-.75L18 13z" />
                </svg>
              </div>
              <div class="flex gap-1.5 rounded-2xl bg-surface-elevated px-4 py-3.5 shadow-gsm">
                <span class="h-2 w-2 animate-bounce rounded-full bg-primary/60 [animation-delay:-0.3s]" />
                <span class="h-2 w-2 animate-bounce rounded-full bg-primary/60 [animation-delay:-0.15s]" />
                <span class="h-2 w-2 animate-bounce rounded-full bg-primary/60" />
              </div>
            </div>
          </div>
        </div>

        <nav
          v-if="messageJumpItems.length > 1"
          class="conversation-jump-nav hidden xl:block"
          aria-label="会话位置导航"
        >
          <button
            v-for="item in messageJumpItems"
            :key="item.id"
            type="button"
            class="conversation-jump-item"
            :class="{ 'conversation-jump-item-active': item.id === activeJumpMessageId }"
            :title="item.title"
            @click="scrollToMessage(item.id)"
          >
            <span class="conversation-jump-title">{{ item.title }}</span>
            <span class="conversation-jump-marker" />
          </button>
        </nav>
      </div>

      <div class="shrink-0 px-4 pb-5 pt-2">
        <div class="chat-composer mx-auto w-full max-w-3xl">
          <div class="px-3 pt-3">
            <div class="composer-source-controls" aria-label="回答资料来源">
              <button
                type="button"
                class="composer-source-pill"
                :class="{ 'composer-source-pill-active': webSearchEnabled }"
                :aria-pressed="webSearchEnabled"
                :disabled="sending"
                @click="webSearchEnabled = !webSearchEnabled"
              >
                联网搜索
              </button>
            </div>
          </div>
          <form
            class="flex items-center gap-2 px-4 pb-3 pt-2"
            @submit.prevent="sendMessage"
          >
            <input
              v-model="input"
              type="text"
              placeholder="输入你的问题..."
              class="min-h-10 flex-1 bg-transparent text-content outline-none placeholder:text-content-secondary"
            />
            <button
              type="submit"
              :disabled="!input.trim() || sending || !activeConversationId"
              class="gemini-icon-btn gemini-icon-btn-primary shrink-0"
              aria-label="发送"
            >
              <svg viewBox="0 0 24 24" class="h-5 w-5" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <line x1="12" y1="19" x2="12" y2="5" />
                <polyline points="5 12 12 5 19 12" />
              </svg>
            </button>
          </form>
        </div>
      </div>
    </div>
  </div>

  <div
    v-if="conversationToDelete"
    class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4 backdrop-blur-sm"
    @click.self="conversationToDelete = null"
  >
    <div class="gemini-rise w-full max-w-sm rounded-glg border border-line bg-surface-elevated p-6 shadow-glg">
      <h2 class="text-lg font-semibold text-content">确认删除会话</h2>
      <p class="mt-2 break-words text-sm text-content-secondary">
        确定要删除「{{ conversationToDelete.title || '未命名会话' }}」吗？此操作会删除该会话下的所有消息。
      </p>
      <div class="mt-6 flex justify-end gap-3">
        <button
          class="gemini-btn gemini-btn-ghost"
          @click="conversationToDelete = null"
        >
          取消
        </button>
        <button
          :disabled="deletingConversation"
          class="gemini-btn gemini-btn-danger"
          @click="deleteConversation"
        >
          {{ deletingConversation ? '删除中...' : '删除' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onBeforeUpdate, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { chatApi, type Conversation, type Message, type SearchMode } from '@/api/chat'
import CitationList from '@/components/chat/CitationList.vue'
import { useNotebookStore } from '@/stores/notebook'

const route = useRoute()
const notebookStore = useNotebookStore()
const notebookId = computed(() => Number(route.params.id))

const conversations = ref<Conversation[]>([])
const activeConversationId = ref<number | null>(null)
const messages = ref<Message[]>([])
const input = ref('')
const webSearchEnabled = ref(false)
const messagesViewport = ref<HTMLElement | null>(null)
const conversationToDelete = ref<Conversation | null>(null)
const editingConversationId = ref<number | null>(null)
const editingConversationTitle = ref('')

const loadingMessages = ref(false)
const creatingConversation = ref(false)
const deletingConversation = ref(false)
const renamingConversation = ref(false)
const sending = ref(false)
const streamingAssistantId = ref<number | null>(null)
const activeJumpMessageId = ref<number | null>(null)
const messageElements = new Map<number, HTMLElement>()
let jumpScrollFrame = 0

const searchMode = computed<SearchMode>(() => (webSearchEnabled.value ? 'hybrid' : 'local'))

const headerHint = computed(() => {
  if (!activeConversationId.value) return '正在初始化会话...'
  return activeConversation.value?.title?.trim() || '新会话'
})

const activeConversation = computed(() => {
  return conversations.value.find((item) => item.id === activeConversationId.value) || null
})

const notebookDisplayLabel = computed(() => {
  const notebook = notebookStore.notebooks.find((item) => item.id === notebookId.value)
  if (notebook?.name?.trim()) return notebook.name
  if (notebookStore.currentNotebook?.id === notebookId.value && notebookStore.currentNotebook.name.trim()) {
    return notebookStore.currentNotebook.name
  }
  return '当前 Notebook'
})

const messageJumpItems = computed(() => {
  return messages.value
    .filter((message) => message.role === 'user')
    .map((message) => ({
      id: message.id,
      title: messageJumpTitle(message.content),
    }))
})

const emptyStateHint = computed(() => {
  if (webSearchEnabled.value) return '当前会同时结合 Notebook 文档和联网搜索结果回答。'
  return '当前会基于该 Notebook 的已解析文档进行检索并回答。'
})

onBeforeUpdate(() => {
  messageElements.clear()
})

async function scrollMessagesToBottom(behavior: 'auto' | 'smooth' = 'auto') {
  await nextTick()
  const el = messagesViewport.value
  if (!el) return
  el.scrollTo({
    top: el.scrollHeight,
    behavior,
  })
  updateActiveJumpMessage()
}

function setMessageElement(messageId: number, element: unknown) {
  if (element instanceof HTMLElement) {
    messageElements.set(messageId, element)
  }
}

function handleMessagesScroll() {
  if (jumpScrollFrame) return
  jumpScrollFrame = window.requestAnimationFrame(() => {
    jumpScrollFrame = 0
    updateActiveJumpMessage()
  })
}

function updateActiveJumpMessage() {
  const viewport = messagesViewport.value
  const items = messageJumpItems.value
  if (!viewport || !items.length) {
    activeJumpMessageId.value = null
    return
  }

  const viewportTop = viewport.getBoundingClientRect().top
  let activeId = items[0].id

  for (const item of items) {
    const element = messageElements.get(item.id)
    if (!element) continue
    const offset = element.getBoundingClientRect().top - viewportTop
    if (offset <= 96) {
      activeId = item.id
    } else {
      break
    }
  }

  activeJumpMessageId.value = activeId
}

async function scrollToMessage(messageId: number) {
  await nextTick()
  const element = messageElements.get(messageId)
  if (!element) return
  activeJumpMessageId.value = messageId
  element.scrollIntoView({
    behavior: 'smooth',
    block: 'start',
  })
}

function messageJumpTitle(content: string) {
  const title = content.replace(/\s+/g, ' ').trim()
  if (!title) return '新问题'
  return title.length > 16 ? `${title.slice(0, 16)}...` : title
}

function renderMarkdown(content: string) {
  return markdownToHtml(content)
}

function markdownToHtml(source: string) {
  const lines = source.replace(/\r\n/g, '\n').split('\n')
  const html: string[] = []
  let paragraph: string[] = []
  let listType: 'ol' | 'ul' | null = null
  let codeFence: string[] | null = null
  let codeLanguage = ''

  const closeParagraph = () => {
    if (!paragraph.length) return
    html.push(`<p>${inlineMarkdown(paragraph.join(' '))}</p>`)
    paragraph = []
  }

  const closeList = () => {
    if (!listType) return
    html.push(`</${listType}>`)
    listType = null
  }

  const openList = (type: 'ol' | 'ul') => {
    if (listType === type) return
    closeList()
    html.push(`<${type}>`)
    listType = type
  }

  let index = 0
  while (index < lines.length) {
    const line = lines[index]
    const trimmed = line.trim()

    if (trimmed.startsWith('```')) {
      closeParagraph()
      closeList()
      if (codeFence) {
        const languageClass = codeLanguage ? ` class="language-${escapeAttribute(codeLanguage)}"` : ''
        html.push(`<pre><code${languageClass}>${escapeHtml(codeFence.join('\n'))}</code></pre>`)
        codeFence = null
        codeLanguage = ''
      } else {
        codeFence = []
        codeLanguage = trimmed.slice(3).trim()
      }
      index += 1
      continue
    }

    if (codeFence) {
      codeFence.push(line)
      index += 1
      continue
    }

    if (!trimmed) {
      closeParagraph()
      closeList()
      index += 1
      continue
    }

    if (trimmed === '---' || trimmed === '***' || trimmed === '___') {
      closeParagraph()
      closeList()
      html.push('<hr>')
      index += 1
      continue
    }

    if (isMarkdownTableStart(lines, index)) {
      closeParagraph()
      closeList()
      const { html: tableHtml, nextIndex } = renderMarkdownTable(lines, index)
      html.push(tableHtml)
      index = nextIndex
      continue
    }

    const heading = trimmed.match(/^(#{1,4})\s+(.+)$/)
    if (heading) {
      closeParagraph()
      closeList()
      const level = heading[1].length + 1
      html.push(`<h${level}>${inlineMarkdown(heading[2])}</h${level}>`)
      index += 1
      continue
    }

    const unordered = trimmed.match(/^[-*]\s+(.+)$/)
    if (unordered) {
      closeParagraph()
      openList('ul')
      html.push(`<li>${inlineMarkdown(unordered[1])}</li>`)
      index += 1
      continue
    }

    const ordered = trimmed.match(/^\d+[.)]\s+(.+)$/)
    if (ordered) {
      closeParagraph()
      openList('ol')
      html.push(`<li>${inlineMarkdown(ordered[1])}</li>`)
      index += 1
      continue
    }

    if (trimmed.startsWith('>')) {
      closeParagraph()
      closeList()
      html.push(`<blockquote>${inlineMarkdown(trimmed.replace(/^>\s?/, ''))}</blockquote>`)
      index += 1
      continue
    }

    paragraph.push(trimmed)
    index += 1
  }

  closeParagraph()
  closeList()
  if (codeFence) {
    const languageClass = codeLanguage ? ` class="language-${escapeAttribute(codeLanguage)}"` : ''
    html.push(`<pre><code${languageClass}>${escapeHtml(codeFence.join('\n'))}</code></pre>`)
  }

  return html.join('')
}

function isMarkdownTableStart(lines: string[], index: number) {
  const header = lines[index]?.trim() || ''
  const separator = lines[index + 1]?.trim() || ''
  return isMarkdownTableRow(header) && isMarkdownTableSeparator(separator)
}

function isMarkdownTableRow(line: string) {
  return line.startsWith('|') && line.endsWith('|') && line.split('|').length >= 4
}

function isMarkdownTableSeparator(line: string) {
  if (!isMarkdownTableRow(line)) return false
  return parseMarkdownTableRow(line).every((cell) => /^:?-{3,}:?$/.test(cell.trim()))
}

function renderMarkdownTable(lines: string[], startIndex: number) {
  const headerCells = parseMarkdownTableRow(lines[startIndex])
  const alignments = parseMarkdownTableRow(lines[startIndex + 1]).map(tableAlignment)
  const bodyRows: string[][] = []
  let index = startIndex + 2

  while (index < lines.length && isMarkdownTableRow(lines[index].trim())) {
    bodyRows.push(parseMarkdownTableRow(lines[index]))
    index += 1
  }

  const header = headerCells
    .map((cell, cellIndex) => (
      `<th${tableAlignAttribute(alignments[cellIndex])}>${inlineMarkdown(cell)}</th>`
    ))
    .join('')
  const rows = bodyRows
    .map((row) => {
      const cells = headerCells.map((_, cellIndex) => {
        const cell = row[cellIndex] || ''
        return `<td${tableAlignAttribute(alignments[cellIndex])}>${inlineMarkdown(cell)}</td>`
      })
      return `<tr>${cells.join('')}</tr>`
    })
    .join('')

  return {
    html: `<div class="table-scroll"><table><thead><tr>${header}</tr></thead><tbody>${rows}</tbody></table></div>`,
    nextIndex: index,
  }
}

function parseMarkdownTableRow(line: string) {
  return line
    .trim()
    .replace(/^\|/, '')
    .replace(/\|$/, '')
    .split('|')
    .map((cell) => cell.trim())
}

function tableAlignment(cell: string) {
  const trimmed = cell.trim()
  if (trimmed.startsWith(':') && trimmed.endsWith(':')) return 'center'
  if (trimmed.endsWith(':')) return 'right'
  return 'left'
}

function tableAlignAttribute(alignment: string | undefined) {
  if (!alignment || alignment === 'left') return ''
  return ` style="text-align:${alignment}"`
}

function inlineMarkdown(text: string) {
  return text
    .split(/(`[^`]*`)/g)
    .map((part) => {
      if (part.startsWith('`') && part.endsWith('`')) {
        return `<code>${escapeHtml(part.slice(1, -1))}</code>`
      }
      return escapeHtml(part)
        .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
        .replace(/\[([^\]]+)\]\((https?:\/\/[^)\s]+)\)/g, '<a href="$2" target="_blank" rel="noreferrer">$1</a>')
    })
    .join('')
}

function escapeHtml(value: string) {
  return value
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;')
}

function escapeAttribute(value: string) {
  return value.replace(/[^a-zA-Z0-9_-]/g, '')
}

async function loadConversations() {
  const id = notebookId.value
  if (!id) return
  const { data } = await chatApi.listConversations(id)
  conversations.value = data
  if (!activeConversationId.value && data.length > 0) {
    activeConversationId.value = data[0].id
  }
}

async function createConversation() {
  const id = notebookId.value
  if (!id) return
  creatingConversation.value = true
  try {
    const { data } = await chatApi.createConversation(id, '')
    conversations.value = [data, ...conversations.value]
    activeConversationId.value = data.id
    await loadMessages()
  } catch {
    // error shown by axios interceptor
  } finally {
    creatingConversation.value = false
  }
}

async function selectConversation(conversationId: number) {
  if (conversationId === activeConversationId.value) return
  activeConversationId.value = conversationId
  await loadMessages()
}

function openDeleteConversation(conversation: Conversation) {
  conversationToDelete.value = conversation
}

function startEditingConversation(conversation: Conversation) {
  editingConversationId.value = conversation.id
  editingConversationTitle.value = conversation.title || ''
}

function cancelEditingConversation() {
  editingConversationId.value = null
  editingConversationTitle.value = ''
}

async function saveConversationTitle(conversation: Conversation) {
  const title = editingConversationTitle.value.trim()
  renamingConversation.value = true
  try {
    const { data } = await chatApi.updateConversation(conversation.id, title)
    conversations.value = conversations.value.map((item) => (
      item.id === data.id ? data : item
    ))
    cancelEditingConversation()
  } catch {
    // error shown by axios interceptor
  } finally {
    renamingConversation.value = false
  }
}

async function deleteConversation() {
  const conversation = conversationToDelete.value
  if (!conversation) return
  deletingConversation.value = true
  try {
    await chatApi.deleteConversation(conversation.id)
    conversations.value = conversations.value.filter((item) => item.id !== conversation.id)
    conversationToDelete.value = null

    if (activeConversationId.value !== conversation.id) return

    const nextConversation = conversations.value[0]
    if (nextConversation) {
      activeConversationId.value = nextConversation.id
      await loadMessages()
    } else {
      activeConversationId.value = null
      messages.value = []
      await createConversation()
    }
  } catch {
    // error shown by axios interceptor
  } finally {
    deletingConversation.value = false
  }
}

async function loadMessages() {
  if (!activeConversationId.value) return
  loadingMessages.value = true
  try {
    const { data } = await chatApi.listMessages(activeConversationId.value)
    messages.value = data
    await scrollMessagesToBottom()
  } finally {
    loadingMessages.value = false
  }
}

async function sendMessage() {
  if (!input.value.trim() || !activeConversationId.value) return
  const content = input.value.trim()
  const conversationId = activeConversationId.value
  input.value = ''
  sending.value = true
  streamingAssistantId.value = null
  let receivedUserMessage = false
  await scrollMessagesToBottom('smooth')
  try {
    await chatApi.sendMessageStream(
      conversationId,
      content,
      searchMode.value,
      {
        onUserMessage: (message) => {
          receivedUserMessage = true
          appendMessage(message)
          void scrollMessagesToBottom('smooth')
        },
        onDelta: (delta) => {
          appendAssistantDelta(conversationId, delta)
          void scrollMessagesToBottom('smooth')
        },
        onAssistantMessage: (message) => {
          replaceStreamingAssistant(message)
          void scrollMessagesToBottom('smooth')
        },
      },
    )
  } catch {
    if (!receivedUserMessage) {
      await sendMessageWithoutStreaming(conversationId, content)
    } else {
      await loadMessages()
    }
  } finally {
    streamingAssistantId.value = null
    sending.value = false
  }
}

function appendMessage(message: Message) {
  if (messages.value.some((item) => item.id === message.id)) return
  messages.value = [...messages.value, message]
}

function appendAssistantDelta(conversationId: number, delta: string) {
  if (!delta) return

  const existingId = streamingAssistantId.value
  if (!existingId) {
    const nextId = -Date.now()
    streamingAssistantId.value = nextId
    messages.value = [
      ...messages.value,
      {
        id: nextId,
        conversation_id: conversationId,
        role: 'assistant',
        content: '',
        citations: [],
        created_at: new Date().toISOString(),
      },
    ]
  }

  messages.value = messages.value.map((message) => {
    if (message.id !== streamingAssistantId.value) return message
    return {
      ...message,
      content: `${message.content}${delta}`,
    }
  })
}

function replaceStreamingAssistant(message: Message) {
  const existingId = streamingAssistantId.value
  if (!existingId) {
    appendMessage(message)
    return
  }

  messages.value = messages.value.map((item) => (
    item.id === existingId ? message : item
  ))
}

async function sendMessageWithoutStreaming(
  conversationId: number,
  content: string,
) {
  try {
    const { data } = await chatApi.sendMessage(
      conversationId,
      content,
      searchMode.value,
    )
    appendMessage(data.user_message)
    appendMessage(data.assistant_message)
    await scrollMessagesToBottom('smooth')
  } catch {
    input.value = content
  }
}

watch(
  () => [messages.value.length, sending.value],
  () => {
    void scrollMessagesToBottom('smooth')
  },
  { flush: 'post' },
)

onMounted(async () => {
  if (!notebookStore.notebooks.length) {
    await notebookStore.fetchNotebooks().catch(() => {})
  }
  if (!notebookStore.notebooks.some((item) => item.id === notebookId.value)) {
    await notebookStore.fetchNotebook(notebookId.value).catch(() => {})
  }
  await loadConversations()
  if (!activeConversationId.value) {
    await createConversation()
  } else {
    await loadMessages()
  }
})
</script>

<style scoped>
.assistant-message {
  overflow-wrap: anywhere;
  box-shadow:
    inset 0 0 0 1px rgba(226, 237, 231, 0.54),
    0 12px 30px -26px rgba(16, 185, 129, 0.35);
}

.ai-avatar {
  display: flex;
  height: 2rem;
  width: 2rem;
  flex-shrink: 0;
  align-items: center;
  justify-content: center;
  border-radius: 9999px;
  color: #047857;
  background: #e6f4ea;
  box-shadow: inset 0 0 0 1px rgba(16, 185, 129, 0.14);
}

.chat-composer {
  border-radius: 1.75rem;
  border: 1px solid rgba(226, 237, 231, 0.86);
  background: rgba(255, 255, 255, 0.88);
  box-shadow:
    0 18px 48px -32px rgba(16, 185, 129, 0.48),
    0 8px 26px -24px rgba(0, 0, 0, 0.28);
  backdrop-filter: blur(16px);
  transition:
    border-color 180ms ease,
    box-shadow 180ms ease,
    background-color 180ms ease;
}

.chat-composer:focus-within {
  border-color: rgba(16, 185, 129, 0.42);
  background: rgba(255, 255, 255, 0.96);
  box-shadow:
    0 0 0 4px rgba(16, 185, 129, 0.08),
    0 22px 54px -34px rgba(16, 185, 129, 0.56),
    0 8px 26px -24px rgba(0, 0, 0, 0.32);
}

.composer-source-controls {
  display: inline-flex;
  align-items: center;
  border-radius: 9999px;
  background: rgba(239, 244, 241, 0.72);
  padding: 0.25rem;
}

.composer-source-pill {
  display: inline-flex;
  min-height: 2rem;
  align-items: center;
  justify-content: center;
  border-radius: 9999px;
  padding: 0.35rem 1rem;
  color: #66756f;
  font-size: 0.875rem;
  font-weight: 650;
  line-height: 1;
  transition:
    background-color 160ms ease,
    color 160ms ease,
    box-shadow 160ms ease,
    transform 160ms ease;
}

.composer-source-pill:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.66);
  color: #2f3f38;
}

.composer-source-pill:active:not(:disabled) {
  transform: translateY(1px);
}

.composer-source-pill:focus-visible {
  outline: 2px solid rgba(16, 185, 129, 0.28);
  outline-offset: 2px;
}

.composer-source-pill:disabled {
  cursor: not-allowed;
  opacity: 0.62;
}

.composer-source-pill-active {
  background: #d8f3e8;
  color: #047857;
  box-shadow: inset 0 0 0 1px rgba(16, 185, 129, 0.08);
}

.composer-source-pill-active {
  background: #e8f7f0;
}

.conversation-jump-nav {
  position: absolute;
  top: 50%;
  right: 0.45rem;
  z-index: 20;
  display: flex;
  width: 2rem;
  max-height: min(70%, 34rem);
  transform: translateY(-50%);
  flex-direction: column;
  align-items: flex-end;
  overflow-y: auto;
  border-radius: 1.25rem;
  padding: 0.45rem 0.35rem;
  background: transparent;
  transition:
    width 160ms ease,
    background-color 160ms ease,
    box-shadow 160ms ease,
    border-color 160ms ease,
    padding 160ms ease;
}

.conversation-jump-nav:hover,
.conversation-jump-nav:focus-within {
  width: 14rem;
  border: 1px solid rgba(226, 237, 231, 0.78);
  background: rgba(255, 255, 255, 0.86);
  box-shadow: 0 18px 46px -34px rgba(30, 41, 37, 0.42);
  backdrop-filter: blur(14px);
}

.conversation-jump-item {
  display: flex;
  width: 100%;
  align-items: center;
  justify-content: flex-end;
  gap: 0.75rem;
  border-radius: 0.75rem;
  padding: 0.42rem 0.2rem;
  color: #8a9891;
  font-size: 0.875rem;
  line-height: 1.2;
  transition:
    color 140ms ease,
    background-color 140ms ease,
    padding 140ms ease;
}

.conversation-jump-nav:hover .conversation-jump-item,
.conversation-jump-nav:focus-within .conversation-jump-item {
  padding: 0.45rem 0.35rem 0.45rem 0.7rem;
}

.conversation-jump-item:hover {
  color: var(--text);
  background: rgba(16, 185, 129, 0.06);
}

.conversation-jump-item-active {
  color: var(--primary);
  font-weight: 600;
}

.conversation-jump-title {
  min-width: 0;
  flex: 1;
  overflow: hidden;
  text-align: right;
  text-overflow: ellipsis;
  white-space: nowrap;
  opacity: 0;
  transform: translateX(0.35rem);
  transition:
    opacity 140ms ease,
    transform 140ms ease;
}

.conversation-jump-nav:hover .conversation-jump-title,
.conversation-jump-nav:focus-within .conversation-jump-title {
  opacity: 1;
  transform: translateX(0);
}

.conversation-jump-marker {
  height: 0.2rem;
  width: 0.5rem;
  flex-shrink: 0;
  border-radius: 9999px;
  background: #d3ddd8;
  transition:
    width 140ms ease,
    background-color 140ms ease;
}

.conversation-jump-item-active .conversation-jump-marker {
  width: 0.95rem;
  background: var(--primary);
}

:global(.dark) .chat-composer {
  border-color: rgba(42, 53, 48, 0.86);
  background: rgba(30, 36, 33, 0.88);
}

:global(.dark) .chat-composer:focus-within {
  border-color: rgba(52, 211, 153, 0.36);
  background: rgba(30, 36, 33, 0.96);
}

:global(.dark) .composer-source-controls {
  background: rgba(18, 22, 20, 0.72);
}

:global(.dark) .composer-source-pill {
  color: #8ea099;
}

:global(.dark) .composer-source-pill:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.06);
  color: #d7e4df;
}

:global(.dark) .composer-source-pill-active {
  background: rgba(16, 185, 129, 0.16);
  color: #7dd3a8;
  box-shadow: inset 0 0 0 1px rgba(16, 185, 129, 0.16);
}

:global(.dark) .conversation-jump-nav:hover,
:global(.dark) .conversation-jump-nav:focus-within {
  border-color: rgba(42, 53, 48, 0.78);
  background: rgba(30, 36, 33, 0.82);
  box-shadow: 0 18px 46px -34px rgba(0, 0, 0, 0.7);
}

:global(.dark) .conversation-jump-marker {
  background: #3a4741;
}

:global(.dark) .markdown-body :deep(.table-scroll),
:global(.dark) .markdown-body :deep(table) {
  background: var(--bg-elevated);
}

:global(.dark) .markdown-body :deep(th) {
  background: var(--bg-secondary);
}

.markdown-body {
  font-size: 0.9375rem;
  line-height: 1.85;
}

.markdown-body :deep(p) {
  margin: 0 0 0.9rem;
}

.markdown-body :deep(p:last-child),
.markdown-body :deep(ul:last-child),
.markdown-body :deep(ol:last-child),
.markdown-body :deep(pre:last-child),
.markdown-body :deep(blockquote:last-child) {
  margin-bottom: 0;
}

.markdown-body :deep(h2),
.markdown-body :deep(h3),
.markdown-body :deep(h4),
.markdown-body :deep(h5) {
  margin: 1.1rem 0 0.45rem;
  color: var(--text);
  font-weight: 700;
  line-height: 1.4;
}

.markdown-body :deep(h2) {
  font-size: 1.125rem;
}

.markdown-body :deep(h3),
.markdown-body :deep(h4),
.markdown-body :deep(h5) {
  font-size: 1rem;
}

.markdown-body :deep(ul),
.markdown-body :deep(ol) {
  margin: 0.35rem 0 1rem 1.35rem;
  padding: 0;
}

.markdown-body :deep(ul) {
  list-style: disc;
}

.markdown-body :deep(ol) {
  list-style: decimal;
}

.markdown-body :deep(li) {
  margin: 0.25rem 0;
  padding-left: 0.2rem;
}

.markdown-body :deep(strong) {
  color: var(--text);
  font-weight: 700;
}

.markdown-body :deep(code) {
  border-radius: 0.35rem;
  background: var(--bg-secondary);
  padding: 0.1rem 0.35rem;
  color: var(--text);
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', monospace;
  font-size: 0.88em;
}

.markdown-body :deep(pre) {
  margin: 0.7rem 0 1rem;
  overflow-x: auto;
  border: 1px solid var(--border);
  border-radius: 0.75rem;
  background: var(--bg-secondary);
  padding: 0.9rem 1rem;
}

.markdown-body :deep(pre code) {
  display: block;
  background: transparent;
  padding: 0;
  white-space: pre;
}

.markdown-body :deep(blockquote) {
  margin: 0.7rem 0 1rem;
  border-left: 3px solid var(--primary);
  padding: 0.15rem 0 0.15rem 0.85rem;
  color: var(--text-secondary);
}

.markdown-body :deep(hr) {
  margin: 1.1rem 0;
  border: 0;
  border-top: 1px solid var(--border);
}

.markdown-body :deep(.table-scroll) {
  margin: 0.8rem 0 1.1rem;
  max-width: 100%;
  overflow-x: auto;
  border: 1px solid rgba(226, 237, 231, 0.72);
  border-radius: 0.75rem;
  background: #ffffff;
}

.markdown-body :deep(table) {
  width: 100%;
  min-width: 560px;
  border-collapse: collapse;
  background: #ffffff;
  font-size: 0.9rem;
  line-height: 1.65;
}

.markdown-body :deep(th),
.markdown-body :deep(td) {
  border-bottom: 1px solid rgba(226, 237, 231, 0.68);
  padding: 0.65rem 0.8rem;
  text-align: left;
  vertical-align: top;
}

.markdown-body :deep(th) {
  background: #f4f8f6;
  color: var(--text);
  font-weight: 700;
  white-space: nowrap;
}

.markdown-body :deep(tr:last-child td) {
  border-bottom: 0;
}

.markdown-body :deep(a) {
  color: var(--primary);
  text-decoration: underline;
  text-underline-offset: 0.18em;
}
</style>
