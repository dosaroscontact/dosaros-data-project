import Navbar from '@/components/Navbar'
import AnalysisList from '@/components/AnalysisList'
import Footer from '@/components/Footer'
import { getAllAnalyses, getAllTags, getAnalysesByTag } from '@/lib/analysis'

export const metadata = {
  title: 'Análisis — DOS AROS',
  description: 'Análisis diarios NBA y EuroLeague. Datos primero. Contexto después. Opinión al final.',
}

interface PageProps {
  searchParams: Promise<{ tag?: string }>
}

export default async function AnalisisPage({ searchParams }: PageProps) {
  const params = await searchParams
  const activeTag = params.tag
  const allTags = getAllTags()
  const analyses = activeTag ? getAnalysesByTag(activeTag) : getAllAnalyses()

  return (
    <main id="main-content">
      <Navbar />
      <div className="pt-24">
        <AnalysisList
          analyses={analyses}
          allTags={allTags}
          activeTag={activeTag}
        />
      </div>
      <Footer />
    </main>
  )
}
