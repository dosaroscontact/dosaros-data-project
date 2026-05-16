'use client'

import { motion } from 'framer-motion'

interface Highlight {
  id: string
  title: string
  description: string
  stat: string
  league: string
  icon: 'star' | 'trending' | 'zap'
  color: string
}

const HIGHLIGHTS: Highlight[] = [
  {
    id: '1',
    title: 'SGA Historic Night',
    description: 'Shai Gilgeous-Alexander alcanza 45 puntos con 8 asistencias contra Golden State',
    stat: '45 PTS, 8 AST',
    league: 'NBA',
    icon: 'star',
    color: 'from-dos-orange to-red-500',
  },
  {
    id: '2',
    title: 'Real Madrid en forma',
    description: 'Real Madrid vence a Barcelona en clásico ACB con defensa sofocante en Q4',
    stat: '78-75 Final',
    league: 'ACB',
    icon: 'trending',
    color: 'from-dos-magenta to-pink-500',
  },
  {
    id: '3',
    title: 'EuroLeague Thriller',
    description: 'Partizan remonta 15 puntos para ganar a Fenerbahçe en el último cuarto',
    stat: '72-68 Final',
    league: 'EuroLeague',
    icon: 'zap',
    color: 'from-purple-500 to-dos-magenta',
  },
]

const iconMap: Record<string, string> = {
  star: '⭐',
  trending: '📈',
  zap: '⚡',
}

export default function Highlights() {
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.15,
      },
    },
  }

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: { duration: 0.6 },
    },
  }

  return (
    <section className="w-full py-12 sm:py-16 px-4 sm:px-6 bg-dos-white dark:bg-dos-blue-dark">
      <div className="max-w-6xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          viewport={{ once: true }}
          className="mb-12 text-center"
        >
          <h2 className="text-3xl sm:text-4xl font-heading font-bold text-dos-blue dark:text-dos-white mb-3">
            Perlas del día
          </h2>
          <p className="text-dos-gray-dark text-base sm:text-lg max-w-xl mx-auto">
            Las actuaciones más destacadas de NBA, EuroLeague y ligas nacionales
          </p>
        </motion.div>

        <motion.div
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          className="grid grid-cols-1 md:grid-cols-3 gap-6"
        >
          {HIGHLIGHTS.map((highlight) => {
            const iconEmoji = iconMap[highlight.icon]
            return (
              <motion.div
                key={highlight.id}
                variants={itemVariants}
                className="group cursor-pointer"
              >
                <div className="relative overflow-hidden rounded-xl border-2 border-dos-gray/30 dark:border-dos-magenta/30 bg-gradient-to-br from-dos-white to-dos-gray/5 dark:from-dos-blue/50 dark:to-dos-magenta/10 hover:border-dos-orange/50 transition-all duration-300 shadow-md hover:shadow-xl p-6 h-full flex flex-col">
                  {/* Background glow effect */}
                  <div className={`absolute inset-0 bg-gradient-to-br ${highlight.color} opacity-0 group-hover:opacity-5 transition-opacity duration-300`}></div>

                  {/* Content */}
                  <div className="relative z-10 flex flex-col h-full">
                    {/* Header with icon and league */}
                    <div className="flex items-start justify-between mb-4">
                      <div className={`p-2 rounded-lg bg-gradient-to-br ${highlight.color} text-dos-white text-xl`}>
                        {iconEmoji}
                      </div>
                      <span className="text-xs font-heading font-bold text-dos-orange uppercase px-2 py-1 bg-dos-orange/10 rounded-lg">
                        {highlight.league}
                      </span>
                    </div>

                    {/* Title */}
                    <h3 className="text-lg sm:text-xl font-heading font-bold text-dos-blue dark:text-dos-white mb-2 group-hover:text-dos-orange transition-colors">
                      {highlight.title}
                    </h3>

                    {/* Description */}
                    <p className="text-sm text-dos-gray-dark dark:text-dos-gray flex-grow mb-4 leading-relaxed">
                      {highlight.description}
                    </p>

                    {/* Stat */}
                    <div className="pt-4 border-t border-dos-gray/20 dark:border-dos-magenta/20">
                      <p className="text-2xl font-heading font-bold text-dos-orange">
                        {highlight.stat}
                      </p>
                    </div>
                  </div>
                </div>
              </motion.div>
            )
          })}
        </motion.div>

        {/* View all CTA */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.3 }}
          viewport={{ once: true }}
          className="mt-12 text-center"
        >
          <a
            href="#"
            className="inline-flex items-center gap-2 px-6 sm:px-8 py-3 sm:py-4 bg-dos-orange hover:opacity-90 text-dos-blue font-heading font-bold rounded-lg transition-opacity duration-300 active:scale-95 min-h-[48px]"
          >
            Ver todas las perlas
            <span aria-hidden="true">→</span>
          </a>
        </motion.div>
      </div>
    </section>
  )
}
