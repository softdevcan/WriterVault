'use client'

import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Shield, Eye, EyeOff, Key, AlertTriangle } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Alert, AlertDescription } from '@/components/ui/alert'

const passwordSchema = z.object({
  currentPassword: z.string().min(1, 'Mevcut şifre gerekli'),
  newPassword: z.string()
    .min(6, 'Yeni şifre en az 6 karakter olmalı')
    .max(50, 'Yeni şifre en fazla 50 karakter olmalı'),
  confirmPassword: z.string(),
}).refine((data) => data.newPassword === data.confirmPassword, {
  message: "Yeni şifreler eşleşmiyor",
  path: ["confirmPassword"],
})

export default function ProfileSecurity() {
  const [showCurrentPassword, setShowCurrentPassword] = useState(false)
  const [showNewPassword, setShowNewPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)
  const [success, setSuccess] = useState(false)

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm({
    resolver: zodResolver(passwordSchema),
  })

  const onSubmit = async (data) => {
    setIsLoading(true)
    setError(null)
    
    try {
      // TODO: API call to change password
      console.log('Password change:', { 
        currentPassword: data.currentPassword, 
        newPassword: data.newPassword 
      })
      
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1500))
      
      setSuccess(true)
      reset()
      setTimeout(() => setSuccess(false), 5000)
      
    } catch (err) {
      setError(err.message || 'Şifre değiştirme işlemi başarısız oldu')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      {/* Password Change Card */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Key className="w-5 h-5" />
            <span>Şifre Değiştir</span>
          </CardTitle>
          <p className="text-sm text-muted-foreground">
            Hesabınızın güvenliği için güçlü bir şifre kullanın
          </p>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            
            {/* Success Alert */}
            {success && (
              <Alert className="border-green-200 bg-green-50 text-green-900">
                <AlertDescription>
                  Şifreniz başarıyla değiştirildi!
                </AlertDescription>
              </Alert>
            )}

            {/* Error Alert */}
            {error && (
              <Alert variant="destructive">
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}

            {/* Current Password */}
            <div className="space-y-2">
              <Label htmlFor="currentPassword">Mevcut Şifre</Label>
              <div className="relative">
                <Input
                  id="currentPassword"
                  type={showCurrentPassword ? 'text' : 'password'}
                  placeholder="Mevcut şifrenizi girin"
                  {...register('currentPassword')}
                />
                <Button
                  type="button"
                  variant="ghost"
                  size="icon"
                  className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent"
                  onClick={() => setShowCurrentPassword(!showCurrentPassword)}
                >
                  {showCurrentPassword ? (
                    <EyeOff className="h-4 w-4" />
                  ) : (
                    <Eye className="h-4 w-4" />
                  )}
                </Button>
              </div>
              {errors.currentPassword && (
                <p className="text-sm text-destructive">{errors.currentPassword.message}</p>
              )}
            </div>

            {/* New Password */}
            <div className="space-y-2">
              <Label htmlFor="newPassword">Yeni Şifre</Label>
              <div className="relative">
                <Input
                  id="newPassword"
                  type={showNewPassword ? 'text' : 'password'}
                  placeholder="Yeni şifrenizi girin"
                  {...register('newPassword')}
                />
                <Button
                  type="button"
                  variant="ghost"
                  size="icon"
                  className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent"
                  onClick={() => setShowNewPassword(!showNewPassword)}
                >
                  {showNewPassword ? (
                    <EyeOff className="h-4 w-4" />
                  ) : (
                    <Eye className="h-4 w-4" />
                  )}
                </Button>
              </div>
              {errors.newPassword && (
                <p className="text-sm text-destructive">{errors.newPassword.message}</p>
              )}
            </div>

            {/* Confirm New Password */}
            <div className="space-y-2">
              <Label htmlFor="confirmPassword">Yeni Şifre Tekrar</Label>
              <div className="relative">
                <Input
                  id="confirmPassword"
                  type={showConfirmPassword ? 'text' : 'password'}
                  placeholder="Yeni şifrenizi tekrar girin"
                  {...register('confirmPassword')}
                />
                <Button
                  type="button"
                  variant="ghost"
                  size="icon"
                  className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                >
                  {showConfirmPassword ? (
                    <EyeOff className="h-4 w-4" />
                  ) : (
                    <Eye className="h-4 w-4" />
                  )}
                </Button>
              </div>
              {errors.confirmPassword && (
                <p className="text-sm text-destructive">{errors.confirmPassword.message}</p>
              )}
            </div>

            {/* Submit Button */}
            <Button type="submit" disabled={isLoading} className="w-full">
              {isLoading ? 'Şifre değiştiriliyor...' : 'Şifreyi Değiştir'}
            </Button>
          </form>
        </CardContent>
      </Card>

      {/* Security Tips Card */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Shield className="w-5 h-5" />
            <span>Güvenlik İpuçları</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-start space-x-3">
              <div className="w-2 h-2 bg-primary rounded-full mt-2 flex-shrink-0"></div>
              <div>
                <h4 className="font-medium">Güçlü Şifre Kullanın</h4>
                <p className="text-sm text-muted-foreground">
                  En az 8 karakter, büyük-küçük harf, rakam ve özel karakter içeren şifreler tercih edin.
                </p>
              </div>
            </div>
            
            <div className="flex items-start space-x-3">
              <div className="w-2 h-2 bg-primary rounded-full mt-2 flex-shrink-0"></div>
              <div>
                <h4 className="font-medium">Şifrenizi Düzenli Değiştirin</h4>
                <p className="text-sm text-muted-foreground">
                  Güvenliğiniz için şifrenizi 3-6 ayda bir değiştirmenizi öneririz.
                </p>
              </div>
            </div>
            
            <div className="flex items-start space-x-3">
              <div className="w-2 h-2 bg-primary rounded-full mt-2 flex-shrink-0"></div>
              <div>
                <h4 className="font-medium">Şifrenizi Paylaşmayın</h4>
                <p className="text-sm text-muted-foreground">
                  Şifrenizi hiç kimseyle paylaşmayın ve güvenli olmayan yerlerde kaydetmeyin.
                </p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Security Status Card */}
      <Card>
        <CardHeader>
          <CardTitle>Güvenlik Durumu</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-center justify-between p-3 bg-green-50 dark:bg-green-950 rounded-lg border border-green-200 dark:border-green-800">
              <div className="flex items-center space-x-3">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                <span className="text-sm font-medium">Hesap Aktif</span>
              </div>
              <span className="text-xs text-green-600 dark:text-green-400">✓ Güvenli</span>
            </div>
            
            <div className="flex items-center justify-between p-3 bg-yellow-50 dark:bg-yellow-950 rounded-lg border border-yellow-200 dark:border-yellow-800">
              <div className="flex items-center space-x-3">
                <AlertTriangle className="w-4 h-4 text-yellow-600" />
                <span className="text-sm font-medium">2FA Kurulmamış</span>
              </div>
              <span className="text-xs text-yellow-600">⚠ Önerilir</span>
            </div>
          </div>
          
          <div className="mt-4 text-center">
            <p className="text-sm text-muted-foreground">
              İki faktörlü doğrulama yakında eklenecek
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}