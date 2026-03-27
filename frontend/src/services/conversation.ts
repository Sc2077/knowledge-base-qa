import api from './api'

export interface Conversation {
  id: string
  user_id: string
  knowledge_base_id: string | null
  title: string
  created_at: string
  updated_at: string
}

export interface Message {
  id: string
  conversation_id: string
  role: 'user' | 'assistant'
  content: string
  created_at: string
}

export interface CreateConversationData {
  title: string
  knowledge_base_id?: string
}

export const conversationService = {
  async list(): Promise<Conversation[]> {
    const response = await api.get<Conversation[]>('/api/conversations')
    return response.data
  },

  async get(id: string): Promise<Conversation> {
    const response = await api.get<Conversation>(`/api/conversations/${id}`)
    return response.data
  },

  async create(data: CreateConversationData): Promise<Conversation> {
    const response = await api.post<Conversation>('/api/conversations', data)
    return response.data
  },

  async delete(id: string): Promise<void> {
    await api.delete(`/api/conversations/${id}`)
  },

  async getMessages(id: string): Promise<Message[]> {
    const response = await api.get<Message[]>(`/api/conversations/${id}/messages`)
    return response.data
  },

  async chat(conversationId: string, question: string, knowledgeBaseId?: string): Promise<ReadableStream> {
    const response = await fetch(`${api.defaults.baseURL}/api/conversations/${conversationId}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`,
      },
      body: JSON.stringify({
        question,
        knowledge_base_id: knowledgeBaseId,
      }),
    })
    return response.body!
  },
}