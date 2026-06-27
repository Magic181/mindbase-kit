import { defineStore } from 'pinia'
import { ref } from 'vue'
import { documentApi, type Document } from '@/api/document'

const POLL_INTERVAL_MS = 3000
const ACTIVE_STATUSES = new Set(['uploading', 'parsing'])

export const useDocumentStore = defineStore('document', () => {
  const documents = ref<Document[]>([])
  const loading = ref(false)
  const uploading = ref(false)
  let pollTimer: ReturnType<typeof setInterval> | null = null

  function hasActiveDocuments() {
    return documents.value.some((doc) => ACTIVE_STATUSES.has(doc.status))
  }

  function stopPolling() {
    if (pollTimer) {
      clearInterval(pollTimer)
      pollTimer = null
    }
  }

  function startPolling(notebookId: number) {
    stopPolling()
    if (!hasActiveDocuments()) return

    pollTimer = setInterval(async () => {
      try {
        await fetchDocuments(notebookId, { silent: true })
        if (!hasActiveDocuments()) {
          stopPolling()
        }
      } catch {
        stopPolling()
      }
    }, POLL_INTERVAL_MS)
  }

  async function fetchDocuments(
    notebookId: number,
    options: { silent?: boolean } = {},
  ) {
    if (!options.silent) {
      loading.value = true
    }
    try {
      const { data } = await documentApi.list(notebookId)
      documents.value = data
      if (hasActiveDocuments()) {
        startPolling(notebookId)
      }
    } finally {
      if (!options.silent) {
        loading.value = false
      }
    }
  }

  async function uploadDocuments(notebookId: number, files: File[]) {
    uploading.value = true
    try {
      const { data } = await documentApi.upload(notebookId, files)
      documents.value = [...data, ...documents.value]
      startPolling(notebookId)
      return data
    } finally {
      uploading.value = false
    }
  }

  async function deleteDocument(id: number) {
    await documentApi.delete(id)
    documents.value = documents.value.filter((doc) => doc.id !== id)
  }

  async function reparseDocument(notebookId: number, id: number) {
    const { data } = await documentApi.reparse(id)
    documents.value = documents.value.map((doc) => (doc.id === id ? data : doc))
    startPolling(notebookId)
    return data
  }

  function reset() {
    stopPolling()
    documents.value = []
  }

  return {
    documents,
    loading,
    uploading,
    fetchDocuments,
    uploadDocuments,
    deleteDocument,
    reparseDocument,
    reset,
  }
})
