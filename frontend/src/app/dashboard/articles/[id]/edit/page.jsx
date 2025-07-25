// src/app/dashboard/articles/[id]/edit/page.jsx
'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useParams } from 'next/navigation'
import { toast } from 'react-hot-toast'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import ArticleForm from '@/components/articles/ArticleForm'
import api, { articleQueryKeys } from '@/lib/api'
import useAuthStore from '@/store/auth'
import { Skeleton } from '@/components/ui/skeleton'
import { Button } from '@/components/ui/button'
import { ArrowLeft, AlertCircle } from 'lucide-react'
import { Alert, AlertDescription } from '@/components/ui/alert'

export default function EditArticlePage() {
  const router = useRouter()
  const params = useParams()
  const queryClient = useQueryClient()
  const { user } = useAuthStore()
  const [isLoading, setIsLoading] = useState(false)
  
  const articleId = parseInt(params.id)

  // Fetch article data
  const {
    data: article,
    isLoading: articleLoading,
    error: articleError,
    refetch
  } = useQuery({
    queryKey: articleQueryKeys.detail(articleId),
    queryFn: () => api.getArticle(articleId),
    enabled: !!articleId && !!user,
    retry: 1,
  })

  // Update article mutation
  const updateArticleMutation = useMutation({
    mutationFn: async (articleData) => {
      // Transform the data for API
      const payload = {
        title: articleData.title,
        summary: articleData.summary || null,
        content: articleData.content.html,
        meta_description: articleData.meta_description || null,
        meta_keywords: articleData.meta_keywords || null,
        category_id: articleData.category_id || null,
        collection_id: articleData.collection_id || null,
        order_in_collection: articleData.order_in_collection || null,
        allow_comments: articleData.allow_comments,
        is_featured: articleData.is_featured,
        status: articleData.status,
        scheduled_at: articleData.scheduled_at || null,
        tag_names: articleData.tag_names || [],
      }

      return api.updateArticle(articleId, payload)
    },
    onSuccess: (data) => {
      // Invalidate and refetch articles
      queryClient.invalidateQueries({ queryKey: articleQueryKeys.all })
      queryClient.setQueryData(articleQueryKeys.detail(articleId), data)
      
      toast.success('Makale başarıyla güncellendi!')
      
      // Redirect based on status
      if (data.status === 'published') {
        router.push(`/articles/${data.slug}`)
      } else {
        router.push('/dashboard/articles')
      }
    },
    onError: (error) => {
      console.error('Article update error:', error)
      toast.error(`Makale güncellenemedi: ${error.message}`)
    },
  })

  const handleSubmit = async (articleData) => {
    setIsLoading(true)
    try {
      await updateArticleMutation.mutateAsync(articleData)
    } finally {
      setIsLoading(false)
    }
  }

  // Check permissions
  useEffect(() => {
    if (article && user && article.author.id !== user.id) {
      toast.error('Bu makaleyi düzenleme yetkiniz yok')
      router.push('/dashboard/articles')
    }
  }, [article, user, router])

  // Redirect if not authenticated
  if (!user) {
    router.push('/auth/login')
    return null
  }

  // Loading state
  if (articleLoading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="container mx-auto py-8">
          <div className="max-w-6xl mx-auto p-6 space-y-6">
            
            {/* Header skeleton */}
            <div className="flex justify-between items-center">
              <div>
                <Skeleton className="h-8 w-64 mb-2" />
                <Skeleton className="h-4 w-48" />
              </div>
              <div className="flex gap-2">
                <Skeleton className="h-10 w-24" />
                <Skeleton className="h-10 w-32" />
                <Skeleton className="h-10 w-24" />
              </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
              
              {/* Main content skeleton */}
              <div className="lg:col-span-3 space-y-6">
                <Skeleton className="h-12 w-full" />
                <Skeleton className="h-24 w-full" />
                <Skeleton className="h-96 w-full" />
              </div>

              {/* Sidebar skeleton */}
              <div className="space-y-6">
                {[...Array(3)].map((_, i) => (
                  <div key={i} className="border rounded-lg p-4 space-y-4">
                    <Skeleton className="h-6 w-32" />
                    <Skeleton className="h-10 w-full" />
                    <Skeleton className="h-10 w-full" />
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    )
  }

  // Error state
  if (articleError) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="container mx-auto py-8">
          <div className="max-w-2xl mx-auto">
            
            {/* Back button */}
            <Button
              variant="ghost"
              onClick={() => router.push('/dashboard/articles')}
              className="mb-6"
            >
              <ArrowLeft className="w-4 h-4 mr-2" />
              Makalelere Dön
            </Button>

            <Alert>
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>
                Makale yüklenirken bir hata oluştu. 
                {articleError.message.includes('404') 
                  ? ' Makale bulunamadı.' 
                  : ' Lütfen tekrar deneyin.'
                }
              </AlertDescription>
            </Alert>

            <div className="mt-6 flex gap-4">
              <Button onClick={() => refetch()}>
                Tekrar Dene
              </Button>
              <Button 
                variant="outline" 
                onClick={() => router.push('/dashboard/articles')}
              >
                Makalelere Dön
              </Button>
            </div>
          </div>
        </div>
      </div>
    )
  }

  // Permission check
  if (article && user && article.author.id !== user.id) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="container mx-auto py-8">
          <div className="max-w-2xl mx-auto">
            <Alert>
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>
                Bu makaleyi düzenleme yetkiniz yok.
              </AlertDescription>
            </Alert>
            
            <div className="mt-6">
              <Button onClick={() => router.push('/dashboard/articles')}>
                <ArrowLeft className="w-4 h-4 mr-2" />
                Makalelere Dön
              </Button>
            </div>
          </div>
        </div>
      </div>
    )
  }

  // Transform article data for form
  const formData = article ? {
    title: article.title,
    summary: article.summary,
    content: {
      html: article.content,
      json: null,
    },
    meta_description: article.meta_description,
    meta_keywords: article.meta_keywords,
    category_id: article.category?.id,
    collection_id: article.collection?.id,
    order_in_collection: article.order_in_collection,
    allow_comments: article.allow_comments,
    is_featured: article.is_featured,
    status: article.status,
    scheduled_at: article.scheduled_at ? 
      new Date(article.scheduled_at).toISOString().slice(0, 16) : '',
    tag_names: article.tags?.map(tag => tag.name) || [],
  } : null

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto py-8">
        
        {/* Back button */}
        <div className="max-w-6xl mx-auto px-6 mb-6">
          <Button
            variant="ghost"
            onClick={() => router.push('/dashboard/articles')}
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Makalelere Dön
          </Button>
        </div>

        {article && formData && (
          <ArticleForm
            mode="edit"
            initialData={formData}
            onSubmit={handleSubmit}
            isLoading={isLoading || updateArticleMutation.isPending}
          />
        )}
      </div>
    </div>
  )
}