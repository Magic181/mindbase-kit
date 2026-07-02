import { mount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'
import type { Message } from '@/api/chat'
import MessageList from './MessageList.vue'

function makeMessage(overrides: Partial<Message> = {}): Message {
  return {
    id: 1,
    conversation_id: 10,
    role: 'assistant',
    content: '1. Follow up',
    citations: [],
    created_at: '2026-01-01T00:00:00Z',
    ...overrides,
  }
}

function mountList(overrides = {}) {
  return mount(MessageList, {
    props: {
      messages: [],
      loading: false,
      emptyStateHint: 'Empty hint',
      sending: false,
      streamingAssistantId: null,
      setMessageElement: vi.fn(),
      ...overrides,
    },
    global: {
      stubs: {
        CitationList: true,
      },
    },
  })
}

describe('MessageList', () => {
  it('renders loading and empty states', () => {
    expect(mountList({ loading: true }).text()).toContain('加载中')
    expect(mountList().text()).toContain('Empty hint')
  })

  it('emits action text when an assistant action item is clicked', async () => {
    const wrapper = mountList({
      messages: [makeMessage()],
    })

    await wrapper.find('.ai-action-item').trigger('click')

    expect(wrapper.emitted('action')?.[0]).toEqual(['Follow up'])
  })

  it('renders a pending assistant indicator when sending without a streaming message', () => {
    const wrapper = mountList({
      messages: [makeMessage({ role: 'user', content: 'Question' })],
      sending: true,
    })

    expect(wrapper.findAll('.animate-bounce')).toHaveLength(3)
  })
})
