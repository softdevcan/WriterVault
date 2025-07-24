'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { 
  Trash2, 
  AlertTriangle, 
  Download, 
  Archive, 
  Shield,
  X,
  Check
} from 'lucide-react'
import useAuthStore from '../../store/auth'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Alert, AlertDescription } from '@/components/ui/alert'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'

export default function ProfileAccount({ user }) {
  const router = useRouter()
  const { logout } = useAuthStore()
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false)
  const [deactivateDialogOpen, setDeactivateDialogOpen] = useState(false)
  const [confirmationText, setConfirmationText] = useState('')
  const [isDeleting, setIsDeleting] = useState(false)
  const [isDeactivating, setIsDeactivating] = useState(false)

  const handleDeleteAccount = async () => {
    if (confirmationText !== user.username) return

    setIsDeleting(true)
    
    try {
      // TODO: API call to delete account
      console.log('Deleting account for:', user.username)
      
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 2000))
      
      // Logout and redirect
      logout()
      router.push('/auth/login?message=account-deleted')
      
    } catch (error) {
      console.error('Delete account failed:', error)
    } finally {
      setIsDeleting(false)
      setDeleteDialogOpen(false)
    }
  }

  const handleDeactivateAccount = async () => {
    setIsDeactivating(true)
    
    try {
      // TODO: API call to deactivate account
      console.log('Deactivating account for:', user.username)
      
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1500))
      
      // Logout and redirect
      logout()
      router.push('/auth/login?message=account-deactivated')
      
    } catch (error) {
      console.error('Deactivate account failed:', error)
    } finally {
      setIsDeactivating(false)
      setDeactivateDialogOpen(false)
    }
  }

  const handleDownloadData = () => {
    // TODO: Implement data download
    console.log('Downloading user data...')
    
    // Simulate download
    const data = {
      user: user,
      articles: [],
      comments: [],
      preferences: {},
      downloadDate: new Date().toISOString()
    }
    
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${user.username}-data.json`
    a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="space-y-6">
      {/* Warning Alert */}
      <Alert variant="destructive">
        <AlertTriangle className="h-4 w-4" />
        <AlertDescription>
          Bu bölümdeki işlemler geri alınamaz. Lütfen dikkatli olun.
        </AlertDescription>
      </Alert>

      {/* Data Download Card */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Download className="w-5 h-5" />
            <span>Veri İndirme</span>
          </CardTitle>
          <p className="text-sm text-muted-foreground">
            Hesabınızdaki tüm verileri JSON formatında indirin
          </p>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="p-4 bg-muted/30 rounded-lg">
              <h4 className="font-medium mb-2">İndirilecek Veriler:</h4>
              <ul className="text-sm text-muted-foreground space-y-1">
                <li>• Profil bilgileri</li>
                <li>• Yazılarınız ve içerikleri</li>
                <li>• Yorumlarınız</li>
                <li>• Hesap ayarları</li>
                <li>• Aktivite geçmişi</li>
              </ul>
            </div>
            
            <Button onClick={handleDownloadData} variant="outline">
              <Download className="w-4 h-4 mr-2" />
              Verilerimi İndir
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Account Deactivation Card */}
      <Card className="border-yellow-200">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2 text-yellow-700">
            <Archive className="w-5 h-5" />
            <span>Hesabı Devre Dışı Bırak</span>
          </CardTitle>
          <p className="text-sm text-muted-foreground">
            Hesabınızı geçici olarak devre dışı bırakın. Daha sonra geri açabilirsiniz.
          </p>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="p-4 bg-yellow-50 dark:bg-yellow-950 rounded-lg border border-yellow-200">
              <h4 className="font-medium text-yellow-800 dark:text-yellow-200 mb-2">
                Hesap devre dışı bırakıldığında:
              </h4>
              <ul className="text-sm text-yellow-700 dark:text-yellow-300 space-y-1">
                <li>• Profiliniz ve yazılarınız gizlenir</li>
                <li>• Diğer kullanıcılar sizi bulamaz</li>
                <li>• Bildirimleri almayı durdurursunuz</li>
                <li>• Verileriniz saklanır, istediğinizde geri açabilirsiniz</li>
              </ul>
            </div>

            <Dialog open={deactivateDialogOpen} onOpenChange={setDeactivateDialogOpen}>
              <DialogTrigger asChild>
                <Button variant="outline" className="border-yellow-300 text-yellow-700 hover:bg-yellow-50">
                  <Archive className="w-4 h-4 mr-2" />
                  Hesabı Devre Dışı Bırak
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle className="flex items-center space-x-2">
                    <Archive className="w-5 h-5 text-yellow-600" />
                    <span>Hesabı Devre Dışı Bırak</span>
                  </DialogTitle>
                  <DialogDescription>
                    Hesabınızı devre dışı bırakmak istediğinizden emin misiniz? 
                    Bu işlem geri alınabilir.
                  </DialogDescription>
                </DialogHeader>
                <DialogFooter>
                  <Button 
                    variant="outline" 
                    onClick={() => setDeactivateDialogOpen(false)}
                    disabled={isDeactivating}
                  >
                    <X className="w-4 h-4 mr-2" />
                    İptal
                  </Button>
                  <Button 
                    variant="outline"
                    className="border-yellow-300 text-yellow-700 hover:bg-yellow-50"
                    onClick={handleDeactivateAccount}
                    disabled={isDeactivating}
                  >
                    <Archive className="w-4 h-4 mr-2" />
                    {isDeactivating ? 'Devre dışı bırakılıyor...' : 'Evet, Devre Dışı Bırak'}
                  </Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>
          </div>
        </CardContent>
      </Card>

      {/* Account Deletion Card */}
      <Card className="border-red-200">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2 text-red-700">
            <Trash2 className="w-5 h-5" />
            <span>Hesabı Sil</span>
          </CardTitle>
          <p className="text-sm text-muted-foreground">
            Hesabınızı kalıcı olarak silin. Bu işlem geri alınamaz.
          </p>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="p-4 bg-red-50 dark:bg-red-950 rounded-lg border border-red-200">
              <h4 className="font-medium text-red-800 dark:text-red-200 mb-2">
                ⚠️ Hesap silindiğinde:
              </h4>
              <ul className="text-sm text-red-700 dark:text-red-300 space-y-1">
                <li>• Tüm yazılarınız ve yorumlarınız silinir</li>
                <li>• Profil bilgileriniz kalıcı olarak kaldırılır</li>
                <li>• Bu işlem geri alınamaz</li>
                <li>• Aynı kullanıcı adıyla tekrar kayıt olamazsınız</li>
              </ul>
            </div>

            <Dialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
              <DialogTrigger asChild>
                <Button variant="destructive">
                  <Trash2 className="w-4 h-4 mr-2" />
                  Hesabı Sil
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle className="flex items-center space-x-2 text-red-700">
                    <Trash2 className="w-5 h-5" />
                    <span>Hesabı Kalıcı Olarak Sil</span>
                  </DialogTitle>
                  <DialogDescription>
                    Bu işlem geri alınamaz. Hesabınızı silmek istediğinizden emin misiniz?
                  </DialogDescription>
                </DialogHeader>
                
                <div className="space-y-4">
                  <Alert variant="destructive">
                    <AlertTriangle className="h-4 w-4" />
                    <AlertDescription>
                      Onaylamak için kullanıcı adınızı yazın: <strong>{user.username}</strong>
                    </AlertDescription>
                  </Alert>
                  
                  <div className="space-y-2">
                    <Label htmlFor="confirmUsername">Kullanıcı Adı</Label>
                    <Input
                      id="confirmUsername"
                      value={confirmationText}
                      onChange={(e) => setConfirmationText(e.target.value)}
                      placeholder={user.username}
                    />
                  </div>
                </div>

                <DialogFooter>
                  <Button 
                    variant="outline" 
                    onClick={() => {
                      setDeleteDialogOpen(false)
                      setConfirmationText('')
                    }}
                    disabled={isDeleting}
                  >
                    <X className="w-4 w-4 mr-2" />
                    İptal
                  </Button>
                  <Button 
                    variant="destructive" 
                    onClick={handleDeleteAccount}
                    disabled={confirmationText !== user.username || isDeleting}
                  >
                    <Trash2 className="w-4 h-4 mr-2" />
                    {isDeleting ? 'Hesap siliniyor...' : 'Evet, Hesabı Sil'}
                  </Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>
          </div>
        </CardContent>
      </Card>

      {/* Security Notice Card */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Shield className="w-5 h-5" />
            <span>Güvenlik Uyarısı</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3 text-sm text-muted-foreground">
            <p>
              • Hesap işlemleri için güvenlik açısından şifreniz tekrar istenebilir.
            </p>
            <p>
              • Şüpheli aktivite durumunda hesabınız geçici olarak kısıtlanabilir.
            </p>
            <p>
              • Hesap silme işlemi öncesi 7 gün bekleme süresi uygulanabilir.
            </p>
            <p>
              • Önemli hesap değişiklikleri için e-posta bildirimi gönderilir.
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}