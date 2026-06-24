<template>
  <div class="flex h-screen bg-[var(--bg)]">
    <aside class="w-64 border-r border-[var(--border)] bg-[var(--bg-secondary)] flex flex-col">
      <div class="p-4 border-b border-[var(--border)]">
        <h1 class="text-lg font-semibold text-[var(--primary)]">AI Notebook</h1>
      </div>
      <div class="flex-1 p-4 overflow-y-auto">
        <p class="text-sm text-[var(--text-secondary)]">Chat History</p>
      </div>
    </aside>
    <main class="flex-1 flex flex-col">
      <header class="h-14 border-b border-[var(--border)] flex items-center px-6">
        <h2 class="font-medium text-[var(--text)]">Chat</h2>
      </header>
      <div class="flex-1 p-6 overflow-y-auto">
        <p class="text-[var(--text-secondary)]">Start a conversation about your documents.</p>
      </div>
      <div class="p-4 border-t border-[var(--border)]">
        <input
          v-model="input"
          type="text"
          placeholder="Ask a question..."
          class="w-full px-4 py-3 rounded-xl border border-[var(--border)] bg-[var(--bg)] text-[var(--text)] outline-none focus:border-[var(--primary)]"
          @keyup.enter="sendMessage"
        />
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useChatStore } from '@/stores/chat'

const chatStore = useChatStore()
const input = ref('')

function sendMessage() {
  if (!input.value.trim()) return
  chatStore.addMessage({
    id: Date.now().toString(),
    role: 'user',
    content: input.value,
    created_at: new Date().toISOString(),
  })
  input.value = ''
}
</script>