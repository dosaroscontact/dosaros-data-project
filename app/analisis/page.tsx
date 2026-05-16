import Navbar from '@/components/Navbar'
import UnderConstruction from '@/components/UnderConstruction'
import Footer from '@/components/Footer'

export const metadata = {
  title: 'Análisis — DOS AROS',
  description: 'Análisis detallados de partidos NBA y EuroLeague. Próximamente en DOS AROS.',
}

export default function AnalisisPage() {
  return (
    <main id="main-content">
      <Navbar />
      <UnderConstruction
        title="Análisis"
        description="Explora análisis detallados de partidos, jugadores y equipos de NBA y EuroLeague. Estadísticas avanzadas, tendencias y patrones de juego."
      />
      <Footer />
    </main>
  )
}
