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
              <li>
                <a href="/analisis" className="hover:text-dos-orange transition-colors">
                  Análisis
                </a>
              </li>
              <li>
                <a href="/predicciones" className="hover:text-dos-orange transition-colors">
                  Predicciones
                </a>
              </li>
              <li>
                <a href="/comunidad" className="hover:text-dos-orange transition-colors">
                  Comunidad
                </a>
              </li>
              <li>
                <a href="/#productos" className="hover:text-dos-orange transition-colors">
                  Productos
                </a>
              </li>
              <li>
                <a href="/contact" className="hover:text-dos-orange transition-colors">
                  Contacto
                </a>
              </li>
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
