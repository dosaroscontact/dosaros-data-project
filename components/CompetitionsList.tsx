'use client'

import { motion } from 'framer-motion'
import { useReducedMotion } from '@/lib/hooks'

interface Competition {
  id: string
  name: string
  region: string
  teams: number
  founded: string
  coverage: string
  description: string
  accent: string
}

const competitions: Competition[] = [
  {
    id: 'nba',
    name: 'NBA',
    region: 'Estados Unidos',
    teams: 30,
    founded: '1946',
    coverage: '1983 — presente',
    description: 'La liga profesional más prestigiosa del mundo. Cobertura completa de partidos, play-by-play desde 2015 y estadísticas avanzadas de cada jugador.',
    accent: 'orange',
  },
  {
    id: 'euroleague',
    name: 'EuroLeague',
    region: 'Europa',
    teams: 18,
    founded: '2000',
    coverage: 'E2007 — presente',
    description: 'La máxima competición europea de clubes. Análisis play-by-play, comparativas con la NBA y métricas adaptadas como el PIR.',
    accent: 'magenta',
  },
]

export default function CompetitionsList() {
  const prefersReducedMotion = useReducedMotion()

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: { staggerChildren: prefersReducedMotion ? 0 : 0.15 },
    },
  }

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: { duration: prefersReducedMotion ? 0 : 0.6, ease: 'easeOut' },
    },
  }

  return (
    <section className="w-full py-16 sm:py-20 px-4 sm:px-6 bg-dos-white dark:bg-dos-blue">
      <div className="max-w-6xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: prefersReducedMotion ? 0 : 0.6 }}
          viewport={{ once: true }}
          className="mb-12 text-center"
        >
          <h1 className="text-4xl sm:text-5xl font-heading font-bold text-dos-blue dark:text-dos-white mb-4">
            Competiciones que Seguimos
          </h1>
          <p className="text-dos-gray-dark dark:text-dos-gray text-base sm:text-lg max-w-2xl mx-auto">
            Análisis comparativo entre las dos competiciones de baloncesto profesional más relevantes del planeta.
          </p>
        </motion.div>

        <motion.div
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-12"
        >
          {competitions.map((competition) => {
            const accentClasses = competition.accent === 'orange'
              ? 'border-dos-orange/30 hover:border-dos-orange'
              : 'border-dos-magenta/30 hover:border-dos-magenta'
            const accentText = competition.accent === 'orange'
              ? 'text-dos-orange'
              : 'text-dos-magenta'

            return (
              <motion.article
                key={competition.id}
                variants={itemVariants}
                className={`rounded-lg p-6 sm:p-8 bg-dos-white dark:bg-dos-blue-dark border-2 ${accentClasses} transition-all`}
              >
                <header className="mb-4">
                  <h2 className={`text-3xl sm:text-4xl font-heading font-bold ${accentText} mb-2`}>
                    {competition.name}
                  </h2>
                  <p className="text-dos-gray-dark dark:text-dos-gray text-sm">
                    {competition.region}
                  </p>
                </header>

                <p className="text-dos-blue dark:text-dos-gray mb-6 leading-relaxed">
                  {competition.description}
                </p>

                <dl className="grid grid-cols-3 gap-4 pt-4 border-t border-dos-gray/20 dark:border-dos-magenta/20">
                  <div>
                    <dt className="text-xs uppercase tracking-wide text-dos-gray-dark dark:text-dos-gray mb-1">
                      Equipos
                    </dt>
                    <dd className={`text-2xl font-heading font-bold ${accentText}`}>
                      {competition.teams}
                    </dd>
                  </div>
                  <div>
                    <dt className="text-xs uppercase tracking-wide text-dos-gray-dark dark:text-dos-gray mb-1">
                      Fundada
                    </dt>
                    <dd className="text-2xl font-heading font-bold text-dos-blue dark:text-dos-white">
                      {competition.founded}
                    </dd>
                  </div>
                  <div>
                    <dt className="text-xs uppercase tracking-wide text-dos-gray-dark dark:text-dos-gray mb-1">
                      Cobertura
                    </dt>
                    <dd className="text-sm font-medium text-dos-blue dark:text-dos-white pt-2">
                      {competition.coverage}
                    </dd>
                  </div>
                </dl>
              </motion.article>
            )
          })}
        </motion.div>

        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          transition={{ duration: prefersReducedMotion ? 0 : 0.6, delay: 0.3 }}
          viewport={{ once: true }}
          className="text-center bg-dos-blue/5 dark:bg-dos-blue-dark/50 rounded-lg p-8 border border-dos-gray/20 dark:border-dos-magenta/20"
        >
          <p className="text-dos-gray-dark dark:text-dos-gray italic max-w-2xl mx-auto">
            <span className="font-bold text-dos-blue dark:text-dos-white">Datos primero. Contexto después. Opinión al final.</span>
            <br />
            Nuestra filosofía: comparar lo que el deporte ofrece, sin sensacionalismo ni opiniones sin fundamento.
          </p>
        </motion.div>
      </div>
    </section>
  )
}
