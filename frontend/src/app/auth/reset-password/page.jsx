'use client'

import { useState, useEffect } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Eye, EyeOff, ArrowLeft } from 'lucide-react'
import useAuthStore from '../../../store/auth'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Alert, AlertDescription } from '@/components/ui/alert'

const resetPasswordSchema = z.object({
  password: z.string()
    .min(6, 'Şifre en az 6 karakter olmalı')
    .max(50, 'Şifre en fazla 50 karakter olmalı'),
  confirmPassword: z.string(),
}).refine((data) => data.password === data.confirmPassword, {
  message: "Şifreler eşleşmiyor",
  path: ["confirmPassword"],
})

export default function ResetPasswordPage() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const token = searchParams.get('token')
  
  const { 
    resetPassword, 
    verifyResetToken, 
    isLoading, 
    error, 
    isAuthenticated, 
    clearError 
  } = useAuthStore()
  
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)
  const [success, setSuccess] = useState(false)
  const [tokenValid, setTokenValid] = useState(null)

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm({
    resolver: zodResolver(resetPasswordSchema),
  })

  // Check if user is authenticated
  useEffect(() => {
    if (isAuthenticated) {
      router.push('/dashboard')
    }
  }, [isAuthenticated, router])

  // Verify token on mount
  useEffect(() => {
    const checkToken = async () => {
      if (!token) {
        setTokenValid(false)
        return
      }

      const result = await verifyResetToken(token)
      setTokenValid(result.success)
    }

    checkToken()
  }, [token, verifyResetToken])

  useEffect(() => {
    clearError()
    setSuccess(false)
  }, [clearError])

  const onSubmit = async (data) => {
    if (!token) return

    const result = await resetPassword(token, data.password)
    
    if (result.success) {
      setSuccess(true)
      setTimeout(() => {
        router.push('/login')
      }, 3000)
    }
  }

  // Loading state while verifying token
  if (tokenValid === null) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-muted/50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Token doğrulanıyor...</p>
        </div>
      </div>
    )
  }

  // Invalid token
  if (!tokenValid) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-muted/50 py-12 px-4">
        <div className="w-full max-w-md">
          <Card>
            <CardHeader>
              <CardTitle>Geçersiz Token</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <Alert variant="destructive">
                <AlertDescription>
                  Şifre sıfırlama bağlantınız geçersiz veya süresi dolmuş. 
                  Lütfen yeni bir sıfırlama bağlantısı isteyin.
                </AlertDescription>
              </Alert>
              
              <div className="space-y-2">
                <Button 
                  className="w-full"
                  onClick={() => router.push('/auth/forgot-password')}
                >
                  Yeni Sıfırlama Bağlantısı İste
                </Button>
                
                <Button 
                  variant="ghost" 
                  className="w-full"
                  onClick={() => router.push('/auth/login')}
                >
                  <ArrowLeft className="h-4 w-4 mr-2" />
                  Giriş Sayfasına Dön
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-muted/50 py-12 px-4">
      <div className="w-full max-w-md space-y-8">
        
        {/* Header */}
        <div className="text-center">
          <h1 className="text-3xl font-bold">Yeni Şifre Belirle</h1>
          <p className="mt-2 text-sm text-muted-foreground">
            Hesabınız için yeni bir şifre oluşturun
          </p>
        </div>

        {/* Reset Password Form */}
        <Card>
          <CardHeader>
            <CardTitle>Şifre Sıfırla</CardTitle>
          </CardHeader>
          <CardContent>
            {success ? (
              <div className="space-y-4">
                <Alert className="border-green-200 bg-green-50 text-green-900">
                  <AlertDescription>
                    Şifreniz başarıyla değiştirildi! Giriş sayfasına yönlendiriliyorsunuz...
                  </AlertDescription>
                </Alert>
                
                <Button 
                  className="w-full"
                  onClick={() => router.push('/auth/login')}
                >
                  Giriş Sayfasına Git
                </Button>
              </div>
            ) : (
              <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
                
                {/* Error Alert */}
                {error && (
                  <Alert variant="destructive">
                    <AlertDescription>{error}</AlertDescription>
                  </Alert>
                )}

                {/* Password Field */}
                <div className="space-y-2">
                  <Label htmlFor="password">Yeni Şifre</Label>
                  <div className="relative">
                    <Input
                      id="password"
                      type={showPassword ? 'text' : 'password'}
                      placeholder="Yeni şifrenizi girin"
                      {...register('password')}
                    />
                    <Button
                      type="button"
                      variant="ghost"
                      size="icon"
                      className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent"
                      onClick={() => setShowPassword(!showPassword)}
                    >
                      {showPassword ? (
                        <EyeOff className="h-4 w-4" />
                      ) : (
                        <Eye className="h-4 w-4" />
                      )}
                    </Button>
                  </div>
                  {errors.password && (
                    <p className="text-sm text-destructive">{errors.password.message}</p>
                  )}
                </div>

                {/* Confirm Password Field */}
                <div className="space-y-2">
                  <Label htmlFor="confirmPassword">Şifre Tekrar</Label>
                  <div className="relative">
                    <Input
                      id="confirmPassword"
                      type={showConfirmPassword ? 'text' : 'password'}
                      placeholder="Şifrenizi tekrar girin"
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
                <Button type="submit" className="w-full" disabled={isLoading}>
                  {isLoading ? 'Şifre güncelleniyor...' : 'Şifreyi Güncelle'}
                </Button>

                {/* Back to Login */}
                <Button 
                  type="button"
                  variant="ghost" 
                  className="w-full"
                  onClick={() => router.push('/auth/login')}
                >
                  <ArrowLeft className="h-4 w-4 mr-2" />
                  Giriş Sayfasına Dön
                </Button>
              </form>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}