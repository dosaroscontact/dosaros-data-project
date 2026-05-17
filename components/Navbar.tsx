'use client'

import { useState } from 'react'
import Image from 'next/image'
import { trackEvent, type NavLocation, type SocialLocation } from '@/lib/analytics'

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

const NAV_LINKS = [
  { text: 'Análisis', href: '/analisis' },
  { text: 'Predicciones', href: '/predicciones' },
  { text: 'Competiciones', href: '/competiciones' },
  { text: 'Productos', href: '/productos' },
  { text: 'Contacto', href: '/contact' },
] as const

export default function Navbar() {
  const [isOpen, setIsOpen] = useState(false)

  const handleNavClick = (text: string, href: string, location: NavLocation) => {
    trackEvent({
      event: 'nav_clicked',
      link_text: text,
      link_url: href,
      nav_location: location,
    })
  }

  const handleSocialClick = (platform: 'twitter' | 'instagram', handle: string, location: SocialLocation) => {
    trackEvent({
      event: 'social_clicked',
      platform,
      handle,
      location,
    })
  }

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
          {NAV_LINKS.map((link) => (
            <a
              key={link.href}
              href={link.href}
              onClick={() => handleNavClick(link.text, link.href, 'header_desktop')}
              className="text-dos-blue dark:text-dos-gray font-body text-sm font-medium hover:text-dos-orange transition-colors"
            >
              {link.text}
            </a>
          ))}
        </div>

        <div className="flex items-center gap-3 sm:gap-6">
          {SocialLinks.map((social) => (
            <a
              key={social.name}
              href={social.href}
              target="_blank"
              rel="noopener noreferrer"
              onClick={() => handleSocialClick(social.name.toLowerCase() as 'twitter' | 'instagram', social.account, 'navbar')}
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
            {NAV_LINKS.map((link) => (
              <a
                key={link.href}
                href={link.href}
                onClick={() => handleNavClick(link.text, link.href, 'header_mobile')}
                className="block px-4 py-2 text-dos-blue dark:text-dos-white text-sm hover:text-dos-orange dark:hover:text-dos-orange"
              >
                {link.text}
              </a>
            ))}
            <div className="border-t border-dos-gray/20 dark:border-dos-magenta/20 mt-4 pt-4 flex gap-4">
              {SocialLinks.map((social) => (
                <a
                  key={social.name}
                  href={social.href}
                  target="_blank"
                  rel="noopener noreferrer"
                  onClick={() => handleSocialClick(social.name.toLowerCase() as 'twitter' | 'instagram', social.account, 'mobile_menu')}
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
