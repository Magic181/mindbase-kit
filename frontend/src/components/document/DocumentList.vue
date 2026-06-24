<template>
  <div v-if="loading" class="py-10 text-center text-sm text-[var(--text-secondary)]">
    加载文档中...
  </div>

  <div v-else-if="documents.length === 0" class="py-6 text-center text-sm text-[var(--text-secondary)]">
    暂无文档，上传第一个文件开始构建知识库
  </div>

  <div v-else class="space-y-3">
    <div
      v-for="doc in documents"
      :key="doc.id"
      class="flex items-center gap-4 rounded-2xl border border-[var(--border)] bg-[var(--bg)] px-4 py-3"
    >
      <div class="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-[var(--bg-secondary)] text-lg">
        {{ fileIcon(doc.file_type) }}
      </div>

      <div class="min-w-0 flex-1">
        <p class="truncate font-medium text-[var(--text)]">{{ doc.name }}</p>
        <p class="mt-1 text-xs text-[var(--text-secondary)]">
          {{ formatSize(doc.file_size) }}
          <span v-if="doc.chunk_count > 0"> · {{ doc.chunk_count }} 个片段</span>
        </p>
        <p v-if="doc.status === 'failed' && doc.error_message" class="mt-1 text-xs text-red-500">
          {{ doc.error_message }}
        </p>
      </div>

      <span
        class="shrink-0 rounded-full px-3 py-1 text-xs font-medium"
        :class="statusClass(doc.status)"
      >
        {{ statusLabel(doc.status) }}
      </span>

      <button
        class="shrink-0 rounded-lg px-3 py-1.5 text-sm text-red-500 hover:bg-red-50 dark:hover:bg-red-950/30"
        @click="$emit('delete', doc)"
      >
        删除
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Document, DocumentStatus } from '@/api/document'

defineProps<{
  documents: Document[]
  loading?: boolean
}>()

defineEmits<{
  delete: [document: Document]
}>()

function fileIcon(type: string) {
  const icons: Record<string, string> = {
    pdf: '📕',
    docx: '📘',
    md: '📝',
    txt: '📄',
  }
  return icons[type] || '📎'
}

function formatSize(bytes: number) {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

function statusLabel(status: DocumentStatus) {
  const labels: Record<DocumentStatus, string> = {
    uploading: '上传中',
    parsing: '解析中',
    completed: '已完成',
    failed: '失败',
  }
  return labels[status]
}

function statusClass(status: DocumentStatus) {
  const classes: Record<DocumentStatus, string> = {
    uploading: 'bg-blue-500/10 text-blue-600',
    parsing: 'bg-amber-500/10 text-amber-600',
    completed: 'bg-green-500/10 text-green-600',
    failed: 'bg-red-500/10 text-red-500',
  }
  return classes[status]
}
</script>
