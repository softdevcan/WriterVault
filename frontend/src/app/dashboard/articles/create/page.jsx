// src/app/dashboard/articles/create/page.jsx
'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { toast } from 'react-hot-toast'
import { useMutation, useQueryClient } from '@tanstack/react-query'

import ArticleForm from '@/components/articles/ArticleForm'
import api, { articleQueryKeys } from '@/lib/api'
import useAuthStore from '@/store/auth'

export default function CreateArticlePage() {
  const router = useRouter()
  const queryClient = useQueryClient()
  const { user } = useAuthStore()
  const [isLoading, setIsLoading] = useState(false)

  // Create article mutation
  const createArticleMutation = useMutation({
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

      return api.createArticle(payload)
    },
    onSuccess: (data) => {
      // Invalidate and refetch articles
      queryClient.invalidateQueries({ queryKey: articleQueryKeys.all })
      
      toast.success('Makale başarıyla oluşturuldu!')
      
      // Redirect to article view or dashboard
      if (data.status === 'published') {
        router.push(`/articles/${data.slug}`)
      } else {
        router.push('/dashboard/articles')
      }
    },
    onError: (error) => {
      console.error('Article creation error:', error)
      toast.error(`Makale oluşturulamadı: ${error.message}`)
    },
  })

  const handleSubmit = async (articleData) => {
    setIsLoading(true)
    try {
      await createArticleMutation.mutateAsync(articleData)
    } finally {
      setIsLoading(false)
    }
  }

  // Redirect if not authenticated
  if (!user) {
    router.push('/auth/login')
    return null
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto py-8">
        <ArticleForm
          mode="create"
          onSubmit={handleSubmit}
          isLoading={isLoading || createArticleMutation.isPending}
        />
      </div>
    </div>
  )
}