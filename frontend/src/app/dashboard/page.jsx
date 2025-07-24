'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { LogOut, User, Settings } from 'lucide-react'
import useAuthStore from '../../store/auth'
import { Button } from '@/components/ui/button'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'

export default function DashboardPage() {
  const router = useRouter()
  const { user, isAuthenticated, logout } = useAuthStore()

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/auth/login')
    }
  }, [isAuthenticated, router])

  const handleLogout = () => {
    logout()
    router.push('/auth/login')
  }

  if (!isAuthenticated || !user) return null

  return (
    <div className="min-h-screen bg-muted/50">
      {/* Header */}
      <header className="bg-background border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <h1 className="text-xl font-semibold">
              Yazarlar Platformu
            </h1>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-muted-foreground">
                Hoş geldin, {user.full_name || user.username}
              </span>
              <Button variant="outline" size="sm" onClick={handleLogout}>
                <LogOut className="h-4 w-4 mr-2" />
                Çıkış
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          
          {/* Welcome Card */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <User className="h-5 w-5 mr-2" />
                Hoş Geldin!
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground">
                Yazarlar platformuna başarıyla giriş yaptınız. 
                Buradan yazılarınızı yönetebilirsiniz.
              </p>
            </CardContent>
          </Card>

          {/* Profile Info */}
          <Card>
            <CardHeader>
              <CardTitle>Profil Bilgileri</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div>
                <p className="text-sm font-medium">Kullanıcı Adı:</p>
                <p className="text-muted-foreground">{user.username}</p>
              </div>
              <div>
                <p className="text-sm font-medium">E-posta:</p>
                <p className="text-muted-foreground">{user.email}</p>
              </div>
              <div>
                <p className="text-sm font-medium">Durum:</p>
                <span className={`inline-flex px-2 py-1 text-xs rounded-full ${
                  user.is_active 
                    ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300' 
                    : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300'
                }`}>
                  {user.is_active ? 'Aktif' : 'Pasif'}
                </span>
              </div>
            </CardContent>
          </Card>

          {/* Quick Actions */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Settings className="h-5 w-5 mr-2" />
                Hızlı İşlemler
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <Button 
                variant="outline" 
                className="w-full justify-start"
                onClick={() => router.push('/profile')}
              >
                <User className="w-4 h-4 mr-2" />
                Profili Düzenle
              </Button>
              <Button variant="outline" className="w-full justify-start">
                Yeni Yazı Oluştur
              </Button>
              <Button variant="outline" className="w-full justify-start">
                Yazılarım
              </Button>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  )
}