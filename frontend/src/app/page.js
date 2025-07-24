'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import useAuthStore from '../store/auth'
import { Button } from '@/components/ui/button'

export default function Home() {
  const router = useRouter()
  const { isAuthenticated } = useAuthStore()

  useEffect(() => {
    if (isAuthenticated) {
      router.push('/dashboard')
    }
  }, [isAuthenticated, router])

  return (
    <div className="min-h-screen bg-gradient-to-br from-muted/50 to-muted">
      {/* Header */}
      <header className="bg-background/80 backdrop-blur-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <h1 className="text-xl font-bold">
              Yazarlar Platformu
            </h1>
            <div className="space-x-4">
              <Button 
                variant="ghost" 
                onClick={() => router.push('/auth/login')}
              >
                Giriş Yap
              </Button>
              <Button 
                onClick={() => router.push('/auth/register')}
              >
                Kayıt Ol
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center py-20">
          <h1 className="text-4xl md:text-6xl font-bold mb-6">
            Yazarlar için
            <span className="text-primary block">
              Modern Platform
            </span>
          </h1>
          
          <p className="text-xl text-muted-foreground mb-8 max-w-2xl mx-auto">
            Yazılarınızı paylaşın, okuyucularla buluşun ve edebi topluluğun bir parçası olun. 
          </p>

          <div className="space-x-4">
            <Button 
              size="lg"
              onClick={() => router.push('/auth/register')}
            >
              Hemen Başlayın
            </Button>
            <Button 
              variant="outline" 
              size="lg"
              onClick={() => router.push('/auth/login')}
            >
              Giriş Yapın
            </Button>
          </div>
        </div>
      </main>
    </div>
  )
}