'use client'

import Link from 'next/link'
import { motion } from 'framer-motion'
import { useReducedMotion } from '@/lib/hooks'
import type { AnalysisMeta } from '@/lib/analysis'

interface Props {
  analyses: AnalysisMeta[]
  allTags: { tag: string; count: number }[]
  activeTag?: string
}

function formatDateES(dateStr: string): string {
  const [y, m, d] = dateStr.split('-')
  const months = [
    'enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
    'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre',
  ]
  return `${parseInt(d, 10)} de ${months[parseInt(m, 10) - 1]} de ${y}`
}

function leagueColor(league: string): string {
  if (league === 'NBA') return 'bg-dos-orange/10 text-dos-orange-dark border-dos-orange/30'
  if (league === 'EuroLeague') return 'bg-dos-magenta/10 text-dos-magenta border-dos-magenta/30'
  return 'bg-dos-gray/10 text-dos-blue dark:text-dos-white border-dos-gray/30'
}

export default function AnalysisList({ analyses, allTags, activeTag }: Props) {
  const prefersReducedMotion = useReducedMotion()

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: { staggerChildren: prefersReducedMotion ? 0 : 0.08 },
    },
  }

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: { duration: prefersReducedMotion ? 0 : 0.5 },
    },
  }

  return (
    <section className="w-full py-16 sm:py-20 px-4 sm:px-6 bg-gradient-to-br from-dos-blue/5 to-dos-magenta/5 min-h-screen">
      <div className="max-w-5xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: prefersReducedMotion ? 0 : 0.6 }}
          className="mb-12 text-center"
        >
          <h1 className="text-3xl sm:text-4xl font-heading font-bold text-dos-blue dark:text-dos-white mb-3">
            Análisis Diarios
          </h1>
          <p className="text-dos-gray-dark dark:text-dos-gray text-base sm:text-lg max-w-2xl mx-auto">
            Datos primero. Contexto después. Opinión al final.
            <br />
            Análisis NBA + EuroLeague publicados diariamente.
          </p>
        </motion.div>

        {/* Tag filters */}
        {allTags.length > 0 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: prefersReducedMotion ? 0 : 0.4, delay: 0.2 }}
            className="flex flex-wrap gap-2 justify-center mb-10"
          >
            <Link
              href="/analisis"
              className={`px-4 py-2 rounded-lg font-heading font-bold text-sm transition-all ${
                !activeTag
                  ? 'bg-dos-blue text-dos-white'
                  : 'bg-dos-white dark:bg-dos-blue/30 text-dos-blue dark:text-dos-white border-2 border-dos-gray/20 dark:border-dos-magenta/20 hover:border-dos-blue/50'
              }`}
            >
              Todos
            </Link>
            {allTags.map(({ tag, count }) => (
              <Link
                key={tag}
                href={`/analisis?tag=${encodeURIComponent(tag)}`}
                className={`px-4 py-2 rounded-lg font-heading font-bold text-sm transition-all ${
                  activeTag?.toLowerCase() === tag.toLowerCase()
                    ? 'bg-dos-orange text-dos-blue'
                    : 'bg-dos-white dark:bg-dos-blue/30 text-dos-blue dark:text-dos-white border-2 border-dos-gray/20 dark:border-dos-magenta/20 hover:border-dos-orange/50'
                }`}
              >
                {tag} <span className="opacity-60">({count})</span>
              </Link>
            ))}
          </motion.div>
        )}

        {/* Articles list */}
        {analyses.length === 0 ? (
          <div className="text-center py-20">
            <p className="text-dos-gray-dark dark:text-dos-gray text-lg">
              No hay análisis publicados todavía{activeTag ? ` con el tag "${activeTag}"` : ''}.
            </p>
          </div>
        ) : (
          <motion.ul
            variants={containerVariants}
            initial="hidden"
            animate="visible"
            className="space-y-6"
          >
            {analyses.map((analysis) => (
              <motion.li key={analysis.slug} variants={itemVariants}>
                <Link
                  href={`/analisis/${analysis.slug}`}
                  className="block group"
                >
                  <article className="rounded-xl border-2 border-dos-gray/20 dark:border-dos-magenta/20 bg-dos-white dark:bg-dos-blue-dark/50 p-6 sm:p-8 hover:border-dos-orange/50 hover:shadow-lg transition-all">
                    <header className="mb-4">
                      <time
                        dateTime={analysis.date}
                        className="block text-sm font-heading font-bold text-dos-orange uppercase tracking-wide mb-2"
                      >
                        {formatDateES(analysis.date)}
                      </time>
                      <h2 className="text-xl sm:text-2xl font-heading font-bold text-dos-blue dark:text-dos-white group-hover:text-dos-orange transition-colors">
                        {analysis.title}
                      </h2>
                    </header>

                    {analysis.summary && (
                      <p className="text-dos-gray-dark dark:text-dos-gray mb-4 leading-relaxed">
                        {analysis.summary}
                      </p>
                    )}

                    <div className="flex flex-wrap items-center gap-2 pt-4 border-t border-dos-gray/10 dark:border-dos-magenta/10">
                      {analysis.sections.map((section, idx) => (
                        <span
                          key={idx}
                          className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold border ${leagueColor(section.league)}`}
                        >
                          {section.icon && <span aria-hidden="true">{section.icon}</span>}
                          {section.league}
                        </span>
                      ))}
                      {analysis.tags.length > 0 && (
                        <span className="text-xs text-dos-gray-dark dark:text-dos-gray ml-auto">
                          {analysis.tags.slice(0, 3).join(' · ')}
                        </span>
                      )}
                    </div>
                  </article>
                </Link>
              </motion.li>
            ))}
          </motion.ul>
        )}
      </div>
    </section>
  )
}
