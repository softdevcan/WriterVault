'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { ArrowLeft } from 'lucide-react'
import useAuthStore from '../../../store/auth'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Alert, AlertDescription } from '@/components/ui/alert'

const forgotPasswordSchema = z.object({
  email: z.string().email('Geçerli bir e-posta adresi girin'),
})

export default function ForgotPasswordPage() {
  const router = useRouter()
  const { requestPasswordReset, isLoading, error, isAuthenticated, clearError } = useAuthStore()
  const [success, setSuccess] = useState(false)

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm({
    resolver: zodResolver(forgotPasswordSchema),
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
    const result = await requestPasswordReset(data.email)
    
    if (result.success) {
      setSuccess(true)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-muted/50 py-12 px-4">
      <div className="w-full max-w-md space-y-8">
        
        {/* Header */}
        <div className="text-center">
          <h1 className="text-3xl font-bold">Şifre Sıfırlama</h1>
          <p className="mt-2 text-sm text-muted-foreground">
            E-posta adresinizi girin, size sıfırlama bağlantısı gönderelim
          </p>
        </div>

        {/* Forgot Password Form */}
        <Card>
          <CardHeader>
            <CardTitle>Şifremi Unuttum</CardTitle>
          </CardHeader>
          <CardContent>
            {success ? (
              <div className="space-y-4">
                <Alert className="border-green-200 bg-green-50 text-green-900">
                  <AlertDescription>
                    Şifre sıfırlama bağlantısı e-posta adresinize gönderildi. 
                    E-postanızı kontrol edin ve bağlantıya tıklayarak şifrenizi sıfırlayın.
                  </AlertDescription>
                </Alert>
                
                <div className="space-y-2">
                  <Button 
                    variant="outline" 
                    className="w-full"
                    onClick={() => setSuccess(false)}
                  >
                    Tekrar Gönder
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
              </div>
            ) : (
              <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
                
                {/* Error Alert */}
                {error && (
                  <Alert variant="destructive">
                    <AlertDescription>{error}</AlertDescription>
                  </Alert>
                )}

                {/* Email Field */}
                <div className="space-y-2">
                  <Label htmlFor="email">E-posta Adresi</Label>
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

                {/* Submit Button */}
                <Button type="submit" className="w-full" disabled={isLoading}>
                  {isLoading ? 'Gönderiliyor...' : 'Sıfırlama Bağlantısı Gönder'}
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