import Navbar from '@/components/Navbar'
import StickyTicker from '@/components/StickyTicker'
import Hero from '@/components/Hero'
import Highlights from '@/components/Highlights'
import Products from '@/components/Products'
import QueryBox from '@/components/QueryBox'
import Newsletter from '@/components/Newsletter'

export default function Home() {
  return (
    <main id="main-content">
      <Navbar />
      <StickyTicker />
      <Hero />
      <Highlights />
      <Products />
      <QueryBox />
      <Newsletter />

      {/* Footer */}
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
                  <a href="#" className="hover:text-dos-orange transition-colors">
                    Análisis
                  </a>
                </li>
                <li>
                  <a href="#" className="hover:text-dos-orange transition-colors">
                    Predicciones
                  </a>
                </li>
                <li>
                  <a href="#productos" className="hover:text-dos-orange transition-colors">
                    Productos
                  </a>
                </li>
              </ul>
            </div>

            {/* Social */}
            <div>
              <h4 className="font-heading font-bold text-sm mb-3">Síguenos</h4>
              <div className="flex gap-4">
                {[
                  { name: 'X', href: 'https://twitter.com/dos_aros' },
                  { name: 'Instagram', href: 'https://instagram.com/dosaros_basket' },
                ].map((social) => (
                  <a
                    key={social.name}
                    href={social.href}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-dos-gray hover:text-dos-orange transition-colors text-sm font-body"
                    aria-label={social.name}
                  >
                    {social.name}
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
    </main>
  )
}
