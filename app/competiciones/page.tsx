import Navbar from '@/components/Navbar'
import CompetitionsList from '@/components/CompetitionsList'
import Footer from '@/components/Footer'

export const metadata = {
  title: 'Competiciones — DOS AROS',
  description: 'Análisis de las competiciones de baloncesto que seguimos: NBA y EuroLeague.',
}

export default function CompeticionesPage() {
  return (
    <main id="main-content">
      <Navbar />
      <div className="pt-24">
        <CompetitionsList />
      </div>
      <Footer />
    </main>
  )
}
