<template>
  <div v-if="loading" class="py-10 text-center text-sm text-content-secondary">
    加载文档中...
  </div>

  <div v-else-if="documents.length === 0" class="py-6 text-center text-sm text-content-secondary">
    暂无文档，上传第一个文件开始构建知识库
  </div>

  <div v-else class="space-y-3">
    <div
      v-for="doc in documents"
      :key="doc.id"
      class="flex flex-col gap-3 rounded-glg border border-line bg-surface-elevated px-4 py-3 shadow-gsm sm:flex-row sm:items-center"
    >
      <div class="flex min-w-0 flex-1 items-start gap-3">
        <div class="flex h-10 w-10 shrink-0 items-center justify-center rounded-gmd bg-primary-soft text-xs font-bold uppercase text-primary">
          {{ fileBadge(doc.file_type) }}
        </div>

        <div class="min-w-0 flex-1">
          <p class="break-words font-medium text-content">{{ doc.name }}</p>
          <p class="mt-1 text-xs text-content-secondary">
            {{ formatSize(doc.file_size) }}
            <span v-if="doc.chunk_count > 0"> · {{ doc.chunk_count }} 个片段</span>
            <span v-if="doc.asset_count > 0"> · {{ doc.asset_count }} 张图片</span>
          </p>
          <div v-if="processingBadges(doc).length" class="mt-2 flex flex-wrap gap-1.5">
            <span
              v-for="badge in processingBadges(doc)"
              :key="badge.label"
              class="rounded-pill border px-2 py-0.5 text-[11px]"
              :class="badge.className"
            >
              {{ badge.label }}
            </span>
          </div>
          <p
            v-if="processingIssueText(doc)"
            class="mt-1 break-words text-xs text-amber-600"
          >
            {{ processingIssueText(doc) }}
          </p>
          <p v-if="doc.status === 'failed' && doc.error_message" class="mt-1 break-words text-xs text-red-500">
            {{ doc.error_message }}
          </p>
        </div>
      </div>

      <div class="flex shrink-0 items-center justify-between gap-3 sm:justify-end">
        <span
          class="rounded-pill px-3 py-1 text-xs font-medium"
          :class="statusClass(doc.status)"
        >
          {{ statusLabel(doc.status) }}
        </span>

        <button
          :disabled="isReparseDisabled(doc)"
          class="gemini-btn gemini-btn-ghost gemini-btn-sm"
          @click="$emit('reparse', doc)"
        >
          {{ isReparsing(doc.id) ? '入队中...' : '重新解析' }}
        </button>

        <button
          class="gemini-btn gemini-btn-danger gemini-btn-sm"
          @click="$emit('delete', doc)"
        >
          删除
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Document, DocumentStatus } from '@/api/document'

const props = defineProps<{
  documents: Document[]
  loading?: boolean
  reparsingIds?: number[]
}>()

defineEmits<{
  delete: [document: Document]
  reparse: [document: Document]
}>()

function fileBadge(type: string) {
  const badges: Record<string, string> = {
    pdf: 'PDF',
    docx: 'DOC',
    md: 'MD',
    txt: 'TXT',
  }
  return badges[type] || 'FILE'
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

function processingBadges(document: Document) {
  const badges: Array<{ label: string; className: string }> = []
  addCountBadge(badges, document.ocr_count, 'OCR 成功', 'success')
  addCountBadge(badges, document.ocr_pending_count, 'OCR 待处理', 'pending')
  addCountBadge(badges, document.ocr_skipped_count, 'OCR 跳过', 'muted')
  addCountBadge(badges, document.ocr_failed_count, 'OCR 失败', 'danger')
  addCountBadge(badges, document.vision_count, '视觉成功', 'success')
  addCountBadge(badges, document.vision_pending_count, '视觉待处理', 'pending')
  addCountBadge(badges, document.vision_skipped_count, '视觉跳过', 'muted')
  addCountBadge(badges, document.vision_failed_count, '视觉失败', 'danger')
  return badges
}

function addCountBadge(
  badges: Array<{ label: string; className: string }>,
  count: number | undefined,
  label: string,
  tone: 'success' | 'pending' | 'muted' | 'danger',
) {
  if (!count) return
  badges.push({
    label: `${label} ${count}`,
    className: processingBadgeClass(tone),
  })
}

function processingBadgeClass(tone: 'success' | 'pending' | 'muted' | 'danger') {
  const classes = {
    success: 'border-green-500/20 bg-green-500/10 text-green-600',
    pending: 'border-amber-500/20 bg-amber-500/10 text-amber-600',
    muted: 'border-[var(--border)] bg-[var(--bg-secondary)] text-[var(--text-secondary)]',
    danger: 'border-red-500/20 bg-red-500/10 text-red-500',
  }
  return classes[tone]
}

function processingIssueText(document: Document) {
  if (document.vision_error_message) return `视觉：${document.vision_error_message}`
  if (document.ocr_error_message) return `OCR：${document.ocr_error_message}`
  return ''
}

function isActiveStatus(status: DocumentStatus) {
  return status === 'uploading' || status === 'parsing'
}

function isReparsing(documentId: number) {
  return Boolean(props.reparsingIds?.includes(documentId))
}

function isReparseDisabled(document: Document) {
  return isActiveStatus(document.status) || isReparsing(document.id)
}
</script>
