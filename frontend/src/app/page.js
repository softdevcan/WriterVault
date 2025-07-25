// src/app/page.js
'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { 
  FileText, 
  BookOpen, 
  Users, 
  TrendingUp,
  ArrowRight,
  Sparkles
} from 'lucide-react'

// Import path'ini senin mevcut import'una göre ayarladım
import useAuthStore from '../store/auth'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'

export default function Home() {
  const router = useRouter()
  const { isAuthenticated } = useAuthStore()

  useEffect(() => {
    if (isAuthenticated) {
      router.push('/dashboard')
    }
  }, [isAuthenticated, router])

  const features = [
    {
      icon: FileText,
      title: 'Modern Editör',
      description: 'TipTap tabanlı gelişmiş metin editörü ile yazılarınızı profesyonel bir şekilde oluşturun.'
    },
    {
      icon: BookOpen,
      title: 'Koleksiyonlar',
      description: 'Makalelerinizi seri halinde organize edin, kitap veya kurs formatında sunun.'
    },
    {
      icon: Users,
      title: 'Topluluk',
      description: 'Diğer yazarlarla etkileşime geçin, yorumlar alın ve takipçi kitlenizi büyütün.'
    },
    {
      icon: TrendingUp,
      title: 'Analitik',
      description: 'Makalelerinizin performansını takip edin, okuyucu etkileşimlerini analiz edin.'
    }
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-muted/50 to-muted">
      
      {/* Header */}
      <header className="bg-background/80 backdrop-blur-sm border-b sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
                <span className="text-primary-foreground font-bold text-sm">W</span>
              </div>
              <h1 className="text-xl font-bold">
                Writer Vault
              </h1>
            </div>
            
            <nav className="hidden md:flex items-center space-x-6">
              <Link href="/articles" className="text-muted-foreground hover:text-foreground transition-colors">
                Makaleler
              </Link>
              <Link href="/authors" className="text-muted-foreground hover:text-foreground transition-colors">
                Yazarlar
              </Link>
              <Link href="/about" className="text-muted-foreground hover:text-foreground transition-colors">
                Hakkımızda
              </Link>
            </nav>

            <div className="flex items-center space-x-3">
              <Button 
                variant="ghost" 
                onClick={() => router.push('/auth/login')}
              >
                Giriş Yap
              </Button>
              <Button 
                onClick={() => router.push('/auth/register')}
                className="hidden sm:inline-flex"
              >
                Kayıt Ol
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Hero */}
        <section className="text-center py-20 lg:py-32">
          <div className="max-w-4xl mx-auto">
            <Badge variant="secondary" className="mb-6">
              <Sparkles className="w-4 h-4 mr-2" />
              Yazarlar için Modern Platform
            </Badge>
            
            <h1 className="text-4xl md:text-6xl lg:text-7xl font-bold mb-6 leading-tight">
              Yazılarınızı
              <span className="text-primary block">
                Dünyayla Paylaşın
              </span>
            </h1>
            
            <p className="text-xl text-muted-foreground mb-10 max-w-3xl mx-auto leading-relaxed">
              Modern editör araçları, güçlü organizasyon sistemi ve aktif topluluk ile 
              yazılarınızı oluşturun, yönetin ve okuyucularınızla buluşturun.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
              <Button 
                size="lg"
                onClick={() => router.push('/auth/register')}
                className="text-lg px-8 py-6"
              >
                Ücretsiz Başlayın
                <ArrowRight className="w-5 h-5 ml-2" />
              </Button>
              <Button 
                variant="outline" 
                size="lg"
                onClick={() => router.push('/auth/login')}
                className="text-lg px-8 py-6"
              >
                Giriş Yapın
              </Button>
            </div>

            <p className="text-sm text-muted-foreground mt-4">
              Kredi kartı gerektirmez • Anında başlayın
            </p>
          </div>
        </section>

        {/* Features */}
        <section className="py-20">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              Yazarlar İçin Güçlü Araçlar
            </h2>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              Modern teknoloji ile desteklenen platform, yazım deneyiminizi bir üst seviyeye taşır.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {features.map((feature, index) => (
              <Card key={index} className="border-0 shadow-lg hover:shadow-xl transition-shadow">
                <CardContent className="p-6 text-center">
                  <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mx-auto mb-4">
                    <feature.icon className="w-6 h-6 text-primary" />
                  </div>
                  <h3 className="text-lg font-semibold mb-2">{feature.title}</h3>
                  <p className="text-muted-foreground text-sm leading-relaxed">
                    {feature.description}
                  </p>
                </CardContent>
              </Card>
            ))}
          </div>
        </section>

        {/* CTA Section */}
        <section className="py-20">
          <Card className="border-0 bg-primary text-primary-foreground shadow-2xl">
            <CardContent className="p-12 text-center">
              <h2 className="text-3xl md:text-4xl font-bold mb-4">
                Yazma Yolculuğunuza Bugün Başlayın
              </h2>
              <p className="text-xl mb-8 opacity-90 max-w-2xl mx-auto">
                Binlerce yazarın güvendiği platform ile hikayelerinizi dünyayla paylaşın.
              </p>
              <Button 
                size="lg" 
                variant="secondary"
                onClick={() => router.push('/auth/register')}
                className="text-lg px-8 py-6"
              >
                Ücretsiz Hesap Oluştur
                <ArrowRight className="w-5 h-5 ml-2" />
              </Button>
            </CardContent>
          </Card>
        </section>

      </main>

      {/* Footer */}
      <footer className="bg-background border-t mt-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="grid md:grid-cols-4 gap-8">
            
            <div>
              <div className="flex items-center space-x-2 mb-4">
                <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
                  <span className="text-primary-foreground font-bold text-sm">W</span>
                </div>
                <span className="text-xl font-bold">Writer Vault</span>
              </div>
              <p className="text-muted-foreground text-sm">
                Modern yazarlar için edebi içerik platformu.
              </p>
            </div>

            <div>
              <h3 className="font-semibold mb-4">Platform</h3>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li><Link href="/features" className="hover:text-foreground transition-colors">Özellikler</Link></li>
                <li><Link href="/pricing" className="hover:text-foreground transition-colors">Fiyatlandırma</Link></li>
                <li><Link href="/docs" className="hover:text-foreground transition-colors">Dokümantasyon</Link></li>
              </ul>
            </div>

            <div>
              <h3 className="font-semibold mb-4">Topluluk</h3>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li><Link href="/articles" className="hover:text-foreground transition-colors">Makaleler</Link></li>
                <li><Link href="/authors" className="hover:text-foreground transition-colors">Yazarlar</Link></li>
                <li><Link href="/forum" className="hover:text-foreground transition-colors">Forum</Link></li>
              </ul>
            </div>

            <div>
              <h3 className="font-semibold mb-4">Destek</h3>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li><Link href="/help" className="hover:text-foreground transition-colors">Yardım</Link></li>
                <li><Link href="/contact" className="hover:text-foreground transition-colors">İletişim</Link></li>
                <li><Link href="/privacy" className="hover:text-foreground transition-colors">Gizlilik</Link></li>
              </ul>
            </div>

          </div>
          
          <div className="border-t mt-8 pt-8 text-center text-sm text-muted-foreground">
            <p>&copy; 2025 Writer Vault. Tüm hakları saklıdır.</p>
          </div>
        </div>
      </footer>

    </div>
  )
}