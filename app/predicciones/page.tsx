import Navbar from '@/components/Navbar'
import UnderConstruction from '@/components/UnderConstruction'
import Footer from '@/components/Footer'

export const metadata = {
  title: 'Predicciones — DOS AROS',
  description: 'Predicciones y pronósticos de partidos NBA y EuroLeague. Próximamente en DOS AROS.',
}

export default function PrediccionesPage() {
  return (
    <main id="main-content">
      <Navbar />
      <UnderConstruction
        title="Predicciones"
        description="Predicciones inteligentes basadas en datos para partidos NBA y EuroLeague. Modelos avanzados que analizan cada variable del juego."
      />
      <Footer />
    </main>
  )
}
