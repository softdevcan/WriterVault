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

const loginSchema = z.object({
  username: z.string().min(1, 'Kullanıcı adı gerekli'),
  password: z.string().min(1, 'Şifre gerekli'),
})

export default function LoginPage() {
  const router = useRouter()
  const { login, isLoading, error, isAuthenticated, clearError } = useAuthStore()
  const [showPassword, setShowPassword] = useState(false)

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm({
    resolver: zodResolver(loginSchema),
  })

  useEffect(() => {
    if (isAuthenticated) {
      router.push('/dashboard')
    }
  }, [isAuthenticated, router])

  useEffect(() => {
    clearError()
  }, [clearError])

  const onSubmit = async (data) => {
    const result = await login(data)
    
    if (result.success) {
      router.push('/dashboard')
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-muted/50 py-12 px-4">
      <div className="w-full max-w-md space-y-8">
        
        {/* Header */}
        <div className="text-center">
          <h1 className="text-3xl font-bold">Yazarlar Platformu</h1>
          <p className="mt-2 text-sm text-muted-foreground">
            Hesabınıza giriş yapın
          </p>
        </div>

        {/* Login Form */}
        <Card>
          <CardHeader>
            <CardTitle>Giriş Yap</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
              
              {/* Error Alert */}
              {error && (
                <Alert variant="destructive">
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              )}

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

              {/* Submit Button */}
              <Button type="submit" className="w-full" disabled={isLoading}>
                {isLoading ? 'Giriş yapılıyor...' : 'Giriş Yap'}
              </Button>
            </form>

            {/* Links */}
            <div className="mt-6 space-y-4">
              <div className="text-center">
                <a
                  href="/auth/forgot-password"
                  className="text-sm text-muted-foreground hover:text-primary underline"
                >
                  Şifrenizi mi unuttunuz?
                </a>
              </div>
              
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
                  Hesabınız yok mu?{' '}
                  <a
                    href="/auth/register"
                    className="font-medium text-primary hover:underline"
                  >
                    Kayıt olun
                  </a>
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Demo Credentials */}
        <Card className="border-dashed">
          <CardContent className="pt-6">
            <h3 className="text-sm font-medium text-muted-foreground mb-2">Demo Hesap:</h3>
            <div className="text-xs text-muted-foreground space-y-1">
              <p><strong>Kullanıcı:</strong> demo</p>
              <p><strong>Şifre:</strong> demo123</p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}