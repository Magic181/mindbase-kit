import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { documentApi, type Document } from '@/api/document'
import { useDocumentStore } from './document'

vi.mock('@/api/document', () => ({
  documentApi: {
    list: vi.fn(),
    upload: vi.fn(),
    get: vi.fn(),
    delete: vi.fn(),
    reparse: vi.fn(),
  },
}))

function makeDocument(overrides: Partial<Document> = {}): Document {
  return {
    id: 1,
    notebook_id: 1,
    name: 'file.txt',
    file_type: 'txt',
    file_size: 100,
    status: 'completed',
    chunk_count: 1,
    asset_count: 0,
    ocr_count: 0,
    ocr_pending_count: 0,
    ocr_failed_count: 0,
    ocr_skipped_count: 0,
    vision_count: 0,
    vision_pending_count: 0,
    vision_failed_count: 0,
    vision_skipped_count: 0,
    created_at: '2026-01-01T00:00:00Z',
    updated_at: '2026-01-01T00:00:00Z',
    ...overrides,
  }
}

describe('useDocumentStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  it('fetchDocuments populates the list and toggles loading', async () => {
    const docs = [makeDocument()]
    vi.mocked(documentApi.list).mockResolvedValue({ data: docs } as never)

    const store = useDocumentStore()
    const promise = store.fetchDocuments(1)
    expect(store.loading).toBe(true)
    await promise
    expect(store.loading).toBe(false)
    expect(store.documents).toEqual(docs)
  })

  it('starts polling when a document is still parsing and stops once completed', async () => {
    vi.mocked(documentApi.list)
      .mockResolvedValueOnce({ data: [makeDocument({ status: 'parsing' })] } as never)
      .mockResolvedValueOnce({ data: [makeDocument({ status: 'completed' })] } as never)

    const store = useDocumentStore()
    await store.fetchDocuments(1)
    expect(store.documents[0].status).toBe('parsing')
    expect(documentApi.list).toHaveBeenCalledTimes(1)

    await vi.advanceTimersByTimeAsync(3000)
    expect(documentApi.list).toHaveBeenCalledTimes(2)
    expect(store.documents[0].status).toBe('completed')

    await vi.advanceTimersByTimeAsync(3000)
    expect(documentApi.list).toHaveBeenCalledTimes(2)
  })

  it('deleteDocument removes the document from the list', async () => {
    vi.mocked(documentApi.delete).mockResolvedValue({} as never)

    const store = useDocumentStore()
    store.documents = [makeDocument({ id: 9 })]
    await store.deleteDocument(9)
    expect(store.documents).toEqual([])
  })

  it('reset clears documents and stops any active polling', async () => {
    vi.mocked(documentApi.list).mockResolvedValue({
      data: [makeDocument({ status: 'parsing' })],
    } as never)

    const store = useDocumentStore()
    await store.fetchDocuments(1)
    store.reset()
    expect(store.documents).toEqual([])

    await vi.advanceTimersByTimeAsync(6000)
    expect(documentApi.list).toHaveBeenCalledTimes(1)
  })
})
