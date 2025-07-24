'use client'

import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { useEffect, useState } from 'react'
import useAuthStore from '../store/auth'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
})

function AuthInitializer({ children }) {
  const [isInitialized, setIsInitialized] = useState(false)
  const initialize = useAuthStore((state) => state.initialize)

  useEffect(() => {
    const init = async () => {
      await initialize()
      setIsInitialized(true)
    }
    init()
  }, [initialize])

  if (!isInitialized) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    )
  }

  return children
}

export default function ClientProviders({ children }) {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthInitializer>
        {children}
      </AuthInitializer>
    </QueryClientProvider>
  )
}