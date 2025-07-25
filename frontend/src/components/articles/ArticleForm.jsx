// src/components/articles/ArticleForm.jsx
'use client'

import { useState, useEffect, useCallback } from 'react'
import { useForm, Controller } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useRouter } from 'next/navigation'
import { toast } from 'react-hot-toast'

import TipTapEditor from '@/components/editor/TipTapEditor'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Label } from '@/components/ui/label'
import { Switch } from '@/components/ui/switch'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Separator } from '@/components/ui/separator'
import { 
  Save, 
  Eye, 
  Send, 
  Calendar,
  Hash,
  X,
  Plus,
  BookOpen,
  Folder
} from 'lucide-react'

// Form validation schema
const articleSchema = z.object({
  title: z.string()
    .min(1, 'Başlık gereklidir')
    .max(255, 'Başlık çok uzun'),
  summary: z.string()
    .max(500, 'Özet çok uzun')
    .optional(),
  content: z.object({
    html: z.string().min(1, 'İçerik gereklidir'),
    json: z.any(),
  }),
  meta_description: z.string()
    .max(160, 'Meta açıklama çok uzun')
    .optional(),
  meta_keywords: z.string()
    .max(255, 'Meta anahtar kelimeler çok uzun')
    .optional(),
  category_id: z.number().positive().optional(),
  collection_id: z.number().positive().optional(),
  order_in_collection: z.number().positive().optional(),
  allow_comments: z.boolean().default(true),
  is_featured: z.boolean().default(false),
  status: z.enum(['draft', 'published', 'archived', 'scheduled']).default('draft'),
  scheduled_at: z.string().optional(),
  tag_names: z.array(z.string()).optional(),
})

const ArticleForm = ({ 
  initialData = null, 
  onSubmit, 
  isLoading = false,
  mode = 'create' // 'create' | 'edit'
}) => {
  const router = useRouter()
  const [categories, setCategories] = useState([])
  const [collections, setCollections] = useState([])
  const [tags, setTags] = useState([])
  const [newTag, setNewTag] = useState('')
  const [lastSaved, setLastSaved] = useState(null)
  const [previewMode, setPreviewMode] = useState(false)

  // Form setup
  const {
    control,
    handleSubmit,
    watch,
    setValue,
    formState: { errors, isDirty }
  } = useForm({
    resolver: zodResolver(articleSchema),
    defaultValues: {
      title: initialData?.title || '',
      summary: initialData?.summary || '',
      content: {
        html: initialData?.content || '',
        json: null,
      },
      meta_description: initialData?.meta_description || '',
      meta_keywords: initialData?.meta_keywords || '',
      category_id: initialData?.category_id || undefined,
      collection_id: initialData?.collection_id || undefined,
      order_in_collection: initialData?.order_in_collection || undefined,
      allow_comments: initialData?.allow_comments ?? true,
      is_featured: initialData?.is_featured ?? false,
      status: initialData?.status || 'draft',
      scheduled_at: initialData?.scheduled_at || '',
      tag_names: initialData?.tag_names || [],
    }
  })

  const watchedValues = watch()

  // Load categories and collections
  useEffect(() => {
    const loadData = async () => {
      try {
        // Load categories
        const categoriesRes = await fetch('/api/v1/categories/', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        })
        if (categoriesRes.ok) {
          const categoriesData = await categoriesRes.json()
          setCategories(categoriesData)
        }

        // Load user's collections
        const collectionsRes = await fetch('/api/v1/collections/', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        })
        if (collectionsRes.ok) {
          const collectionsData = await collectionsRes.json()
          setCollections(collectionsData)
        }
      } catch (error) {
        console.error('Error loading data:', error)
      }
    }

    loadData()
  }, [])

  // Auto-save functionality
  const handleAutoSave = useCallback(async (content) => {
    if (!isDirty || mode === 'create') return

    try {
      const formData = {
        ...watchedValues,
        content: content
      }

      const response = await fetch(`/api/v1/articles/${initialData?.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(formData)
      })

      if (response.ok) {
        setLastSaved(new Date())
        toast.success('Otomatik kaydedildi', { duration: 2000 })
      }
    } catch (error) {
      console.error('Auto-save error:', error)
    }
  }, [watchedValues, isDirty, mode, initialData?.id])

  // Handle tag management
  const addTag = () => {
    if (newTag.trim() && !tags.includes(newTag.trim())) {
      const updatedTags = [...tags, newTag.trim()]
      setTags(updatedTags)
      setValue('tag_names', updatedTags)
      setNewTag('')
    }
  }

  const removeTag = (tagToRemove) => {
    const updatedTags = tags.filter(tag => tag !== tagToRemove)
    setTags(updatedTags)
    setValue('tag_names', updatedTags)
  }

  // Handle form submission
  const onSubmitForm = async (data) => {
    try {
      await onSubmit(data)
      if (mode === 'create') {
        toast.success('Makale başarıyla oluşturuldu!')
        router.push('/dashboard/articles')
      } else {
        toast.success('Makale başarıyla güncellendi!')
      }
    } catch (error) {
      toast.error('Bir hata oluştu: ' + error.message)
    }
  }

  // Quick actions
  const handleQuickSave = () => {
    setValue('status', 'draft')
    handleSubmit(onSubmitForm)()
  }

  const handlePublish = () => {
    setValue('status', 'published')
    handleSubmit(onSubmitForm)()
  }

  const handleSchedule = () => {
    setValue('status', 'scheduled')
    handleSubmit(onSubmitForm)()
  }

  return (
    <div className="max-w-6xl mx-auto p-6">
      <form onSubmit={handleSubmit(onSubmitForm)} className="space-y-6">
        
        {/* Header */}
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold">
              {mode === 'create' ? 'Yeni Makale' : 'Makaleyi Düzenle'}
            </h1>
            {lastSaved && (
              <p className="text-sm text-gray-500 mt-1">
                Son kaydedilme: {lastSaved.toLocaleTimeString('tr-TR')}
              </p>
            )}
          </div>
          
          <div className="flex gap-2">
            <Button
              type="button"
              variant="outline"
              onClick={() => setPreviewMode(!previewMode)}
            >
              <Eye className="w-4 h-4 mr-2" />
              {previewMode ? 'Düzenle' : 'Önizle'}
            </Button>
            
            <Button
              type="button"
              variant="outline"
              onClick={handleQuickSave}
              disabled={isLoading}
            >
              <Save className="w-4 h-4 mr-2" />
              Taslak Kaydet
            </Button>
            
            <Button
              type="button"
              onClick={handlePublish}
              disabled={isLoading}
            >
              <Send className="w-4 h-4 mr-2" />
              Yayınla
            </Button>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          
          {/* Main Content */}
          <div className="lg:col-span-3 space-y-6">
            
            {/* Title */}
            <div className="space-y-2">
              <Label htmlFor="title">Başlık *</Label>
              <Controller
                name="title"
                control={control}
                render={({ field }) => (
                  <Input
                    {...field}
                    id="title"
                    placeholder="Makalenizin başlığını yazın..."
                    className="text-lg font-medium"
                    error={errors.title?.message}
                  />
                )}
              />
              {errors.title && (
                <p className="text-sm text-red-500">{errors.title.message}</p>
              )}
            </div>

            {/* Summary */}
            <div className="space-y-2">
              <Label htmlFor="summary">Özet</Label>
              <Controller
                name="summary"
                control={control}
                render={({ field }) => (
                  <Textarea
                    {...field}
                    id="summary"
                    placeholder="Makalenizin kısa özetini yazın..."
                    rows={3}
                  />
                )}
              />
              {errors.summary && (
                <p className="text-sm text-red-500">{errors.summary.message}</p>
              )}
            </div>

            {/* Content Editor */}
            <div className="space-y-2">
              <Label>İçerik *</Label>
              {previewMode ? (
                <Card>
                  <CardContent className="p-6">
                    <div 
                      className="prose prose-lg max-w-none"
                      dangerouslySetInnerHTML={{ 
                        __html: watchedValues.content?.html || '' 
                      }}
                    />
                  </CardContent>
                </Card>
              ) : (
                <Controller
                  name="content"
                  control={control}
                  render={({ field }) => (
                    <TipTapEditor
                      content={field.value?.html || ''}
                      onChange={(content) => field.onChange(content)}
                      onAutoSave={handleAutoSave}
                      placeholder="Makalenizi yazmaya başlayın..."
                      autoSave={mode === 'edit'}
                    />
                  )}
                />
              )}
              {errors.content && (
                <p className="text-sm text-red-500">{errors.content.message}</p>
              )}
            </div>

          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            
            {/* Publishing Options */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Yayın Ayarları</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                
                {/* Status */}
                <div className="space-y-2">
                  <Label>Durum</Label>
                  <Controller
                    name="status"
                    control={control}
                    render={({ field }) => (
                      <Select value={field.value} onValueChange={field.onChange}>
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="draft">Taslak</SelectItem>
                          <SelectItem value="published">Yayınlanmış</SelectItem>
                          <SelectItem value="scheduled">Zamanlanmış</SelectItem>
                          <SelectItem value="archived">Arşivlenmiş</SelectItem>
                        </SelectContent>
                      </Select>
                    )}
                  />
                </div>

                {/* Scheduled Date */}
                {watchedValues.status === 'scheduled' && (
                  <div className="space-y-2">
                    <Label>Yayın Tarihi</Label>
                    <Controller
                      name="scheduled_at"
                      control={control}
                      render={({ field }) => (
                        <Input
                          {...field}
                          type="datetime-local"
                          className="w-full"
                        />
                      )}
                    />
                  </div>
                )}

                <Separator />

                {/* Toggles */}
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <Label htmlFor="allow_comments">Yorumlara İzin Ver</Label>
                    <Controller
                      name="allow_comments"
                      control={control}
                      render={({ field }) => (
                        <Switch
                          id="allow_comments"
                          checked={field.value}
                          onCheckedChange={field.onChange}
                        />
                      )}
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <Label htmlFor="is_featured">Öne Çıkan</Label>
                    <Controller
                      name="is_featured"
                      control={control}
                      render={({ field }) => (
                        <Switch
                          id="is_featured"
                          checked={field.value}
                          onCheckedChange={field.onChange}
                        />
                      )}
                    />
                  </div>
                </div>

              </CardContent>
            </Card>

            {/* Organization */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Organizasyon</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                
                {/* Category */}
                <div className="space-y-2">
                  <Label className="flex items-center gap-2">
                    <Folder className="w-4 h-4" />
                    Kategori
                  </Label>
                  <Controller
                    name="category_id"
                    control={control}
                    render={({ field }) => (
                      <Select 
                        value={field.value?.toString()} 
                        onValueChange={(value) => field.onChange(parseInt(value))}
                      >
                        <SelectTrigger>
                          <SelectValue placeholder="Kategori seçin" />
                        </SelectTrigger>
                        <SelectContent>
                          {categories.map((category) => (
                            <SelectItem 
                              key={category.id} 
                              value={category.id.toString()}
                            >
                              {category.name}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    )}
                  />
                </div>

                {/* Collection */}
                <div className="space-y-2">
                  <Label className="flex items-center gap-2">
                    <BookOpen className="w-4 h-4" />
                    Koleksiyon
                  </Label>
                  <Controller
                    name="collection_id"
                    control={control}
                    render={({ field }) => (
                      <Select 
                        value={field.value?.toString()} 
                        onValueChange={(value) => field.onChange(parseInt(value))}
                      >
                        <SelectTrigger>
                          <SelectValue placeholder="Koleksiyon seçin" />
                        </SelectTrigger>
                        <SelectContent>
                          {collections.map((collection) => (
                            <SelectItem 
                              key={collection.id} 
                              value={collection.id.toString()}
                            >
                              {collection.title}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    )}
                  />
                </div>

                {/* Order in Collection */}
                {watchedValues.collection_id && (
                  <div className="space-y-2">
                    <Label>Koleksiyondaki Sırası</Label>
                    <Controller
                      name="order_in_collection"
                      control={control}
                      render={({ field }) => (
                        <Input
                          {...field}
                          type="number"
                          min="1"
                          placeholder="1"
                          onChange={(e) => field.onChange(parseInt(e.target.value))}
                        />
                      )}
                    />
                  </div>
                )}

                {/* Tags */}
                <div className="space-y-2">
                  <Label className="flex items-center gap-2">
                    <Hash className="w-4 h-4" />
                    Etiketler
                  </Label>
                  
                  {/* Add new tag */}
                  <div className="flex gap-2">
                    <Input
                      value={newTag}
                      onChange={(e) => setNewTag(e.target.value)}
                      placeholder="Etiket ekle..."
                      onKeyDown={(e) => {
                        if (e.key === 'Enter') {
                          e.preventDefault()
                          addTag()
                        }
                      }}
                    />
                    <Button
                      type="button"
                      size="sm"
                      onClick={addTag}
                      disabled={!newTag.trim()}
                    >
                      <Plus className="w-4 h-4" />
                    </Button>
                  </div>

                  {/* Display tags */}
                  {tags.length > 0 && (
                    <div className="flex flex-wrap gap-2">
                      {tags.map((tag, index) => (
                        <Badge key={index} variant="secondary" className="flex items-center gap-1">
                          {tag}
                          <button
                            type="button"
                            onClick={() => removeTag(tag)}
                            className="ml-1 hover:text-red-500"
                          >
                            <X className="w-3 h-3" />
                          </button>
                        </Badge>
                      ))}
                    </div>
                  )}
                </div>

              </CardContent>
            </Card>

            {/* SEO */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">SEO</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                
                <div className="space-y-2">
                  <Label htmlFor="meta_description">Meta Açıklama</Label>
                  <Controller
                    name="meta_description"
                    control={control}
                    render={({ field }) => (
                      <Textarea
                        {...field}
                        id="meta_description"
                        placeholder="Arama motorları için açıklama..."
                        rows={3}
                        maxLength={160}
                      />
                    )}
                  />
                  <p className="text-xs text-gray-500">
                    {watchedValues.meta_description?.length || 0}/160 karakter
                  </p>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="meta_keywords">Meta Anahtar Kelimeler</Label>
                  <Controller
                    name="meta_keywords"
                    control={control}
                    render={({ field }) => (
                      <Input
                        {...field}
                        id="meta_keywords"
                        placeholder="anahtar, kelime, virgül, ile, ayırın"
                      />
                    )}
                  />
                </div>

              </CardContent>
            </Card>

          </div>
        </div>

      </form>
    </div>
  )
}

export default ArticleForm