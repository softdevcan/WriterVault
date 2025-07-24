'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { User, Shield, Settings, Trash2, CalendarDays, Mail, UserCheck } from 'lucide-react'
import useAuthStore from '../../store/auth'
import { Button } from '@/components/ui/button'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import ProfileGeneral from '../../components/profile/ProfileGeneral'
import ProfileSecurity from '../../components/profile/ProfileSecurity'
import ProfileSettings from '../../components/profile/ProfileSettings'
import ProfileAccount from '../../components/profile/ProfileAccount.jsx'

export default function ProfilePage() {
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

  const formatDate = (dateString) => {
    if (!dateString) return 'Bilinmiyor'
    return new Date(dateString).toLocaleDateString('tr-TR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    })
  }

  if (!isAuthenticated || !user) return null

  return (
    <div className="min-h-screen bg-muted/50">
      {/* Header */}
      <header className="bg-background border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-4">
              <Button
                variant="ghost"
                onClick={() => router.push('/dashboard')}
              >
                ← Dashboard'a Dön
              </Button>
              <h1 className="text-xl font-semibold">Profil Ayarları</h1>
            </div>
            <Button variant="outline" size="sm" onClick={handleLogout}>
              Çıkış Yap
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          
          {/* Left Panel - Profile Card */}
          <div className="lg:col-span-1">
            <Card className="sticky top-8">
              <CardContent className="pt-6">
                {/* Avatar Placeholder */}
                <div className="flex flex-col items-center space-y-4">
                  <div className="w-24 h-24 bg-primary/10 rounded-full flex items-center justify-center">
                    <User className="w-12 h-12 text-primary" />
                  </div>
                  
                  {/* User Info */}
                  <div className="text-center space-y-2">
                    <h2 className="text-xl font-semibold">
                      {user.full_name || 'Ad Soyad Belirtilmemiş'}
                    </h2>
                    <p className="text-muted-foreground">@{user.username}</p>
                    
                    {/* Status Badge */}
                    <Badge variant={user.is_active ? "default" : "destructive"}>
                      {user.is_active ? (
                        <><UserCheck className="w-3 h-3 mr-1" /> Aktif</>
                      ) : (
                        <>⏸️ Pasif</>
                      )}
                    </Badge>
                  </div>
                </div>

                <Separator className="my-6" />

                {/* User Details */}
                <div className="space-y-3">
                  <div className="flex items-center space-x-3 text-sm">
                    <Mail className="w-4 h-4 text-muted-foreground" />
                    <span className="text-muted-foreground">{user.email}</span>
                  </div>
                  
                  <div className="flex items-center space-x-3 text-sm">
                    <CalendarDays className="w-4 h-4 text-muted-foreground" />
                    <span className="text-muted-foreground">
                      {formatDate(user.created_at)} tarihinde katıldı
                    </span>
                  </div>

                  {user.is_admin && (
                    <div className="pt-2">
                      <Badge variant="secondary">
                        🛡️ Yönetici
                      </Badge>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Right Panel - Tabs Content */}
          <div className="lg:col-span-3">
            <Tabs defaultValue="general" className="space-y-6">
              <TabsList className="grid w-full grid-cols-4">
                <TabsTrigger value="general" className="flex items-center space-x-2">
                  <User className="w-4 h-4" />
                  <span className="hidden sm:inline">Genel</span>
                </TabsTrigger>
                <TabsTrigger value="security" className="flex items-center space-x-2">
                  <Shield className="w-4 h-4" />
                  <span className="hidden sm:inline">Güvenlik</span>
                </TabsTrigger>
                <TabsTrigger value="settings" className="flex items-center space-x-2">
                  <Settings className="w-4 h-4" />
                  <span className="hidden sm:inline">Ayarlar</span>
                </TabsTrigger>
                <TabsTrigger value="account" className="flex items-center space-x-2">
                  <Trash2 className="w-4 h-4" />
                  <span className="hidden sm:inline">Hesap</span>
                </TabsTrigger>
              </TabsList>

              <TabsContent value="general">
                <ProfileGeneral user={user} />
              </TabsContent>

              <TabsContent value="security">
                <ProfileSecurity />
              </TabsContent>

              <TabsContent value="settings">
                <ProfileSettings user={user} />
              </TabsContent>

              <TabsContent value="account">
                <ProfileAccount user={user} />
              </TabsContent>
            </Tabs>
          </div>
        </div>
      </main>
    </div>
  )
}