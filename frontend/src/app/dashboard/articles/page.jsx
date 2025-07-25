// src/app/dashboard/articles/page.jsx
'use client'

import { useState, useMemo } from 'react'
import { useRouter } from 'next/navigation'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { toast } from 'react-hot-toast'
import {
  Plus,
  Search,
  Filter,
  Edit,
  Eye,
  Trash2,
  MoreHorizontal,
  Calendar,
  FileText,
  TrendingUp,
  BookOpen,
  Settings
} from 'lucide-react'

import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from '@/components/ui/alert-dialog'

import api, { articleQueryKeys } from '@/lib/api'
import useAuthStore from '@/store/auth'

// Status badge styling
const getStatusBadge = (status) => {
  const styles = {
    draft: 'bg-gray-100 text-gray-800',
    published: 'bg-green-100 text-green-800',
    archived: 'bg-red-100 text-red-800',
    scheduled: 'bg-blue-100 text-blue-800',
  }
  
  const labels = {
    draft: 'Taslak',
    published: 'Yayında',
    archived: 'Arşiv',
    scheduled: 'Zamanlanmış',
  }

  return (
    <Badge className={styles[status] || styles.draft}>
      {labels[status] || status}
    </Badge>
  )
}

export default function ArticlesDashboard() {
  const router = useRouter()
  const queryClient = useQueryClient()
  const { user } = useAuthStore()
  
  // Filters state
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState('all')
  const [sortBy, setSortBy] = useState('created_at')
  const [sortOrder, setSortOrder] = useState('desc')
  
  // Pagination
  const [page, setPage] = useState(1)
  const limit = 20

  // Build query parameters
  const queryParams = useMemo(() => ({
    search: search || undefined,
    status: statusFilter !== 'all' ? statusFilter : undefined,
    sort_by: sortBy,
    sort_order: sortOrder,
    skip: (page - 1) * limit,
    limit,
  }), [search, statusFilter, sortBy, sortOrder, page, limit])

  // Fetch user's articles
  const {
    data: articlesData,
    isLoading,
    error,
    refetch
  } = useQuery({
    queryKey: [...articleQueryKeys.user(user?.id || 0), queryParams],
    queryFn: () => api.getUserArticles(user?.id, queryParams),
    enabled: !!user?.id,
    keepPreviousData: true,
  })

  // Delete article mutation
  const deleteArticleMutation = useMutation({
    mutationFn: (articleId) => api.deleteArticle(articleId),
    onSuccess: () => {
      toast.success('Makale silindi')
      queryClient.invalidateQueries({ queryKey: articleQueryKeys.all })
    },
    onError: (error) => {
      toast.error(`Silme işlemi başarısız: ${error.message}`)
    },
  })

  // Quick status update mutation
  const updateStatusMutation = useMutation({
    mutationFn: ({ articleId, status }) => api.updateArticleStatus(articleId, status),
    onSuccess: () => {
      toast.success('Durum güncellendi')
      queryClient.invalidateQueries({ queryKey: articleQueryKeys.all })
    },
    onError: (error) => {
      toast.error(`Güncelleme başarısız: ${error.message}`)
    },
  })

  // Handle article actions
  const handleEdit = (articleId) => {
    router.push(`/dashboard/articles/${articleId}/edit`)
  }

  const handleView = (articleSlug) => {
    router.push(`/articles/${articleSlug}`)
  }

  const handleDelete = (articleId) => {
    deleteArticleMutation.mutate(articleId)
  }

  const handleQuickPublish = (articleId) => {
    updateStatusMutation.mutate({ articleId, status: 'published' })
  }

  const handleQuickUnpublish = (articleId) => {
    updateStatusMutation.mutate({ articleId, status: 'draft' })
  }

  // Calculate stats
  const stats = useMemo(() => {
    if (!articlesData?.articles) return null

    const articles = articlesData.articles
    return {
      total: articles.length,
      published: articles.filter(a => a.status === 'published').length,
      drafts: articles.filter(a => a.status === 'draft').length,
      totalViews: articles.reduce((sum, a) => sum + a.view_count, 0),
    }
  }, [articlesData])

  if (!user) {
    router.push('/auth/login')
    return null
  }

  return (
    <div className="container mx-auto py-8 space-y-8">
      
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Makalelerim</h1>
          <p className="text-gray-600 mt-1">
            Makalelerinizi yönetin ve yeni içerik oluşturun
          </p>
        </div>
        <Button onClick={() => router.push('/dashboard/articles/create')}>
          <Plus className="w-4 h-4 mr-2" />
          Yeni Makale
        </Button>
      </div>

      {/* Stats Cards */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Toplam</p>
                  <p className="text-2xl font-bold">{stats.total}</p>
                </div>
                <FileText className="w-8 h-8 text-blue-600" />
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Yayında</p>
                  <p className="text-2xl font-bold text-green-600">{stats.published}</p>
                </div>
                <Eye className="w-8 h-8 text-green-600" />
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Taslak</p>
                  <p className="text-2xl font-bold text-gray-600">{stats.drafts}</p>
                </div>
                <Edit className="w-8 h-8 text-gray-600" />
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Görüntüleme</p>
                  <p className="text-2xl font-bold text-purple-600">{stats.totalViews}</p>
                </div>
                <TrendingUp className="w-8 h-8 text-purple-600" />
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Filters */}
      <Card>
        <CardContent className="p-6">
          <div className="flex flex-col md:flex-row gap-4">
            
            {/* Search */}
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                <Input
                  placeholder="Makale ara..."
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>

            {/* Status Filter */}
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-48">
                <SelectValue placeholder="Durum" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Tüm Durumlar</SelectItem>
                <SelectItem value="draft">Taslak</SelectItem>
                <SelectItem value="published">Yayında</SelectItem>
                <SelectItem value="scheduled">Zamanlanmış</SelectItem>
                <SelectItem value="archived">Arşiv</SelectItem>
              </SelectContent>
            </Select>

            {/* Sort */}
            <Select value={`${sortBy}-${sortOrder}`} onValueChange={(value) => {
              const [newSortBy, newSortOrder] = value.split('-')
              setSortBy(newSortBy)
              setSortOrder(newSortOrder)
            }}>
              <SelectTrigger className="w-48">
                <SelectValue placeholder="Sırala" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="created_at-desc">En Yeni</SelectItem>
                <SelectItem value="created_at-asc">En Eski</SelectItem>
                <SelectItem value="updated_at-desc">Son Güncellenen</SelectItem>
                <SelectItem value="title-asc">Başlık (A-Z)</SelectItem>
                <SelectItem value="view_count-desc">En Çok Görüntülenen</SelectItem>
              </SelectContent>
            </Select>

          </div>
        </CardContent>
      </Card>

      {/* Articles Table */}
      <Card>
        <CardHeader>
          <CardTitle>Makaleler</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="space-y-4">
              {[...Array(5)].map((_, i) => (
                <div key={i} className="animate-pulse">
                  <div className="h-16 bg-gray-200 rounded"></div>
                </div>
              ))}
            </div>
          ) : error ? (
            <div className="text-center py-8">
              <p className="text-red-500">Makaleler yüklenirken hata oluştu</p>
              <Button onClick={() => refetch()} variant="outline" className="mt-2">
                Tekrar Dene
              </Button>
            </div>
          ) : !articlesData?.articles?.length ? (
            <div className="text-center py-12">
              <BookOpen className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-600 mb-2">
                Henüz makale yok
              </h3>
              <p className="text-gray-500 mb-4">
                İlk makalenizi oluşturarak başlayın
              </p>
              <Button onClick={() => router.push('/dashboard/articles/create')}>
                <Plus className="w-4 h-4 mr-2" />
                Yeni Makale
              </Button>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Başlık</TableHead>
                  <TableHead>Durum</TableHead>
                  <TableHead>Kategori</TableHead>
                  <TableHead>Görüntüleme</TableHead>
                  <TableHead>Tarih</TableHead>
                  <TableHead className="w-16"></TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {articlesData.articles.map((article) => (
                  <TableRow key={article.id}>
                    <TableCell className="font-medium">
                      <div>
                        <p className="font-medium">{article.title}</p>
                        {article.summary && (
                          <p className="text-sm text-gray-500 mt-1 truncate max-w-md">
                            {article.summary}
                          </p>
                        )}
                      </div>
                    </TableCell>
                    <TableCell>
                      {getStatusBadge(article.status)}
                    </TableCell>
                    <TableCell>
                      {article.category ? (
                        <Badge variant="outline">{article.category.name}</Badge>
                      ) : (
                        <span className="text-gray-400">-</span>
                      )}
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-1">
                        <Eye className="w-4 h-4 text-gray-400" />
                        {article.view_count}
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="text-sm">
                        <p>{new Date(article.created_at).toLocaleDateString('tr-TR')}</p>
                        {article.published_at && article.status === 'published' && (
                          <p className="text-gray-500">
                            Yayın: {new Date(article.published_at).toLocaleDateString('tr-TR')}
                          </p>
                        )}
                      </div>
                    </TableCell>
                    <TableCell>
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" size="sm">
                            <MoreHorizontal className="w-4 h-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <DropdownMenuLabel>İşlemler</DropdownMenuLabel>
                          <DropdownMenuSeparator />
                          
                          <DropdownMenuItem onClick={() => handleEdit(article.id)}>
                            <Edit className="w-4 h-4 mr-2" />
                            Düzenle
                          </DropdownMenuItem>
                          
                          {article.status === 'published' && (
                            <DropdownMenuItem onClick={() => handleView(article.slug)}>
                              <Eye className="w-4 h-4 mr-2" />
                              Görüntüle
                            </DropdownMenuItem>
                          )}
                          
                          <DropdownMenuSeparator />
                          
                          {article.status === 'draft' && (
                            <DropdownMenuItem onClick={() => handleQuickPublish(article.id)}>
                              <Calendar className="w-4 h-4 mr-2" />
                              Yayınla
                            </DropdownMenuItem>
                          )}
                          
                          {article.status === 'published' && (
                            <DropdownMenuItem onClick={() => handleQuickUnpublish(article.id)}>
                              <Settings className="w-4 h-4 mr-2" />
                              Taslağa Çevir
                            </DropdownMenuItem>
                          )}
                          
                          <DropdownMenuSeparator />
                          
                          <AlertDialog>
                            <AlertDialogTrigger asChild>
                              <DropdownMenuItem 
                                className="text-red-600 focus:text-red-600"
                                onSelect={(e) => e.preventDefault()}
                              >
                                <Trash2 className="w-4 h-4 mr-2" />
                                Sil
                              </DropdownMenuItem>
                            </AlertDialogTrigger>
                            <AlertDialogContent>
                              <AlertDialogHeader>
                                <AlertDialogTitle>Makaleyi sil?</AlertDialogTitle>
                                <AlertDialogDescription>
                                  Bu işlem geri alınamaz. Makale kalıcı olarak silinecek.
                                </AlertDialogDescription>
                              </AlertDialogHeader>
                              <AlertDialogFooter>
                                <AlertDialogCancel>İptal</AlertDialogCancel>
                                <AlertDialogAction
                                  onClick={() => handleDelete(article.id)}
                                  className="bg-red-600 hover:bg-red-700"
                                >
                                  Sil
                                </AlertDialogAction>
                              </AlertDialogFooter>
                            </AlertDialogContent>
                          </AlertDialog>
                          
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

    </div>
  )
}