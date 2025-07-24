'use client'

import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Save, User, Edit } from 'lucide-react'
import useAuthStore from '../../store/auth'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Textarea } from '@/components/ui/textarea'

const profileSchema = z.object({
  full_name: z.string()
    .min(2, 'Ad soyad en az 2 karakter olmalı')
    .max(100, 'Ad soyad en fazla 100 karakter olmalı'),
  bio: z.string()
    .max(500, 'Bio en fazla 500 karakter olmalı')
    .optional(),
})

export default function ProfileGeneral({ user }) {
  const { refreshUser, isLoading, error, clearError } = useAuthStore()
  const [isEditing, setIsEditing] = useState(false)
  const [success, setSuccess] = useState(false)

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm({
    resolver: zodResolver(profileSchema),
    defaultValues: {
      full_name: user.full_name || '',
      bio: user.bio || '',
    }
  })

  const onSubmit = async (data) => {
    // TODO: API call to update profile
    console.log('Profile update:', data)
    
    // Simulate API call
    setTimeout(() => {
      setSuccess(true)
      setIsEditing(false)
      setTimeout(() => setSuccess(false), 3000)
    }, 1000)
  }

  const handleCancel = () => {
    reset({
      full_name: user.full_name || '',
      bio: user.bio || '',
    })
    setIsEditing(false)
    clearError()
  }

  return (
    <div className="space-y-6">
      {/* Profile Information Card */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <div>
            <CardTitle className="flex items-center space-x-2">
              <User className="w-5 h-5" />
              <span>Profil Bilgileri</span>
            </CardTitle>
            <p className="text-sm text-muted-foreground mt-1">
              Genel profil bilgilerinizi düzenleyin
            </p>
          </div>
          {!isEditing && (
            <Button 
              variant="outline" 
              size="sm"
              onClick={() => setIsEditing(true)}
            >
              <Edit className="w-4 h-4 mr-2" />
              Düzenle
            </Button>
          )}
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            
            {/* Success Alert */}
            {success && (
              <Alert className="border-green-200 bg-green-50 text-green-900">
                <AlertDescription>
                  Profil bilgileriniz başarıyla güncellendi!
                </AlertDescription>
              </Alert>
            )}

            {/* Error Alert */}
            {error && (
              <Alert variant="destructive">
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}

            {/* Full Name Field */}
            <div className="space-y-2">
              <Label htmlFor="full_name">Ad Soyad</Label>
              {isEditing ? (
                <Input
                  id="full_name"
                  type="text"
                  placeholder="Adınızı ve soyadınızı girin"
                  {...register('full_name')}
                />
              ) : (
                <div className="px-3 py-2 border rounded-md bg-muted/30">
                  {user.full_name || 'Belirtilmemiş'}
                </div>
              )}
              {errors.full_name && (
                <p className="text-sm text-destructive">{errors.full_name.message}</p>
              )}
            </div>

            {/* Bio Field */}
            <div className="space-y-2">
              <Label htmlFor="bio">Hakkımda</Label>
              {isEditing ? (
                <Textarea
                  id="bio"
                  placeholder="Kendiniz hakkında kısa bir açıklama yazın..."
                  rows={3}
                  {...register('bio')}
                />
              ) : (
                <div className="px-3 py-2 border rounded-md bg-muted/30 min-h-[80px]">
                  {user.bio || 'Henüz bir açıklama eklenmemiş'}
                </div>
              )}
              {errors.bio && (
                <p className="text-sm text-destructive">{errors.bio.message}</p>
              )}
            </div>

            {/* Read-only Fields */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>Kullanıcı Adı</Label>
                <div className="px-3 py-2 border rounded-md bg-muted/50">
                  @{user.username}
                </div>
                <p className="text-xs text-muted-foreground">
                  Kullanıcı adı değiştirilemez
                </p>
              </div>

              <div className="space-y-2">
                <Label>E-posta</Label>
                <div className="px-3 py-2 border rounded-md bg-muted/50">
                  {user.email}
                </div>
                <p className="text-xs text-muted-foreground">
                  E-posta Ayarlar sekmesinden değiştirilebilir
                </p>
              </div>
            </div>

            {/* Action Buttons */}
            {isEditing && (
              <div className="flex space-x-4 pt-4">
                <Button type="submit" disabled={isLoading}>
                  <Save className="w-4 h-4 mr-2" />
                  {isLoading ? 'Kaydediliyor...' : 'Kaydet'}
                </Button>
                <Button 
                  type="button" 
                  variant="outline" 
                  onClick={handleCancel}
                  disabled={isLoading}
                >
                  İptal
                </Button>
              </div>
            )}
          </form>
        </CardContent>
      </Card>

      {/* Account Stats Card */}
      <Card>
        <CardHeader>
          <CardTitle>Hesap İstatistikleri</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center p-4 bg-muted/30 rounded-lg">
              <div className="text-2xl font-bold text-primary">0</div>
              <p className="text-sm text-muted-foreground">Toplam Yazı</p>
            </div>
            <div className="text-center p-4 bg-muted/30 rounded-lg">
              <div className="text-2xl font-bold text-primary">0</div>
              <p className="text-sm text-muted-foreground">Toplam Yorum</p>
            </div>
            <div className="text-center p-4 bg-muted/30 rounded-lg">
              <div className="text-2xl font-bold text-primary">0</div>
              <p className="text-sm text-muted-foreground">Takipçi</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}