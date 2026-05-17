'use client'

import Link from 'next/link'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { motion } from 'framer-motion'
import { useReducedMotion } from '@/lib/hooks'
import type { Analysis } from '@/lib/analysis'

interface Props {
  analysis: Analysis
}

function formatDateES(dateStr: string): string {
  const [y, m, d] = dateStr.split('-')
  const months = [
    'enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
    'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre',
  ]
  return `${parseInt(d, 10)} de ${months[parseInt(m, 10) - 1]} de ${y}`
}

export default function AnalysisArticle({ analysis }: Props) {
  const prefersReducedMotion = useReducedMotion()

  return (
    <article className="w-full py-12 sm:py-16 px-4 sm:px-6 bg-dos-white dark:bg-dos-blue min-h-screen">
      <div className="max-w-3xl mx-auto">
        {/* Back link */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: prefersReducedMotion ? 0 : 0.4 }}
          className="mb-8"
        >
          <Link
            href="/analisis"
            className="inline-flex items-center gap-2 text-sm text-dos-blue/70 dark:text-dos-gray hover:text-dos-orange transition-colors"
          >
            ← Volver a análisis
          </Link>
        </motion.div>

        {/* Header */}
        <motion.header
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: prefersReducedMotion ? 0 : 0.6 }}
          className="mb-10 pb-8 border-b border-dos-gray/20 dark:border-dos-magenta/20"
        >
          <time
            dateTime={analysis.date}
            className="block text-sm font-heading font-bold text-dos-orange uppercase tracking-wide mb-3"
          >
            {formatDateES(analysis.date)}
          </time>
          <h1 className="text-3xl sm:text-4xl lg:text-5xl font-heading font-bold text-dos-blue dark:text-dos-white mb-4 leading-tight">
            {analysis.title}
          </h1>
          {analysis.summary && (
            <p className="text-lg text-dos-blue/70 dark:text-dos-gray leading-relaxed">
              {analysis.summary}
            </p>
          )}
          {analysis.tags.length > 0 && (
            <div className="flex flex-wrap gap-2 mt-5">
              {analysis.tags.map((tag) => (
                <Link
                  key={tag}
                  href={`/analisis?tag=${encodeURIComponent(tag)}`}
                  className="text-xs px-3 py-1 rounded-full bg-dos-gray/10 dark:bg-dos-magenta/10 text-dos-blue dark:text-dos-white hover:bg-dos-orange/20 hover:text-dos-orange transition-colors"
                >
                  {tag}
                </Link>
              ))}
            </div>
          )}
        </motion.header>

        {/* Body */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: prefersReducedMotion ? 0 : 0.6, delay: 0.2 }}
          className="prose-dos-aros"
        >
          <ReactMarkdown remarkPlugins={[remarkGfm]}>
            {analysis.content}
          </ReactMarkdown>
        </motion.div>

        {/* Footer signature */}
        <motion.footer
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: prefersReducedMotion ? 0 : 0.6, delay: 0.4 }}
          className="mt-16 pt-8 border-t border-dos-gray/20 dark:border-dos-magenta/20 text-center"
        >
          <p className="text-sm text-dos-blue/70 dark:text-dos-gray italic">
            <span className="font-bold text-dos-blue dark:text-dos-white">Dos Aros</span>
            {' · '}
            Donde la NBA y la EuroLeague se cruzan.
          </p>
          <Link
            href="/analisis"
            className="inline-block mt-6 text-sm text-dos-orange hover:underline"
          >
            Ver todos los análisis →
          </Link>
        </motion.footer>
      </div>
    </article>
  )
}
