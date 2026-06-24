<template>
  <div class="flex h-screen bg-[var(--bg)]">
    <aside class="w-64 border-r border-[var(--border)] bg-[var(--bg-secondary)] flex flex-col">
      <div class="p-4 border-b border-[var(--border)]">
        <h1 class="text-lg font-semibold text-[var(--primary)]">AI Notebook</h1>
      </div>
      <div class="flex-1 p-4 overflow-y-auto">
        <p class="text-sm text-[var(--text-secondary)]">Notebook</p>
      </div>
    </aside>
    <main class="flex-1 flex flex-col">
      <header class="h-14 border-b border-[var(--border)] flex items-center px-6">
        <h2 class="font-medium text-[var(--text)]">{{ notebook?.name || 'Notebook' }}</h2>
      </header>
      <div class="flex-1 p-6 overflow-y-auto">
        <p class="text-[var(--text-secondary)]">Documents and chat will appear here.</p>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useNotebookStore } from '@/stores/notebook'

const route = useRoute()
const notebookStore = useNotebookStore()
const notebook = notebookStore.currentNotebook

onMounted(() => {
  const id = Number(route.params.id)
  if (id) notebookStore.fetchNotebook(id)
})
</script>