export interface User {
  id: number
  username: string
  email: string
  avatar?: string
}

export interface Notebook {
  id: number
  name: string
  description: string
  created_at: string
  updated_at: string
  is_favorite: boolean
  tags: Tag[]
  document_count: number
}

export interface Document {
  id: number
  notebook_id: number
  name: string
  file_type: string
  file_size: number
  status: 'uploading' | 'parsing' | 'vectorizing' | 'completed' | 'failed'
  chunk_count: number
  created_at: string
}

export interface DocumentChunk {
  id: number
  document_id: number
  content: string
  page?: number
  chapter?: string
  metadata: Record<string, any>
}

export interface Tag {
  id: number
  name: string
  color: string
}