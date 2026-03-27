import api from './api'

export interface User {
  id: string
  username: string
  email: string
}

export interface LoginData {
  username: string
  password: string
}

export interface RegisterData {
  username: string
  email: string
  password: string
}

export interface Token {
  access_token: string
  token_type: string
}

export const authService = {
  async login(data: LoginData): Promise<Token> {
    const response = await api.post<Token>('/api/auth/login', data)
    localStorage.setItem('token', response.data.access_token)
    return response.data
  },

  async register(data: RegisterData): Promise<User> {
    const response = await api.post<User>('/api/auth/register', data)
    return response.data
  },

  async getCurrentUser(): Promise<User> {
    const response = await api.get<User>('/api/auth/me')
    return response.data
  },

  logout(): void {
    localStorage.removeItem('token')
  },

  getToken(): string | null {
    return localStorage.getItem('token')
  },

  isAuthenticated(): boolean {
    return !!this.getToken()
  },
}