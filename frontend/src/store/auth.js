import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { apiClient } from '../lib/api'

const useAuthStore = create(
  persist(
    (set, get) => ({
      // State
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      // Actions
      setUser: (user) => set({ user, isAuthenticated: !!user }),
      
      setToken: (token) => {
        set({ token })
        apiClient.setToken(token)
      },

      setLoading: (isLoading) => set({ isLoading }),
      
      setError: (error) => set({ error }),

      clearError: () => set({ error: null }),

      // Login
      login: async (credentials) => {
        set({ isLoading: true, error: null })
        
        try {
          const response = await apiClient.login(credentials)
          const { access_token } = response
          
          // Set token
          get().setToken(access_token)
          
          // Get user info
          const user = await apiClient.getCurrentUser()
          get().setUser(user)
          
          set({ isLoading: false })
          return { success: true }
        } catch (error) {
          set({ isLoading: false, error: error.message })
          return { success: false, error: error.message }
        }
      },

      // Register
      register: async (userData) => {
        set({ isLoading: true, error: null })
        
        try {
          const user = await apiClient.register(userData)
          set({ isLoading: false })
          return { success: true, user }
        } catch (error) {
          set({ isLoading: false, error: error.message })
          return { success: false, error: error.message }
        }
      },

      // Logout
      logout: () => {
        set({
          user: null,
          token: null,
          isAuthenticated: false,
          error: null,
        })
        apiClient.setToken(null)
        
        // Call logout endpoint (for logging purposes)
        apiClient.logout().catch(() => {
          // Ignore errors on logout
        })
      },

      // Password Reset Request
      requestPasswordReset: async (email) => {
        set({ isLoading: true, error: null })
        
        try {
          const response = await apiClient.requestPasswordReset(email)
          set({ isLoading: false })
          return { success: true, message: response.message }
        } catch (error) {
          set({ isLoading: false, error: error.message })
          return { success: false, error: error.message }
        }
      },

      // Password Reset
      resetPassword: async (token, newPassword) => {
        set({ isLoading: true, error: null })
        
        try {
          const response = await apiClient.resetPassword(token, newPassword)
          set({ isLoading: false })
          return { success: true, message: response.message }
        } catch (error) {
          set({ isLoading: false, error: error.message })
          return { success: false, error: error.message }
        }
      },

      // Verify Reset Token
      verifyResetToken: async (token) => {
        set({ isLoading: true, error: null })
        
        try {
          await apiClient.verifyResetToken(token)
          set({ isLoading: false })
          return { success: true }
        } catch (error) {
          set({ isLoading: false, error: error.message })
          return { success: false, error: error.message }
        }
      },

      // Initialize auth state
      initialize: async () => {
        const { token } = get()
        if (!token) return

        try {
          apiClient.setToken(token)
          
          // Validate token first
          await apiClient.validateToken()
          
          // Get user info
          const user = await apiClient.getCurrentUser()
          get().setUser(user)
        } catch (error) {
          // Token expired or invalid, clear auth state
          console.warn('Token validation failed:', error.message)
          get().logout()
        }
      },

      // Refresh user data
      refreshUser: async () => {
        if (!get().token) return { success: false }

        try {
          const user = await apiClient.getCurrentUser()
          get().setUser(user)
          return { success: true, user }
        } catch (error) {
          console.error('Failed to refresh user:', error.message)
          return { success: false, error: error.message }
        }
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({ 
        token: state.token,
        user: state.user 
      }),
    }
  )
)

export default useAuthStore