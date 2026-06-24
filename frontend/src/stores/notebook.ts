import { defineStore } from 'pinia'
import { ref } from 'vue'
import { notebookApi, type Notebook } from '@/api/notebook'

export const useNotebookStore = defineStore('notebook', () => {
  const notebooks = ref<Notebook[]>([])
  const currentNotebook = ref<Notebook | null>(null)
  const loading = ref(false)

  async function fetchNotebooks() {
    loading.value = true
    try {
      const { data } = await notebookApi.list()
      notebooks.value = data
    } finally {
      loading.value = false
    }
  }

  async function fetchNotebook(id: number) {
    const { data } = await notebookApi.get(id)
    currentNotebook.value = data
  }

  return { notebooks, currentNotebook, loading, fetchNotebooks, fetchNotebook }
})