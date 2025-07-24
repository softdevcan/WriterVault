'use client'

import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Settings, Mail, Bell, Globe, Save } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Switch } from '@/components/ui/switch'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'

const emailSchema = z.object({
  email: z.string().email('Geçerli bir e-posta adresi girin'),
})

export default function ProfileSettings({ user }) {
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)
  const [success, setSuccess] = useState(false)
  const [emailSuccess, setEmailSuccess] = useState(false)

  // Notification settings state
  const [notifications, setNotifications] = useState({
    emailNotifications: true,
    articleComments: true,
    followUpdates: false,
    systemUpdates: true,
  })

  // Email form
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm({
    resolver: zodResolver(emailSchema),
    defaultValues: {
      email: user.email,
    }
  })

  const onEmailSubmit = async (data) => {
    setIsLoading(true)
    setError(null)
    
    try {
      // TODO: API call to change email
      console.log('Email change:', data)
      
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1500))
      
      setEmailSuccess(true)
      setTimeout(() => setEmailSuccess(false), 5000)
      
    } catch (err) {
      setError(err.message || 'E-posta güncelleme başarısız oldu')
    } finally {
      setIsLoading(false)
    }
  }

  const handleNotificationChange = (key, value) => {
    setNotifications(prev => ({
      ...prev,
      [key]: value
    }))
    
    // Auto-save notification preferences
    console.log('Notification settings updated:', { [key]: value })
    setSuccess(true)
    setTimeout(() => setSuccess(false), 2000)
  }

  return (
    <div className="space-y-6">
      {/* Global Success Alert */}
      {success && (
        <Alert className="border-green-200 bg-green-50 text-green-900">
          <AlertDescription>
            Ayarlarınız başarıyla güncellendi!
          </AlertDescription>
        </Alert>
      )}

      {/* Email Settings Card */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Mail className="w-5 h-5" />
            <span>E-posta Ayarları</span>
          </CardTitle>
          <p className="text-sm text-muted-foreground">
            E-posta adresinizi güncelleyin
          </p>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit(onEmailSubmit)} className="space-y-4">
            
            {/* Email Success Alert */}
            {emailSuccess && (
              <Alert className="border-green-200 bg-green-50 text-green-900">
                <AlertDescription>
                  E-posta adresiniz güncellendi! Doğrulama e-postasını kontrol edin.
                </AlertDescription>
              </Alert>
            )}

            {/* Error Alert */}
            {error && (
              <Alert variant="destructive">
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}

            {/* Current Email Display */}
            <div className="space-y-2">
              <Label>Mevcut E-posta</Label>
              <div className="px-3 py-2 bg-muted/30 border rounded-md">
                {user.email}
              </div>
            </div>

            {/* New Email Input */}
            <div className="space-y-2">
              <Label htmlFor="email">Yeni E-posta</Label>
              <Input
                id="email"
                type="email"
                placeholder="Yeni e-posta adresinizi girin"
                {...register('email')}
              />
              {errors.email && (
                <p className="text-sm text-destructive">{errors.email.message}</p>
              )}
              <p className="text-xs text-muted-foreground">
                E-posta değiştirildikten sonra doğrulama gerekecektir
              </p>
            </div>

            <Button type="submit" disabled={isLoading}>
              <Save className="w-4 h-4 mr-2" />
              {isLoading ? 'Güncelleniyor...' : 'E-postayı Güncelle'}
            </Button>
          </form>
        </CardContent>
      </Card>

      {/* Notification Settings Card */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Bell className="w-5 h-5" />
            <span>Bildirim Ayarları</span>
          </CardTitle>
          <p className="text-sm text-muted-foreground">
            Hangi bildirimleri almak istediğinizi seçin
          </p>
        </CardHeader>
        <CardContent>
          <div className="space-y-6">
            
            {/* Email Notifications */}
            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label className="text-base">E-posta Bildirimleri</Label>
                <p className="text-sm text-muted-foreground">
                  Genel e-posta bildirimlerini alın
                </p>
              </div>
              <Switch
                checked={notifications.emailNotifications}
                onCheckedChange={(checked) => 
                  handleNotificationChange('emailNotifications', checked)
                }
              />
            </div>

            {/* Article Comments */}
            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label className="text-base">Yazı Yorumları</Label>
                <p className="text-sm text-muted-foreground">
                  Yazılarınıza yapılan yorumlar hakkında bildirim alın
                </p>
              </div>
              <Switch
                checked={notifications.articleComments}
                onCheckedChange={(checked) => 
                  handleNotificationChange('articleComments', checked)
                }
              />
            </div>

            {/* Follow Updates */}
            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label className="text-base">Takip Güncellemeleri</Label>
                <p className="text-sm text-muted-foreground">
                  Takip ettiğiniz yazarların yeni içerikleri hakkında bildirim alın
                </p>
              </div>
              <Switch
                checked={notifications.followUpdates}
                onCheckedChange={(checked) => 
                  handleNotificationChange('followUpdates', checked)
                }
              />
            </div>

            {/* System Updates */}
            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label className="text-base">Sistem Güncellemeleri</Label>
                <p className="text-sm text-muted-foreground">
                  Platform güncellemeleri ve önemli duyurular
                </p>
              </div>
              <Switch
                checked={notifications.systemUpdates}
                onCheckedChange={(checked) => 
                  handleNotificationChange('systemUpdates', checked)
                }
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Language & Region Settings Card */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Globe className="w-5 h-5" />
            <span>Dil ve Bölge</span>
          </CardTitle>
          <p className="text-sm text-muted-foreground">
            Dil ve bölge tercihlerinizi ayarlayın
          </p>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            
            {/* Language Selection */}
            <div className="space-y-2">
              <Label>Dil</Label>
              <Select defaultValue="tr">
                <SelectTrigger>
                  <SelectValue placeholder="Bir dil seçin" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="tr">Türkçe</SelectItem>
                  <SelectItem value="en">English</SelectItem>
                  <SelectItem value="de">Deutsch</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* Timezone Selection */}
            <div className="space-y-2">
              <Label>Saat Dilimi</Label>
              <Select defaultValue="tr">
                <SelectTrigger>
                  <SelectValue placeholder="Saat dilimi seçin" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="tr">Türkiye (GMT+3)</SelectItem>
                  <SelectItem value="utc">UTC (GMT+0)</SelectItem>
                  <SelectItem value="est">Eastern (GMT-5)</SelectItem>
                  <SelectItem value="pst">Pacific (GMT-8)</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* Date Format */}
            <div className="space-y-2">
              <Label>Tarih Formatı</Label>
              <Select defaultValue="dd/mm/yyyy">
                <SelectTrigger>
                  <SelectValue placeholder="Tarih formatı seçin" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="dd/mm/yyyy">DD/MM/YYYY</SelectItem>
                  <SelectItem value="mm/dd/yyyy">MM/DD/YYYY</SelectItem>
                  <SelectItem value="yyyy-mm-dd">YYYY-MM-DD</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="pt-2">
              <p className="text-xs text-muted-foreground">
                Dil ve bölge ayarları yakında eklenecek
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}