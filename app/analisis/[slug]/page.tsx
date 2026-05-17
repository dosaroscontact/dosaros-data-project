import { notFound } from 'next/navigation'
import Navbar from '@/components/Navbar'
import AnalysisArticle from '@/components/AnalysisArticle'
import Footer from '@/components/Footer'
import { getAnalysisBySlug, getAllSlugs, formatDateES } from '@/lib/analysis'

interface PageProps {
  params: Promise<{ slug: string }>
}

export async function generateStaticParams() {
  return getAllSlugs().map((slug) => ({ slug }))
}

export async function generateMetadata({ params }: PageProps) {
  const { slug } = await params
  const analysis = getAnalysisBySlug(slug)

  if (!analysis) {
    return { title: 'Análisis no encontrado — DOS AROS' }
  }

  return {
    title: `${analysis.title} — DOS AROS`,
    description: analysis.summary || `Análisis del ${formatDateES(analysis.date)}`,
  }
}

export default async function AnalysisPage({ params }: PageProps) {
  const { slug } = await params
  const analysis = getAnalysisBySlug(slug)

  if (!analysis) notFound()

  return (
    <main id="main-content">
      <Navbar />
      <div className="pt-20 sm:pt-24">
        <AnalysisArticle analysis={analysis} />
      </div>
      <Footer />
    </main>
  )
}
