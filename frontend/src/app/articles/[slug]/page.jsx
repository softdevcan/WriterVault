// src/app/articles/[slug]/page.jsx
'use client'

import { useState, useEffect } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { useQuery } from '@tanstack/react-query'
import { toast } from 'react-hot-toast'
import {
  Calendar,
  Clock,
  Eye,
  Heart,
  Share2,
  BookOpen,
  Tag,
  User,
  ArrowLeft,
  Edit,
  MessageCircle,
  Facebook,
  Twitter,
  Linkedin,
  Copy
} from 'lucide-react'

import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent } from '@/components/ui/card'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { Separator } from '@/components/ui/separator'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { Skeleton } from '@/components/ui/skeleton'
import { Alert, AlertDescription } from '@/components/ui/alert'

import api, { articleQueryKeys } from '@/lib/api'
import useAuthStore from '@/store/auth'

// Format date helper
const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('tr-TR', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

// Reading time calculator
const calculateReadingTime = (text) => {
  const wordsPerMinute = 200
  const words = text.split(/\s+/).length
  const minutes = Math.ceil(words / wordsPerMinute)
  return minutes
}

// Share functions
const shareArticle = {
  facebook: (url, title) => {
    window.open(`https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(url)}`, '_blank')
  },
  twitter: (url, title) => {
    window.open(`https://twitter.com/intent/tweet?url=${encodeURIComponent(url)}&text=${encodeURIComponent(title)}`, '_blank')
  },
  linkedin: (url, title) => {
    window.open(`https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(url)}`, '_blank')
  },
  copy: (url) => {
    navigator.clipboard.writeText(url).then(() => {
      toast.success('Link kopyalandı!')
    })
  }
}

export default function ArticleViewPage() {
  const params = useParams()
  const router = useRouter()
  const { user } = useAuthStore()
  const [isLiked, setIsLiked] = useState(false)
  const [likeCount, setLikeCount] = useState(0)
  
  const slug = params.slug

  // Fetch article by slug
  const {
    data: article,
    isLoading,
    error
  } = useQuery({
    queryKey: ['article', 'slug', slug],
    queryFn: () => api.getArticleBySlug(slug),
    retry: 1,
  })

  // Update view count and like status on mount
  useEffect(() => {
    if (article) {
      setLikeCount(article.like_count)
      // TODO: Check if user has liked this article
      // setIsLiked(checkUserLike())
    }
  }, [article])

  const handleLike = async () => {
    if (!user) {
      toast.error('Beğenmek için giriş yapmalısınız')
      return
    }

    try {
      // TODO: Implement like API
      setIsLiked(!isLiked)
      setLikeCount(prev => isLiked ? prev - 1 : prev + 1)
      toast.success(isLiked ? 'Beğeni kaldırıldı' : 'Makale beğenildi')
    } catch (error) {
      toast.error('Bir hata oluştu')
    }
  }

  const canEdit = user && article && article.author.id === user.id

  // Generate current URL for sharing
  const currentUrl = typeof window !== 'undefined' ? window.location.href : ''

  // Loading state
  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="max-w-4xl mx-auto py-8 px-6">
          
          {/* Header skeleton */}
          <div className="mb-8">
            <Skeleton className="h-10 w-3/4 mb-4" />
            <Skeleton className="h-6 w-full mb-2" />
            <Skeleton className="h-6 w-2/3 mb-4" />
            
            <div className="flex items-center gap-4 mb-6">
              <Skeleton className="w-12 h-12 rounded-full" />
              <div>
                <Skeleton className="h-4 w-32 mb-1" />
                <Skeleton className="h-3 w-24" />
              </div>
            </div>
          </div>

          {/* Content skeleton */}
          <div className="space-y-4">
            {[...Array(8)].map((_, i) => (
              <Skeleton key={i} className="h-4 w-full" />
            ))}
          </div>
        </div>
      </div>
    )
  }

  // Error state
  if (error) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="max-w-2xl mx-auto py-8 px-6">
          <Button
            variant="ghost"
            onClick={() => router.back()}
            className="mb-6"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Geri Dön
          </Button>

          <Alert>
            <AlertDescription>
              {error.message.includes('404') 
                ? 'Makale bulunamadı.' 
                : 'Makale yüklenirken bir hata oluştu.'
              }
            </AlertDescription>
          </Alert>

          <div className="mt-6">
            <Button onClick={() => router.push('/')}>
              Ana Sayfaya Dön
            </Button>
          </div>
        </div>
      </div>
    )
  }

  if (!article) return null

  const readingTime = calculateReadingTime(article.content)

  return (
    <div className="min-h-screen bg-gray-50">
      
      {/* Navigation */}
      <div className="bg-white border-b sticky top-0 z-10">
        <div className="max-w-4xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <Button
              variant="ghost"
              onClick={() => router.back()}
            >
              <ArrowLeft className="w-4 h-4 mr-2" />
              Geri
            </Button>

            <div className="flex items-center gap-2">
              {canEdit && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => router.push(`/dashboard/articles/${article.id}/edit`)}
                >
                  <Edit className="w-4 h-4 mr-2" />
                  Düzenle
                </Button>
              )}

              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="outline" size="sm">
                    <Share2 className="w-4 h-4 mr-2" />
                    Paylaş
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end">
                  <DropdownMenuItem 
                    onClick={() => shareArticle.facebook(currentUrl, article.title)}
                  >
                    <Facebook className="w-4 h-4 mr-2" />
                    Facebook
                  </DropdownMenuItem>
                  <DropdownMenuItem 
                    onClick={() => shareArticle.twitter(currentUrl, article.title)}
                  >
                    <Twitter className="w-4 h-4 mr-2" />
                    Twitter
                  </DropdownMenuItem>
                  <DropdownMenuItem 
                    onClick={() => shareArticle.linkedin(currentUrl, article.title)}
                  >
                    <Linkedin className="w-4 h-4 mr-2" />
                    LinkedIn
                  </DropdownMenuItem>
                  <DropdownMenuItem 
                    onClick={() => shareArticle.copy(currentUrl)}
                  >
                    <Copy className="w-4 h-4 mr-2" />
                    Linki Kopyala
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
          </div>
        </div>
      </div>

      <article className="max-w-4xl mx-auto py-8 px-6">
        
        {/* Article Header */}
        <header className="mb-8">
          
          {/* Category & Collection */}
          <div className="flex items-center gap-2 mb-4">
            {article.category && (
              <Badge variant="secondary" className="flex items-center gap-1">
                <Tag className="w-3 h-3" />
                {article.category.name}
              </Badge>
            )}
            {article.collection && (
              <Badge variant="outline" className="flex items-center gap-1">
                <BookOpen className="w-3 h-3" />
                {article.collection.title}
              </Badge>
            )}
          </div>

          {/* Title */}
          <h1 className="text-4xl font-bold text-gray-900 mb-4 leading-tight">
            {article.title}
          </h1>

          {/* Summary */}
          {article.summary && (
            <p className="text-xl text-gray-600 mb-6 leading-relaxed">
              {article.summary}
            </p>
          )}

          {/* Meta info */}
          <div className="flex flex-wrap items-center gap-6 text-sm text-gray-500 mb-6">
            <div className="flex items-center gap-2">
              <Calendar className="w-4 h-4" />
              {formatDate(article.published_at || article.created_at)}
            </div>
            <div className="flex items-center gap-2">
              <Clock className="w-4 h-4" />
              {readingTime} dk okuma
            </div>
            <div className="flex items-center gap-2">
              <Eye className="w-4 h-4" />
              {article.view_count} görüntüleme
            </div>
          </div>

          {/* Author */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Avatar className="w-12 h-12">
                <AvatarImage src={article.author.avatar_url} alt={article.author.username} />
                <AvatarFallback>
                  {article.author.username.charAt(0).toUpperCase()}
                </AvatarFallback>
              </Avatar>
              <div>
                <p className="font-medium text-gray-900">{article.author.username}</p>
                {article.author.full_name && (
                  <p className="text-sm text-gray-500">{article.author.full_name}</p>
                )}
              </div>
            </div>

            {/* Engagement */}
            <div className="flex items-center gap-4">
              <Button
                variant={isLiked ? "default" : "outline"}
                size="sm"
                onClick={handleLike}
                className="flex items-center gap-2"
              >
                <Heart className={`w-4 h-4 ${isLiked ? 'fill-current' : ''}`} />
                {likeCount}
              </Button>
              
              {article.allow_comments && (
                <Button variant="outline" size="sm">
                  <MessageCircle className="w-4 h-4 mr-2" />
                  {article.comment_count}
                </Button>
              )}
            </div>
          </div>
        </header>

        <Separator className="mb-8" />

        {/* Article Content */}
        <div className="mb-12">
          <div 
            className="prose prose-lg prose-gray max-w-none"
            dangerouslySetInnerHTML={{ __html: article.content }}
            style={{
              fontFamily: "'Merriweather', Georgia, serif",
              lineHeight: '1.8',
              fontSize: '18px'
            }}
          />
        </div>

        {/* Tags */}
        {article.tags && article.tags.length > 0 && (
          <div className="mb-8">
            <h3 className="text-lg font-semibold mb-3">Etiketler</h3>
            <div className="flex flex-wrap gap-2">
              {article.tags.map((tag) => (
                <Badge key={tag.id} variant="secondary" className="cursor-pointer">
                  #{tag.name}
                </Badge>
              ))}
            </div>
          </div>
        )}

        <Separator className="mb-8" />

        {/* Author Info Card */}
        <Card className="mb-8">
          <CardContent className="p-6">
            <div className="flex items-start gap-4">
              <Avatar className="w-16 h-16">
                <AvatarImage src={article.author.avatar_url} alt={article.author.username} />
                <AvatarFallback className="text-lg">
                  {article.author.username.charAt(0).toUpperCase()}
                </AvatarFallback>
              </Avatar>
              <div className="flex-1">
                <h3 className="text-xl font-semibold mb-1">{article.author.username}</h3>
                {article.author.full_name && (
                  <p className="text-gray-600 mb-2">{article.author.full_name}</p>
                )}
                <p className="text-gray-600 text-sm">
                  Bu yazarın diğer makalelerini görüntülemek için profile tıklayın.
                </p>
                <Button 
                  variant="outline" 
                  size="sm" 
                  className="mt-3"
                  onClick={() => router.push(`/authors/${article.author.username}`)}
                >
                  <User className="w-4 h-4 mr-2" />
                  Profile Git
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Related Articles from Collection */}
        {article.collection && (
          <Card>
            <CardContent className="p-6">
              <h3 className="text-xl font-semibold mb-4 flex items-center gap-2">
                <BookOpen className="w-5 h-5" />
                {article.collection.title} Koleksiyonundan
              </h3>
              <p className="text-gray-600 text-sm mb-4">
                Bu makale "{article.collection.title}" koleksiyonunun parçasıdır.
              </p>
              <Button 
                variant="outline"
                onClick={() => router.push(`/collections/${article.collection.slug}`)}
              >
                Koleksiyonu Görüntüle
              </Button>
            </CardContent>
          </Card>
        )}

      </article>
    </div>
  )
}