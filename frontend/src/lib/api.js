const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

class ApiClient {
  constructor() {
    this.baseURL = API_BASE_URL
    this.token = null
  }

  setToken(token) {
    this.token = token
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`
    
    const headers = {
      'Content-Type': 'application/json',
      ...options.headers,
    }

    if (this.token) {
      headers.Authorization = `Bearer ${this.token}`
    }

    try {
      const response = await fetch(url, {
        ...options,
        headers,
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.detail || `HTTP Error: ${response.status}`)
      }

      return await response.json()
    } catch (error) {
      console.error('API Request failed:', error)
      throw error
    }
  }

  // Auth endpoints
  async login(credentials) {
    const formData = new URLSearchParams()
    formData.append('username', credentials.username)
    formData.append('password', credentials.password)

    return this.request('/api/v1/auth/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: formData,
    })
  }

  async register(userData) {
    return this.request('/api/v1/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData),
    })
  }

  async getCurrentUser() {
    return this.request('/api/v1/auth/me')
  }

  async logout() {
    return this.request('/api/v1/auth/logout', {
      method: 'POST',
    })
  }

  async validateToken() {
    return this.request('/api/v1/auth/validate-token')
  }

  async requestPasswordReset(email) {
    return this.request('/api/v1/auth/request-password-reset', {
      method: 'POST',
      body: JSON.stringify({ email }),
    })
  }

  async resetPassword(token, newPassword) {
    return this.request('/api/v1/auth/reset-password', {
      method: 'POST',
      body: JSON.stringify({ token, new_password: newPassword }),
    })
  }

  async verifyResetToken(token) {
    return this.request(`/api/v1/auth/verify-reset-token?token=${token}`, {
      method: 'POST',
    })
  }

  // Future: Article endpoints
  async getArticles(params = {}) {
    const queryString = new URLSearchParams(params).toString()
    return this.request(`/api/v1/articles${queryString ? `?${queryString}` : ''}`)
  }

  async createArticle(articleData) {
    return this.request('/api/v1/articles', {
      method: 'POST',
      body: JSON.stringify(articleData),
    })
  }

  async getArticle(id) {
    return this.request(`/api/v1/articles/${id}`)
  }

  async updateArticle(id, articleData) {
    return this.request(`/api/v1/articles/${id}`, {
      method: 'PUT',
      body: JSON.stringify(articleData),
    })
  }

  async deleteArticle(id) {
    return this.request(`/api/v1/articles/${id}`, {
      method: 'DELETE',
    })
  }
}

export const apiClient = new ApiClient()