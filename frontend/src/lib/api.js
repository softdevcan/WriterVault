// src/lib/api.js - Extended from your existing code
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000'

class ApiClient {
  constructor() {
    this.baseURL = API_BASE_URL
    this.token = null
  }

  setToken(token) {
    this.token = token
  }

  // Get token for requests (enhanced to check localStorage as fallback)
  getAuthToken() {
    if (this.token) {
      return this.token
    }
    // Fallback to localStorage for browser environment
    if (typeof window !== 'undefined') {
      return localStorage.getItem('token')
    }
    return null
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`
    
    const headers = {
      'Content-Type': 'application/json',
      ...options.headers,
    }

    // Use getAuthToken() instead of direct this.token
    const token = this.getAuthToken()
    if (token) {
      headers.Authorization = `Bearer ${token}`
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

      // Handle no content responses (for DELETE operations)
      if (response.status === 204) {
        return null
      }

      return await response.json()
    } catch (error) {
      console.error('API Request failed:', error)
      throw error
    }
  }

  // =====================================
  // AUTH ENDPOINTS (Your existing code)
  // =====================================

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

  // =====================================
  // ARTICLE ENDPOINTS (Enhanced & Extended)
  // =====================================

  // Enhanced getArticles with advanced filtering
  async getArticles(params = {}) {
    const searchParams = new URLSearchParams()
    
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        searchParams.append(key, value)
      }
    })

    const queryString = searchParams.toString()
    const endpoint = `/api/v1/articles/${queryString ? `?${queryString}` : ''}`
    
    return this.request(endpoint)
  }

  // Enhanced createArticle
  async createArticle(articleData) {
    return this.request('/api/v1/articles/', {
      method: 'POST',
      body: JSON.stringify(articleData),
    })
  }

  // Enhanced getArticle
  async getArticle(id) {
    return this.request(`/api/v1/articles/${id}`)
  }

  // Get article by slug (new)
  async getArticleBySlug(slug) {
    return this.request(`/api/v1/articles/slug/${slug}`)
  }

  // Enhanced updateArticle
  async updateArticle(id, articleData) {
    return this.request(`/api/v1/articles/${id}`, {
      method: 'PUT',
      body: JSON.stringify(articleData),
    })
  }

  // Enhanced deleteArticle
  async deleteArticle(id) {
    return this.request(`/api/v1/articles/${id}`, {
      method: 'DELETE',
    })
  }

  // Update article status (new)
  async updateArticleStatus(articleId, status, scheduledAt = null) {
    return this.request(`/api/v1/articles/${articleId}/status`, {
      method: 'PATCH',
      body: JSON.stringify({
        status,
        ...(scheduledAt && { scheduled_at: scheduledAt }),
      }),
    })
  }

  // Get user's articles (new)
  async getUserArticles(userId, params = {}) {
    const searchParams = new URLSearchParams()
    
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        searchParams.append(key, value)
      }
    })

    const queryString = searchParams.toString()
    const endpoint = `/api/v1/articles/user/${userId}${queryString ? `?${queryString}` : ''}`
    
    return this.request(endpoint)
  }

  // Quick publish/unpublish actions (new)
  async publishArticle(articleId) {
    return this.request(`/api/v1/articles/${articleId}/publish`, {
      method: 'POST',
    })
  }

  async unpublishArticle(articleId) {
    return this.request(`/api/v1/articles/${articleId}/unpublish`, {
      method: 'POST',
    })
  }

  // =====================================
  // CATEGORY ENDPOINTS (New)
  // =====================================

  async getCategories(params = {}) {
    const searchParams = new URLSearchParams()
    
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        searchParams.append(key, value)
      }
    })

    const queryString = searchParams.toString()
    const endpoint = `/api/v1/categories/${queryString ? `?${queryString}` : ''}`
    
    return this.request(endpoint)
  }

  async getCategoryTree() {
    return this.request('/api/v1/categories/tree')
  }

  async getCategory(categoryId) {
    return this.request(`/api/v1/categories/${categoryId}`)
  }

  async getCategoryBySlug(slug) {
    return this.request(`/api/v1/categories/slug/${slug}`)
  }

  async createCategory(categoryData) {
    return this.request('/api/v1/categories/', {
      method: 'POST',
      body: JSON.stringify(categoryData),
    })
  }

  async updateCategory(categoryId, categoryData) {
    return this.request(`/api/v1/categories/${categoryId}`, {
      method: 'PUT',
      body: JSON.stringify(categoryData),
    })
  }

  async deleteCategory(categoryId) {
    return this.request(`/api/v1/categories/${categoryId}`, {
      method: 'DELETE',
    })
  }

  // =====================================
  // COLLECTION ENDPOINTS (New)
  // =====================================

  async getCollections(params = {}) {
    const searchParams = new URLSearchParams()
    
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        searchParams.append(key, value)
      }
    })

    const queryString = searchParams.toString()
    const endpoint = `/api/v1/collections/${queryString ? `?${queryString}` : ''}`
    
    return this.request(endpoint)
  }

  async getCollection(collectionId) {
    return this.request(`/api/v1/collections/${collectionId}`)
  }

  async getCollectionBySlug(slug) {
    return this.request(`/api/v1/collections/slug/${slug}`)
  }

  async createCollection(collectionData) {
    return this.request('/api/v1/collections/', {
      method: 'POST',
      body: JSON.stringify(collectionData),
    })
  }

  async updateCollection(collectionId, collectionData) {
    return this.request(`/api/v1/collections/${collectionId}`, {
      method: 'PUT',
      body: JSON.stringify(collectionData),
    })
  }

  async deleteCollection(collectionId) {
    return this.request(`/api/v1/collections/${collectionId}`, {
      method: 'DELETE',
    })
  }

  async getUserCollections(userId, params = {}) {
    const searchParams = new URLSearchParams()
    
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        searchParams.append(key, value)
      }
    })

    const queryString = searchParams.toString()
    const endpoint = `/api/v1/collections/user/${userId}${queryString ? `?${queryString}` : ''}`
    
    return this.request(endpoint)
  }

  async publishCollection(collectionId) {
    return this.request(`/api/v1/collections/${collectionId}/publish`, {
      method: 'POST',
    })
  }

  // =====================================
  // EXPORT ENDPOINTS (Future)
  // =====================================

  // Export article to different formats
  async exportArticle(articleId, format = 'pdf') {
    const response = await fetch(`${this.baseURL}/api/v1/articles/${articleId}/export/${format}`, {
      headers: {
        'Authorization': `Bearer ${this.getAuthToken()}`,
      },
    })

    if (!response.ok) {
      throw new Error(`Export failed: ${response.statusText}`)
    }

    // Return blob for download
    return await response.blob()
  }

  // =====================================
  // UTILITY METHODS
  // =====================================

  // Health check
  async healthCheck() {
    return this.request('/health')
  }

  // API info
  async getApiInfo() {
    return this.request('/api/v1/info')
  }
}

// Create and export singleton instance (keeping your pattern)
export const apiClient = new ApiClient()

// Also export the class for potential future use
export { ApiClient }

// Default export for convenience
export default apiClient

// React Query helper functions (new addition)
export const articleQueryKeys = {
  all: ['articles'],
  lists: () => [...articleQueryKeys.all, 'list'],
  list: (filters) => [...articleQueryKeys.lists(), { filters }],
  details: () => [...articleQueryKeys.all, 'detail'],
  detail: (id) => [...articleQueryKeys.details(), id],
  user: (userId) => [...articleQueryKeys.all, 'user', userId],
}

export const categoryQueryKeys = {
  all: ['categories'],
  lists: () => [...categoryQueryKeys.all, 'list'],
  tree: () => [...categoryQueryKeys.all, 'tree'],
  detail: (id) => [...categoryQueryKeys.all, 'detail', id],
}

export const collectionQueryKeys = {
  all: ['collections'],
  lists: () => [...collectionQueryKeys.all, 'list'],
  detail: (id) => [...collectionQueryKeys.all, 'detail', id],
  user: (userId) => [...collectionQueryKeys.all, 'user', userId],
}