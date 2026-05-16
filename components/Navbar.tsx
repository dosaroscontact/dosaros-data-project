'use client'

import { useState } from 'react'
import Image from 'next/image'

export default function Navbar() {
  const [isOpen, setIsOpen] = useState(false)

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-dos-white/95 dark:bg-dos-blue/95 backdrop-blur-md border-b border-dos-gray/20 dark:border-dos-magenta/20 shadow-sm">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 py-4 flex items-center justify-between">
        <a href="#" className="flex items-center gap-2 sm:gap-3 group">
          <Image
            src="/logo-dos-aros-official.png"
            alt="DOS AROS logo"
            width={40}
            height={40}
            className="w-8 h-8 sm:w-10 sm:h-10"
            priority
          />
          <span className="text-lg sm:text-xl font-heading font-bold text-dos-blue dark:text-dos-white">
            DOS AROS
          </span>
        </a>

        <div className="hidden md:flex items-center gap-8">
          <a href="#" className="text-dos-blue dark:text-dos-gray font-body text-sm font-medium">Análisis</a>
          <a href="#" className="text-dos-blue dark:text-dos-gray font-body text-sm font-medium">Predicciones</a>
          <a href="#" className="text-dos-blue dark:text-dos-gray font-body text-sm font-medium">Comunidad</a>
          <a href="#" className="text-dos-blue dark:text-dos-gray font-body text-sm font-medium">Precios</a>
        </div>

        <button
          onClick={() => setIsOpen(!isOpen)}
          className="md:hidden p-2 text-dos-blue dark:text-dos-white"
        >
          {isOpen ? '✕' : '☰'}
        </button>
      </div>

      {isOpen && (
        <div className="md:hidden bg-dos-white dark:bg-dos-blue-dark border-t">
          <div className="px-4 py-4 space-y-3">
            <a href="#" className="block px-4 py-2 text-dos-blue dark:text-dos-white text-sm">Análisis</a>
            <a href="#" className="block px-4 py-2 text-dos-blue dark:text-dos-white text-sm">Predicciones</a>
            <a href="#" className="block px-4 py-2 text-dos-blue dark:text-dos-white text-sm">Comunidad</a>
            <a href="#" className="block px-4 py-2 text-dos-blue dark:text-dos-white text-sm">Precios</a>
          </div>
        </div>
      )}
    </nav>
  )
}
