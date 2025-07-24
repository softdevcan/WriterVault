'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Eye, EyeOff } from 'lucide-react'
import useAuthStore from '../../../store/auth'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Alert, AlertDescription } from '@/components/ui/alert'

const registerSchema = z.object({
  username: z.string()
    .min(3, 'Kullanıcı adı en az 3 karakter olmalı')
    .max(20, 'Kullanıcı adı en fazla 20 karakter olmalı')
    .regex(/^[a-zA-Z0-9_]+$/, 'Kullanıcı adı sadece harf, rakam ve _ içerebilir'),
  email: z.string()
    .email('Geçerli bir e-posta adresi girin'),
  password: z.string()
    .min(6, 'Şifre en az 6 karakter olmalı')
    .max(50, 'Şifre en fazla 50 karakter olmalı'),
  confirmPassword: z.string(),
  full_name: z.string()
    .min(2, 'Ad soyad en az 2 karakter olmalı')
    .max(100, 'Ad soyad en fazla 100 karakter olmalı')
    .optional(),
}).refine((data) => data.password === data.confirmPassword, {
  message: "Şifreler eşleşmiyor",
  path: ["confirmPassword"],
})

export default function RegisterPage() {
  const router = useRouter()
  const { register: registerUser, isLoading, error, isAuthenticated, clearError } = useAuthStore()
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)
  const [success, setSuccess] = useState(false)

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm({
    resolver: zodResolver(registerSchema),
  })

  useEffect(() => {
    if (isAuthenticated) {
      router.push('/dashboard')
    }
  }, [isAuthenticated, router])

  useEffect(() => {
    clearError()
    setSuccess(false)
  }, [clearError])

  const onSubmit = async (data) => {
    const { confirmPassword, ...registerData } = data
    const result = await registerUser(registerData)
    
    if (result.success) {
      setSuccess(true)
      setTimeout(() => {
        router.push('/auth/login')
      }, 2000)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-muted/50 py-12 px-4">
      <div className="w-full max-w-md space-y-8">
        
        {/* Header */}
        <div className="text-center">
          <h1 className="text-3xl font-bold">Yazarlar Platformu</h1>
          <p className="mt-2 text-sm text-muted-foreground">
            Yeni hesap oluşturun
          </p>
        </div>

        {/* Register Form */}
        <Card>
          <CardHeader>
            <CardTitle>Kayıt Ol</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
              
              {/* Success Alert */}
              {success && (
                <Alert className="border-green-200 bg-green-50 text-green-900">
                  <AlertDescription>
                    Hesabınız başarıyla oluşturuldu! Giriş sayfasına yönlendiriliyorsunuz...
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
                <Input
                  id="full_name"
                  type="text"
                  placeholder="Adınızı ve soyadınızı girin"
                  {...register('full_name')}
                />
                {errors.full_name && (
                  <p className="text-sm text-destructive">{errors.full_name.message}</p>
                )}
              </div>

              {/* Username Field */}
              <div className="space-y-2">
                <Label htmlFor="username">Kullanıcı Adı</Label>
                <Input
                  id="username"
                  type="text"
                  placeholder="Kullanıcı adınızı girin"
                  {...register('username')}
                />
                {errors.username && (
                  <p className="text-sm text-destructive">{errors.username.message}</p>
                )}
              </div>

              {/* Email Field */}
              <div className="space-y-2">
                <Label htmlFor="email">E-posta</Label>
                <Input
                  id="email"
                  type="email"
                  placeholder="E-posta adresinizi girin"
                  {...register('email')}
                />
                {errors.email && (
                  <p className="text-sm text-destructive">{errors.email.message}</p>
                )}
              </div>

              {/* Password Field */}
              <div className="space-y-2">
                <Label htmlFor="password">Şifre</Label>
                <div className="relative">
                  <Input
                    id="password"
                    type={showPassword ? 'text' : 'password'}
                    placeholder="Şifrenizi girin"
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
              <Button 
                type="submit" 
                className="w-full" 
                disabled={isLoading || success}
              >
                {isLoading ? 'Kayıt oluşturuluyor...' : 'Kayıt Ol'}
              </Button>
            </form>

            {/* Links */}
            <div className="mt-6 space-y-4">
              <div className="relative">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t" />
                </div>
                <div className="relative flex justify-center text-xs uppercase">
                  <span className="bg-background px-2 text-muted-foreground">
                    veya
                  </span>
                </div>
              </div>
              
              <div className="text-center">
                <p className="text-sm text-muted-foreground">
                  Zaten hesabınız var mı?{' '}
                  <a
                    href="/auth/login"
                    className="font-medium text-primary hover:underline"
                  >
                    Giriş yapın
                  </a>
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}