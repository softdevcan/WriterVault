// src/app/dashboard/layout.jsx
'use client'

import { useState } from 'react'
import { useRouter, usePathname } from 'next/navigation'
import Link from 'next/link'
import {
  LayoutDashboard,
  FileText,
  BookOpen,
  Folder,
  Settings,
  User,
  LogOut,
  Menu,
  X,
  PlusCircle
} from 'lucide-react'

import { Button } from '@/components/ui/button'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} 

from '@/components/ui/dropdown-menu'
import useAuthStore from '@/store/auth'

const DashboardLayout = ({ children }) => {
  const router = useRouter()
  const pathname = usePathname()
  const { user, logout } = useAuthStore()
  const [sidebarOpen, setSidebarOpen] = useState(false)

  // Navigation items
  const navigation = [
    {
      name: 'Dashboard',
      href: '/dashboard',
      icon: LayoutDashboard,
      exact: true
    },
    {
      name: 'Makaleler',
      href: '/dashboard/articles',
      icon: FileText,
      children: [
        { name: 'Tüm Makaleler', href: '/dashboard/articles' },
        { name: 'Yeni Makale', href: '/dashboard/articles/create' },
      ]
    },
    {
      name: 'Koleksiyonlar',
      href: '/dashboard/collections',
      icon: BookOpen,
      children: [
        { name: 'Tüm Koleksiyonlar', href: '/dashboard/collections' },
        { name: 'Yeni Koleksiyon', href: '/dashboard/collections/create' },
      ]
    },
    {
      name: 'Kategoriler',
      href: '/dashboard/categories',
      icon: Folder,
    },
    {
      name: 'Profil',
      href: '/dashboard/profile',
      icon: User,
    },
    {
      name: 'Ayarlar',
      href: '/dashboard/settings',
      icon: Settings,
    },
  ]

  const handleLogout = async () => {
    try {
      await logout()
      router.push('/auth/login')
    } catch (error) {
      console.error('Logout error:', error)
    }
  }

  const isActiveRoute = (href, exact = false) => {
    if (exact) {
      return pathname === href
    }
    return pathname.startsWith(href)
  }

  return (
    <div className="flex min-h-screen bg-gray-50">
      
      {/* Main content */}
      <div className="flex-1 overflow-hidden">
      
      {/* Top bar - mobile hamburger'ı sağa al */}
      <div className="sticky top-0 z-30 flex items-center justify-between h-16 px-6 bg-white border-b lg:hidden">
        <Link href="/dashboard" className="flex items-center space-x-2">
          <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
            <span className="text-white font-bold text-sm">W</span>
          </div>
          <span className="text-xl font-bold text-gray-900">WriterHub</span>
        </Link>
        
        <Button
          variant="ghost"
          size="sm"
          onClick={() => setSidebarOpen(true)}
        >
          <Menu className="w-5 h-5" />
        </Button>
      </div>

      {/* Page content */}
      <main className="min-h-screen">
        {children}
      </main>
    </div>
      
      {/* Mobile sidebar backdrop */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 z-40 bg-black bg-opacity-50 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <div className={`
      w-64 bg-white shadow-lg z-50 flex-shrink-0 
      ${sidebarOpen ? 'fixed inset-y-0 right-0' : 'hidden lg:block'}
      lg:relative lg:translate-x-0
    `}>
        
        {/* Sidebar header */}
        <div className="flex items-center justify-between h-16 px-6 border-b">
          <Link href="/dashboard" className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">W</span>
            </div>
            <span className="text-xl font-bold text-gray-900">WriterHub</span>
          </Link>
          
          {/* Mobile close button */}
          <Button
            variant="ghost"
            size="sm"
            className="lg:hidden"
            onClick={() => setSidebarOpen(false)}
          >
            <X className="w-5 h-5" />
          </Button>
        </div>

        {/* User section */}
        <div className="p-4 border-t">
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" className="w-full justify-start p-2">
                <Avatar className="w-8 h-8 mr-3">
                  <AvatarImage src={user?.avatar_url} alt={user?.username} />
                  <AvatarFallback>
                    {user?.username?.charAt(0).toUpperCase() || 'U'}
                  </AvatarFallback>
                </Avatar>
                <div className="flex-1 text-left">
                  <p className="text-sm font-medium">{user?.username}</p>
                  <p className="text-xs text-gray-500 truncate">{user?.email}</p>
                </div>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-56">
              <DropdownMenuLabel>Hesabım</DropdownMenuLabel>
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={() => router.push('/dashboard/profile')}>
                <User className="w-4 h-4 mr-2" />
                Profil
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => router.push('/dashboard/settings')}>
                <Settings className="w-4 h-4 mr-2" />
                Ayarlar
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={handleLogout} className="text-red-600">
                <LogOut className="w-4 h-4 mr-2" />
                Çıkış Yap
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>

        {/* Quick actions */}
        <div className="p-4 border-b">
          <Button 
            className="w-full" 
            onClick={() => router.push('/dashboard/articles/create')}
          >
            <PlusCircle className="w-4 h-4 mr-2" />
            Yeni Makale
          </Button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-4 py-6 space-y-2">
          {navigation.map((item) => (
            <div key={item.name}>
              <Link
                href={item.href}
                className={`
                  flex items-center px-3 py-2 text-sm font-medium rounded-lg transition-colors
                  ${isActiveRoute(item.href, item.exact)
                    ? 'bg-blue-50 text-blue-700 border-r-2 border-blue-700'
                    : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                  }
                `}
              >
                <item.icon className="w-5 h-5 mr-3" />
                {item.name}
              </Link>
              
              {/* Sub-navigation */}
              {item.children && isActiveRoute(item.href) && (
                <div className="ml-8 mt-2 space-y-1">
                  {item.children.map((child) => (
                    <Link
                      key={child.name}
                      href={child.href}
                      className={`
                        block px-3 py-1 text-sm rounded-md transition-colors
                        ${pathname === child.href
                          ? 'text-blue-700 bg-blue-50'
                          : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'
                        }
                      `}
                    >
                      {child.name}
                    </Link>
                  ))}
                </div>
              )}
            </div>
          ))}
        </nav>
      </div>

      
    </div>
  )
}

export default DashboardLayout