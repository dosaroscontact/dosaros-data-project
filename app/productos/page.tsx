import Navbar from '@/components/Navbar'
import ProductCatalog from '@/components/ProductCatalog'
import Footer from '@/components/Footer'

export const metadata = {
  title: 'Productos — DOS AROS',
  description: 'Catálogo completo de productos oficiales DOS AROS. Camisetas, sudaderas, gorras y más para fans de NBA y EuroLeague.',
}

export default function ProductosPage() {
  return (
    <main id="main-content">
      <Navbar />
      <div className="pt-24 pb-12 bg-dos-white dark:bg-dos-blue">
        <ProductCatalog />
      </div>
      <Footer />
    </main>
  )
}
