'use client'

import { trackEvent } from '@/lib/analytics'

const FOOTER_LINKS = [
  { text: 'Análisis', href: '/analisis' },
  { text: 'Predicciones', href: '/predicciones' },
  { text: 'Competiciones', href: '/competiciones' },
  { text: 'Productos', href: '/productos' },
  { text: 'Contacto', href: '/contact' },
] as const

const SocialLinks = [
  {
    name: 'X' as const,
    platform: 'twitter' as const,
    account: '@dos_aros',
    href: 'https://twitter.com/dos_aros',
    icon: '/twitter.svg',
  },
  {
    name: 'Instagram' as const,
    platform: 'instagram' as const,
    account: '@dosaros_basket',
    href: 'https://instagram.com/dosaros_basket',
    icon: '/instagram.svg',
  },
]

export default function Footer() {
  return (
    <footer className="bg-dos-blue text-dos-white py-8 sm:py-12 px-4 sm:px-6">
      <div className="max-w-6xl mx-auto">
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-8 mb-8">
          {/* Brand */}
          <div>
            <h3 className="font-heading font-bold text-lg mb-3">DOS AROS</h3>
            <p className="text-dos-gray text-sm">
              Basketball reimagined. Data-driven insights para todos.
            </p>
          </div>

          {/* Links */}
          <div>
            <h4 className="font-heading font-bold text-sm mb-3">Producto</h4>
            <ul className="space-y-2 text-sm text-dos-gray">
              {FOOTER_LINKS.map((link) => (
                <li key={link.href}>
                  <a
                    href={link.href}
                    onClick={() => trackEvent({
                      event: 'nav_clicked',
                      link_text: link.text,
                      link_url: link.href,
                      nav_location: 'footer',
                    })}
                    className="hover:text-dos-orange transition-colors"
                  >
                    {link.text}
                  </a>
                </li>
              ))}
            </ul>
          </div>

          {/* Social */}
          <div>
            <h4 className="font-heading font-bold text-sm mb-3">Síguenos</h4>
            <div className="flex gap-4">
              {SocialLinks.map((social) => (
                <a
                  key={social.name}
                  href={social.href}
                  target="_blank"
                  rel="noopener noreferrer"
                  onClick={() => trackEvent({
                    event: 'social_clicked',
                    platform: social.platform,
                    handle: social.account,
                    location: 'footer',
                  })}
                  className="text-dos-gray hover:text-dos-orange transition-colors"
                  aria-label={`Seguir en ${social.account}`}
                  title={social.account}
                >
                  <img
                    src={social.icon}
                    alt={social.name}
                    className={`w-6 h-6 hover:opacity-80 transition-opacity ${
                      social.name === 'Instagram'
                        ? 'brightness-0 invert'
                        : ''
                    }`}
                  />
                </a>
              ))}
            </div>
          </div>
        </div>

        <div className="border-t border-dos-magenta/20 pt-6 text-center text-sm text-dos-gray">
          <p>© 2026 DOS AROS. Todos los derechos reservados.</p>
        </div>
      </div>
    </footer>
  )
}
