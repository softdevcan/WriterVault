// src/components/editor/EditorToolbar.jsx
'use client'

import { 
  Bold, 
  Italic, 
  Underline,
  Strikethrough,
  Quote,
  List,
  ListOrdered,
  Heading1,
  Heading2,
  Heading3,
  Link,
  Image,
  Table,
  Code,
  Undo,
  Redo,
  AlignLeft,
  AlignCenter,
  AlignRight,
  AlignJustify,
  Palette,
  Type,
  Eye,
  EyeOff
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Separator } from '@/components/ui/separator'
import { Toggle } from '@/components/ui/toggle'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { Input } from '@/components/ui/input'
import { useState, useCallback } from 'react'

const EditorToolbar = ({ editor }) => {
  const [showLinkInput, setShowLinkInput] = useState(false)
  const [linkUrl, setLinkUrl] = useState('')
  const [focusMode, setFocusMode] = useState(false)

  // Text formatting actions
  const formatActions = [
    {
      label: 'Kalın',
      icon: Bold,
      action: () => editor.chain().focus().toggleBold().run(),
      isActive: () => editor.isActive('bold'),
      shortcut: 'Ctrl+B'
    },
    {
      label: 'İtalik',
      icon: Italic,
      action: () => editor.chain().focus().toggleItalic().run(),
      isActive: () => editor.isActive('italic'),
      shortcut: 'Ctrl+I'
    },
    {
      label: 'Altı Çizili',
      icon: Underline,
      action: () => editor.chain().focus().toggleUnderline().run(),
      isActive: () => editor.isActive('underline'),
      shortcut: 'Ctrl+U'
    },
    {
      label: 'Üstü Çizili',
      icon: Strikethrough,
      action: () => editor.chain().focus().toggleStrike().run(),
      isActive: () => editor.isActive('strike'),
      shortcut: 'Ctrl+Shift+X'
    },
    {
      label: 'Kod',
      icon: Code,
      action: () => editor.chain().focus().toggleCode().run(),
      isActive: () => editor.isActive('code'),
      shortcut: 'Ctrl+E'
    }
  ]

  // Heading actions
  const headingActions = [
    {
      label: 'Başlık 1',
      icon: Heading1,
      action: () => editor.chain().focus().toggleHeading({ level: 1 }).run(),
      isActive: () => editor.isActive('heading', { level: 1 })
    },
    {
      label: 'Başlık 2',
      icon: Heading2,
      action: () => editor.chain().focus().toggleHeading({ level: 2 }).run(),
      isActive: () => editor.isActive('heading', { level: 2 })
    },
    {
      label: 'Başlık 3',
      icon: Heading3,
      action: () => editor.chain().focus().toggleHeading({ level: 3 }).run(),
      isActive: () => editor.isActive('heading', { level: 3 })
    }
  ]

  // List actions
  const listActions = [
    {
      label: 'Madde Liste',
      icon: List,
      action: () => editor.chain().focus().toggleBulletList().run(),
      isActive: () => editor.isActive('bulletList')
    },
    {
      label: 'Numaralı Liste',
      icon: ListOrdered,
      action: () => editor.chain().focus().toggleOrderedList().run(),
      isActive: () => editor.isActive('orderedList')
    },
    {
      label: 'Alıntı',
      icon: Quote,
      action: () => editor.chain().focus().toggleBlockquote().run(),
      isActive: () => editor.isActive('blockquote')
    }
  ]

  // Handle link addition
  const handleLinkAdd = useCallback(() => {
    if (linkUrl) {
      editor.chain().focus().setLink({ href: linkUrl }).run()
      setLinkUrl('')
      setShowLinkInput(false)
    }
  }, [editor, linkUrl])

  // Handle image upload
  const handleImageUpload = useCallback((event) => {
    const file = event.target.files?.[0]
    if (file) {
      const reader = new FileReader()
      reader.onload = (e) => {
        const url = e.target?.result
        if (url) {
          editor.chain().focus().setImage({ src: url }).run()
        }
      }
      reader.readAsDataURL(file)
    }
  }, [editor])

  // Toggle focus mode
  const toggleFocusMode = useCallback(() => {
    setFocusMode(!focusMode)
    // Add focus mode class to editor
    const editorElement = document.querySelector('.ProseMirror')
    if (editorElement) {
      editorElement.classList.toggle('focus-mode', !focusMode)
    }
  }, [focusMode])

  return (
    <div className="flex flex-wrap items-center gap-1 p-3 border-b bg-gray-50">
      {/* History */}
      <div className="flex items-center gap-1">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => editor.chain().focus().undo().run()}
          disabled={!editor.can().undo()}
          title="Geri Al (Ctrl+Z)"
        >
          <Undo className="w-4 h-4" />
        </Button>
        <Button
          variant="ghost"
          size="sm"
          onClick={() => editor.chain().focus().redo().run()}
          disabled={!editor.can().redo()}
          title="Yinele (Ctrl+Y)"
        >
          <Redo className="w-4 h-4" />
        </Button>
      </div>

      <Separator orientation="vertical" className="h-6" />

      {/* Headings */}
      <div className="flex items-center gap-1">
        {headingActions.map((action, index) => (
          <Toggle
            key={index}
            size="sm"
            pressed={action.isActive()}
            onPressedChange={action.action}
            title={action.label}
          >
            <action.icon className="w-4 h-4" />
          </Toggle>
        ))}
      </div>

      <Separator orientation="vertical" className="h-6" />

      {/* Text formatting */}
      <div className="flex items-center gap-1">
        {formatActions.map((action, index) => (
          <Toggle
            key={index}
            size="sm"
            pressed={action.isActive()}
            onPressedChange={action.action}
            title={`${action.label} (${action.shortcut})`}
          >
            <action.icon className="w-4 h-4" />
          </Toggle>
        ))}
      </div>

      <Separator orientation="vertical" className="h-6" />

      {/* Lists and quotes */}
      <div className="flex items-center gap-1">
        {listActions.map((action, index) => (
          <Toggle
            key={index}
            size="sm"
            pressed={action.isActive()}
            onPressedChange={action.action}
            title={action.label}
          >
            <action.icon className="w-4 h-4" />
          </Toggle>
        ))}
      </div>

      <Separator orientation="vertical" className="h-6" />

      {/* Link */}
      <div className="flex items-center gap-1">
        {showLinkInput ? (
          <div className="flex items-center gap-2">
            <Input
              type="url"
              placeholder="Link URL'si"
              value={linkUrl}
              onChange={(e) => setLinkUrl(e.target.value)}
              className="w-48 h-8"
              onKeyDown={(e) => {
                if (e.key === 'Enter') {
                  handleLinkAdd()
                }
                if (e.key === 'Escape') {
                  setShowLinkInput(false)
                  setLinkUrl('')
                }
              }}
              autoFocus
            />
            <Button size="sm" onClick={handleLinkAdd}>
              Ekle
            </Button>
            <Button 
              size="sm" 
              variant="ghost" 
              onClick={() => {
                setShowLinkInput(false)
                setLinkUrl('')
              }}
            >
              İptal
            </Button>
          </div>
        ) : (
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setShowLinkInput(true)}
            title="Link Ekle"
          >
            <Link className="w-4 h-4" />
          </Button>
        )}
      </div>

      {/* Image Upload */}
      <div className="flex items-center gap-1">
        <Button
          variant="ghost"
          size="sm"
          title="Resim Ekle"
          onClick={() => document.getElementById('image-upload')?.click()}
        >
          <Image className="w-4 h-4" />
        </Button>
        <input
          id="image-upload"
          type="file"
          accept="image/*"
          className="hidden"
          onChange={handleImageUpload}
        />
      </div>

      {/* Table */}
      <Button
        variant="ghost"
        size="sm"
        onClick={() => editor.chain().focus().insertTable({ rows: 3, cols: 3, withHeaderRow: true }).run()}
        title="Tablo Ekle"
      >
        <Table className="w-4 h-4" />
      </Button>

      <Separator orientation="vertical" className="h-6" />

      {/* Color Picker */}
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button variant="ghost" size="sm" title="Metin Rengi">
            <Palette className="w-4 h-4" />
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent>
          <div className="grid grid-cols-6 gap-1 p-2">
            {[
              '#000000', '#ef4444', '#f97316', '#eab308', 
              '#22c55e', '#3b82f6', '#8b5cf6', '#ec4899'
            ].map((color) => (
              <button
                key={color}
                className="w-6 h-6 rounded border-2 border-gray-300 hover:border-gray-500"
                style={{ backgroundColor: color }}
                onClick={() => editor.chain().focus().setColor(color).run()}
              />
            ))}
          </div>
          <DropdownMenuItem
            onClick={() => editor.chain().focus().unsetColor().run()}
          >
            Rengi Kaldır
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>

      {/* Focus Mode Toggle */}
      <Button
        variant="ghost"
        size="sm"
        onClick={toggleFocusMode}
        title={focusMode ? "Odaklanma Modunu Kapat" : "Odaklanma Modu"}
        className={focusMode ? "bg-blue-100" : ""}
      >
        {focusMode ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
      </Button>
    </div>
  )
}

export default EditorToolbar