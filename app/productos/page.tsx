import Navbar from '@/components/Navbar'
import ProductsBanner from '@/components/ProductsBanner'
import ProductCatalog from '@/components/ProductCatalog'
import Footer from '@/components/Footer'

export const metadata = {
  title: 'Productos — DOS AROS',
  description: 'Catálogo completo de productos oficiales DOS AROS. Camisetas, sudaderas, gorras, totebags y accesorios para fans del baloncesto.',
}

export default function ProductosPage() {
  return (
    <main id="main-content">
      <Navbar />
      <div className="pt-24">
        <ProductsBanner />
        <ProductCatalog />
      </div>
      <Footer />
    </main>
  )
}
