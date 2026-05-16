'use client'

import { useState } from 'react'
import Image from 'next/image'

const SocialLinks = [
  {
    name: 'X',
    account: '@dos_aros',
    href: 'https://twitter.com/dos_aros',
    icon: '/twitter.svg',
  },
  {
    name: 'Instagram',
    account: '@dosaros_basket',
    href: 'https://instagram.com/dosaros_basket',
    icon: '/instagram.svg',
  },
]

export default function Navbar() {
  const [isOpen, setIsOpen] = useState(false)

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-dos-white/95 dark:bg-dos-blue/95 backdrop-blur-md border-b border-dos-gray/20 dark:border-dos-magenta/20 shadow-sm">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 py-4 flex items-center justify-between">
        <a href="/" className="flex items-center gap-2 sm:gap-3 group hover:opacity-80 transition-opacity">
          <Image
            src="/logo-dos-aros-official.png"
            alt="DOS AROS logo"
            width={40}
            height={40}
            className="w-8 h-8 sm:w-10 sm:h-10"
            priority
          />
          <Image
            src="/banners/letering-orange.png"
            alt="DOS AROS"
            width={2744}
            height={447}
            className="h-6 sm:h-8 w-auto"
            priority
          />
        </a>

        <div className="hidden md:flex items-center gap-8">
          <a href="/analisis" className="text-dos-blue dark:text-dos-gray font-body text-sm font-medium hover:text-dos-orange transition-colors">Análisis</a>
          <a href="/predicciones" className="text-dos-blue dark:text-dos-gray font-body text-sm font-medium hover:text-dos-orange transition-colors">Predicciones</a>
          <a href="/comunidad" className="text-dos-blue dark:text-dos-gray font-body text-sm font-medium hover:text-dos-orange transition-colors">Comunidad</a>
          <a href="/#productos" className="text-dos-blue dark:text-dos-gray font-body text-sm font-medium hover:text-dos-orange transition-colors">Productos</a>
          <a href="/contact" className="text-dos-blue dark:text-dos-gray font-body text-sm font-medium hover:text-dos-orange transition-colors">Contacto</a>
        </div>

        <div className="flex items-center gap-3 sm:gap-6">
          {SocialLinks.map((social) => (
            <a
              key={social.name}
              href={social.href}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2 text-dos-blue dark:text-dos-white hover:opacity-80 transition-opacity"
              aria-label={`Seguir en ${social.account}`}
              title={social.account}
            >
              <img
                src={social.icon}
                alt={social.name}
                className="w-6 h-6 sm:w-5 sm:h-5"
              />
              <span className="hidden sm:inline text-sm font-body">{social.account}</span>
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
            <a href="/analisis" className="block px-4 py-2 text-dos-blue dark:text-dos-white text-sm hover:text-dos-orange dark:hover:text-dos-orange">Análisis</a>
            <a href="/predicciones" className="block px-4 py-2 text-dos-blue dark:text-dos-white text-sm hover:text-dos-orange dark:hover:text-dos-orange">Predicciones</a>
            <a href="/comunidad" className="block px-4 py-2 text-dos-blue dark:text-dos-white text-sm hover:text-dos-orange dark:hover:text-dos-orange">Comunidad</a>
            <a href="/#productos" className="block px-4 py-2 text-dos-blue dark:text-dos-white text-sm hover:text-dos-orange dark:hover:text-dos-orange">Productos</a>
            <a href="/contact" className="block px-4 py-2 text-dos-blue dark:text-dos-white text-sm hover:text-dos-orange dark:hover:text-dos-orange">Contacto</a>
            <div className="border-t border-dos-gray/20 dark:border-dos-magenta/20 mt-4 pt-4 flex gap-4">
              {SocialLinks.map((social) => (
                <a
                  key={social.name}
                  href={social.href}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-dos-blue dark:text-dos-gray hover:opacity-80 transition-opacity"
                  aria-label={`Seguir en ${social.name}`}
                  title={social.name}
                >
                  <img
                    src={social.icon}
                    alt={social.name}
                    className="w-6 h-6"
                  />
                </a>
              ))}
            </div>
          </div>
        </div>
      )}
    </nav>
  )
}
