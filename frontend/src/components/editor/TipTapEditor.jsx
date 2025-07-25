// src/components/editor/TipTapEditor.jsx
'use client'

import { useEditor, EditorContent } from '@tiptap/react'
import StarterKit from '@tiptap/starter-kit'
import Typography from '@tiptap/extension-typography'
import Placeholder from '@tiptap/extension-placeholder'
import CharacterCount from '@tiptap/extension-character-count'
import Link from '@tiptap/extension-link'
import Image from '@tiptap/extension-image'
import { Table } from '@tiptap/extension-table'
import { TableRow } from '@tiptap/extension-table-row' 
import { TableHeader } from '@tiptap/extension-table-header'
import { TableCell } from '@tiptap/extension-table-cell'
import { TextStyle } from '@tiptap/extension-text-style'
import { Color } from '@tiptap/extension-color'
import { Focus } from '@tiptap/extension-focus'

import { useCallback, useEffect } from 'react'
import debounce from 'lodash.debounce'

// Editor Toolbar Component
import EditorToolbar from './EditorToolbar'

const TipTapEditor = ({ 
  content = '', 
  onChange,
  onAutoSave,
  placeholder = 'Yazmaya başlayın...',
  className = '',
  readOnly = false,
  autoSave = true,
  characterLimit = 50000
}) => {
  
  // Debounced auto-save function
  const debouncedAutoSave = useCallback(
    debounce((content) => {
      if (onAutoSave && autoSave) {
        onAutoSave(content)
      }
    }, 2000), // 2 seconds delay
    [onAutoSave, autoSave]
  )

  const editor = useEditor({
    immediatelyRender: false,
    extensions: [
      StarterKit.configure({
        heading: {
          levels: [1, 2, 3, 4, 5, 6],
        },
        bulletList: {
          keepMarks: true,
          keepAttributes: false,
        },
        orderedList: {
          keepMarks: true,
          keepAttributes: false,
        },
      }),
      
      Typography.configure({
        // Turkish typography rules
        leftArrow: '←',
        rightArrow: '→',
        copyright: '©',
        trademark: '™',
        oneHalf: '½',
        plusMinus: '±',
        notEqual: '≠',
        laquo: '«',
        raquo: '»',
        multiplication: '×',
        superscriptTwo: '²',
        superscriptThree: '³',
        oneQuarter: '¼',
        threeQuarters: '¾',
      }),
      
      Placeholder.configure({
        placeholder,
        emptyEditorClass: 'is-editor-empty',
      }),
      
      CharacterCount.configure({
        limit: characterLimit,
      }),
      
      Link.configure({
        openOnClick: false,
        HTMLAttributes: {
          class: 'text-blue-600 underline hover:text-blue-800',
        },
      }),
      
      Image.configure({
        HTMLAttributes: {
          class: 'max-w-full h-auto rounded-lg',
        },
      }),
      
      Table.configure({
        resizable: true,
        HTMLAttributes: {
          class: 'border-collapse border border-gray-300',
        },
      }),
      TableRow,
      TableHeader.configure({
        HTMLAttributes: {
          class: 'border border-gray-300 bg-gray-50 font-semibold p-2',
        },
      }),
      TableCell.configure({
        HTMLAttributes: {
          class: 'border border-gray-300 p-2',
        },
      }),
      
      TextStyle,
      Color,
      
      Focus.configure({
        className: 'has-focus',
        mode: 'all',
      }),
    ],
    
    content,
    editable: !readOnly,
    
    onUpdate: ({ editor }) => {
      const html = editor.getHTML()
      const json = editor.getJSON()
      
      // Call onChange immediately for real-time updates
      if (onChange) {
        onChange({
          html,
          json,
          text: editor.getText(),
          characterCount: editor.storage.characterCount.characters(),
          wordCount: editor.storage.characterCount.words(),
        })
      }
      
      // Trigger auto-save with debounce
      debouncedAutoSave({
        html,
        json,
      })
    },
  })

  // Update editor content when prop changes
  useEffect(() => {
    if (editor && content !== editor.getHTML()) {
      editor.commands.setContent(content)
    }
  }, [content, editor])

  // Cleanup debounced function
  useEffect(() => {
    return () => {
      debouncedAutoSave.cancel()
    }
  }, [debouncedAutoSave])

  if (!editor) {
    return (
      <div className="animate-pulse">
        <div className="h-10 bg-gray-200 rounded mb-4"></div>
        <div className="h-64 bg-gray-200 rounded"></div>
      </div>
    )
  }

  const characterCount = editor.storage.characterCount.characters()
  const wordCount = editor.storage.characterCount.words()

  return (
    <div className={`border border-gray-200 rounded-lg overflow-hidden ${className}`}>
      {/* Toolbar */}
      {!readOnly && (
        <EditorToolbar editor={editor} />
      )}
      
      {/* Editor Content */}
      <div className="relative">
        <EditorContent 
          editor={editor}
          className="prose prose-lg max-w-none p-6 min-h-[400px] focus:outline-none"
        />
        
        {/* Focus overlay for writing mode */}
        <div className="absolute inset-0 pointer-events-none opacity-0 bg-gradient-to-b from-transparent via-transparent to-white transition-opacity duration-300 has-focus:opacity-50"></div>
      </div>
      
      {/* Footer with stats */}
      <div className="flex justify-between items-center px-6 py-3 bg-gray-50 border-t text-sm text-gray-600">
        <div className="flex space-x-4">
          <span>{wordCount} kelime</span>
          <span>{characterCount} karakter</span>
          {characterLimit && (
            <span className={characterCount > characterLimit * 0.9 ? 'text-red-500' : ''}>
              / {characterLimit}
            </span>
          )}
        </div>
        
        {autoSave && (
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
            <span>Otomatik kayıt aktif</span>
          </div>
        )}
      </div>
    </div>
  )
}

export default TipTapEditor