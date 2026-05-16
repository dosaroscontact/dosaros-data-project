'use client'

import { useState } from 'react'
import Image from 'next/image'

const SocialLinks = [
  {
    name: 'X',
    href: 'https://twitter.com/dos_aros',
    icon: (
      <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
        <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24h-6.627l-5.1-6.694-5.867 6.694H2.882l7.732-8.835L1.227 2.25h6.802l4.557 6.018L17.541 2.25h.703zm-1.106 17.920h1.828L5.900 4.122H4.002l12.136 16.048z"/>
      </svg>
    ),
  },
  {
    name: 'Instagram',
    href: 'https://instagram.com/dosaros_basket',
    icon: (
      <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
        <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163C8.756 0 8.331.012 7.052.072 2.977.272.273 2.977.073 7.052.012 8.331 0 8.756 0 12s.012 3.669.072 4.948c.2 4.074 2.904 6.778 6.979 6.978 1.279.06 1.704.072 4.948.072s3.669-.012 4.948-.072c4.074-.2 6.778-2.904 6.978-6.978.06-1.279.072-1.704.072-4.948s-.012-3.669-.072-4.948c-.2-4.074-2.904-6.778-6.978-6.978C15.669.012 15.244 0 12 0zm0 5.838a6.162 6.162 0 100 12.324 6.162 6.162 0 000-12.324zM12 16a4 4 0 110-8 4 4 0 010 8zm4.965-10.322a1.44 1.44 0 100 2.881 1.44 1.44 0 000-2.881z"/>
      </svg>
    ),
  },
]

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
          <Image
            src="/banner-dos-aros.png"
            alt="DOS AROS"
            width={120}
            height={40}
            className="h-8 sm:h-10 w-auto"
            priority
          />
        </a>

        <div className="hidden md:flex items-center gap-8">
          <a href="#" className="text-dos-blue dark:text-dos-gray font-body text-sm font-medium">Análisis</a>
          <a href="#" className="text-dos-blue dark:text-dos-gray font-body text-sm font-medium">Predicciones</a>
          <a href="#" className="text-dos-blue dark:text-dos-gray font-body text-sm font-medium">Comunidad</a>
          <a href="#productos" className="text-dos-blue dark:text-dos-gray font-body text-sm font-medium">Productos</a>
        </div>

        <div className="flex items-center gap-4 sm:gap-6">
          {SocialLinks.map((social) => (
            <a
              key={social.name}
              href={social.href}
              target="_blank"
              rel="noopener noreferrer"
              className="text-dos-blue dark:text-dos-gray hover:text-dos-orange dark:hover:text-dos-orange transition-colors"
              aria-label={`Seguir en ${social.name}`}
            >
              <span className="hidden sm:inline">{social.name}</span>
              <span className="sm:hidden">{social.icon}</span>
            </a>
          ))}
          <button
            onClick={() => setIsOpen(!isOpen)}
            className="md:hidden p-2 text-dos-blue dark:text-dos-white"
          >
            {isOpen ? '✕' : '☰'}
          </button>
        </div>
      </div>

      {isOpen && (
        <div className="md:hidden bg-dos-white dark:bg-dos-blue-dark border-t">
          <div className="px-4 py-4 space-y-3">
            <a href="#" className="block px-4 py-2 text-dos-blue dark:text-dos-white text-sm">Análisis</a>
            <a href="#" className="block px-4 py-2 text-dos-blue dark:text-dos-white text-sm">Predicciones</a>
            <a href="#" className="block px-4 py-2 text-dos-blue dark:text-dos-white text-sm">Comunidad</a>
            <a href="#productos" className="block px-4 py-2 text-dos-blue dark:text-dos-white text-sm">Productos</a>
            <div className="border-t border-dos-gray/20 dark:border-dos-magenta/20 mt-4 pt-4 flex gap-4">
              {SocialLinks.map((social) => (
                <a
                  key={social.name}
                  href={social.href}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-dos-blue dark:text-dos-gray hover:text-dos-orange dark:hover:text-dos-orange transition-colors"
                  aria-label={`Seguir en ${social.name}`}
                >
                  {social.icon}
                </a>
              ))}
            </div>
          </div>
        </div>
      )}
    </nav>
  )
}
