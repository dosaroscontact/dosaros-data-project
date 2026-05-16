import Navbar from '@/components/Navbar'
import UnderConstruction from '@/components/UnderConstruction'
import Footer from '@/components/Footer'

export const metadata = {
  title: 'Comunidad — DOS AROS',
  description: 'Únete a la comunidad DOS AROS de aficionados al baloncesto. Próximamente.',
}

export default function ComunidadPage() {
  return (
    <main id="main-content">
      <Navbar />
      <UnderConstruction
        title="Comunidad"
        description="Únete a una comunidad apasionada por el baloncesto. Comparte análisis, discute estrategias y conecta con otros aficionados NBA y EuroLeague."
      />
      <Footer />
    </main>
  )
}
