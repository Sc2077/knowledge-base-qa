import api from './api'

export interface KnowledgeBase {
  id: string
  user_id: string
  name: string
  description: string
  collection_name: string
  created_at: string
  updated_at: string
}

export interface CreateKnowledgeBaseData {
  name: string
  description?: string
}

export const knowledgeBaseService = {
  async list(): Promise<KnowledgeBase[]> {
    const response = await api.get<KnowledgeBase[]>('/api/knowledge-bases')
    return response.data
  },

  async get(id: string): Promise<KnowledgeBase> {
    const response = await api.get<KnowledgeBase>(`/api/knowledge-bases/${id}`)
    return response.data
  },

  async create(data: CreateKnowledgeBaseData): Promise<KnowledgeBase> {
    const response = await api.post<KnowledgeBase>('/api/knowledge-bases', data)
    return response.data
  },

  async update(id: string, data: Partial<CreateKnowledgeBaseData>): Promise<KnowledgeBase> {
    const response = await api.put<KnowledgeBase>(`/api/knowledge-bases/${id}`, data)
    return response.data
  },

  async delete(id: string): Promise<void> {
    await api.delete(`/api/knowledge-bases/${id}`)
  },
}