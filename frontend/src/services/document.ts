import api from './api'

export interface Document {
  id: string
  knowledge_base_id: string
  filename: string
  file_type: string
  file_size: number
  chunk_count: number
  status: string
  error_message: string
  created_at: string
  updated_at: string
}

export const documentService = {
  async upload(knowledgeBaseId: string, file: File): Promise<Document> {
    const formData = new FormData()
    formData.append('knowledge_base_id', knowledgeBaseId)
    formData.append('file', file)
    
    const response = await api.post<Document>('/api/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },

  async list(knowledgeBaseId: string): Promise<Document[]> {
    const response = await api.get<Document[]>('/api/documents', {
      params: { knowledge_base_id: knowledgeBaseId },
    })
    return response.data
  },

  async delete(id: string): Promise<void> {
    await api.delete(`/api/documents/${id}`)
  },
}