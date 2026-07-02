import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { notebookApi, type Notebook } from '@/api/notebook'
import { useNotebookStore } from './notebook'

vi.mock('@/api/notebook', () => ({
  notebookApi: {
    list: vi.fn(),
    get: vi.fn(),
    create: vi.fn(),
    update: vi.fn(),
    delete: vi.fn(),
    toggleFavorite: vi.fn(),
  },
}))

function makeNotebook(overrides: Partial<Notebook> = {}): Notebook {
  return {
    id: 1,
    name: 'Test Notebook',
    description: '',
    created_at: '2026-01-01T00:00:00Z',
    updated_at: '2026-01-01T00:00:00Z',
    is_favorite: false,
    ...overrides,
  }
}

describe('useNotebookStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('fetchNotebooks populates the list and toggles loading', async () => {
    const notebooks = [makeNotebook()]
    vi.mocked(notebookApi.list).mockResolvedValue({
      data: { items: notebooks, total: 1, page: 1, page_size: 20 },
    } as never)

    const store = useNotebookStore()
    const promise = store.fetchNotebooks()
    expect(store.loading).toBe(true)
    await promise
    expect(store.loading).toBe(false)
    expect(store.notebooks).toEqual(notebooks)
    expect(store.total).toBe(1)
  })

  it('fetchNotebooks resets loading even when the request fails', async () => {
    vi.mocked(notebookApi.list).mockRejectedValue(new Error('network error'))

    const store = useNotebookStore()
    await expect(store.fetchNotebooks()).rejects.toThrow('network error')
    expect(store.loading).toBe(false)
  })

  it('createNotebook prepends the new notebook and increments total', async () => {
    const created = makeNotebook({ id: 2, name: 'New Notebook' })
    vi.mocked(notebookApi.create).mockResolvedValue({ data: created } as never)

    const store = useNotebookStore()
    store.notebooks = [makeNotebook({ id: 1 })]
    store.total = 1

    const result = await store.createNotebook({ name: 'New Notebook' })
    expect(result).toEqual(created)
    expect(store.notebooks[0]).toEqual(created)
    expect(store.total).toBe(2)
  })

  it('deleteNotebook removes the notebook from the list and clears currentNotebook if active', async () => {
    vi.mocked(notebookApi.delete).mockResolvedValue({} as never)

    const store = useNotebookStore()
    const notebook = makeNotebook({ id: 5 })
    store.notebooks = [notebook]
    store.currentNotebook = notebook
    store.total = 1

    await store.deleteNotebook(5)
    expect(store.notebooks).toEqual([])
    expect(store.currentNotebook).toBeNull()
    expect(store.total).toBe(0)
  })

  it('toggleFavorite removes the notebook from the list when the favorite filter is active and it becomes unfavorited', async () => {
    const notebook = makeNotebook({ id: 3, is_favorite: false })
    vi.mocked(notebookApi.toggleFavorite).mockResolvedValue({ data: notebook } as never)

    const store = useNotebookStore()
    store.notebooks = [notebook]
    store.total = 1
    store.filters = { is_favorite: true }

    await store.toggleFavorite(3)
    expect(store.notebooks).toEqual([])
    expect(store.total).toBe(0)
  })
})
