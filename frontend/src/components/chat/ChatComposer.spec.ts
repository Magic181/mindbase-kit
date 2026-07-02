import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import ChatComposer from './ChatComposer.vue'

function mountComposer(overrides = {}) {
  return mount(ChatComposer, {
    props: {
      modelValue: 'Question',
      webSearchEnabled: false,
      sending: false,
      sendFailed: false,
      canStopGeneration: false,
      activeConversationId: 10,
      ...overrides,
    },
  })
}

describe('ChatComposer', () => {
  it('emits input, web search toggle and send events', async () => {
    const wrapper = mountComposer()

    await wrapper.find('input').setValue('Next question')
    await wrapper.find('.composer-source-pill').trigger('click')
    await wrapper.find('form').trigger('submit')

    expect(wrapper.emitted('update:modelValue')?.[0]).toEqual(['Next question'])
    expect(wrapper.emitted('update:webSearchEnabled')?.[0]).toEqual([true])
    expect(wrapper.emitted('send')).toHaveLength(1)
  })

  it('emits stop while generation can be stopped', async () => {
    const wrapper = mountComposer({
      sending: true,
      canStopGeneration: true,
    })

    await wrapper.find('[aria-label="停止生成"]').trigger('click')

    expect(wrapper.emitted('stop')).toHaveLength(1)
    expect(wrapper.find('[aria-label="发送"]').exists()).toBe(false)
  })

  it('disables send while input is blank or chat is unavailable', () => {
    const blank = mountComposer({ modelValue: '   ' })
    const unavailable = mountComposer({ activeConversationId: null })

    expect(blank.find('button[type="submit"]').attributes('disabled')).toBeDefined()
    expect(unavailable.find('button[type="submit"]').attributes('disabled')).toBeDefined()
  })

  it('renders send failure state and emits send from retry button', async () => {
    const wrapper = mountComposer({ sendFailed: true })

    expect(wrapper.text()).toContain('发送失败')
    await wrapper.find('.composer-retry-btn').trigger('click')

    expect(wrapper.emitted('send')).toHaveLength(1)
  })
})
