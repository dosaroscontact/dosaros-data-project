'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { useReducedMotion } from '@/lib/hooks'

export default function QueryBox() {
  const [query, setQuery] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [result, setResult] = useState<string | null>(null)
  const prefersReducedMotion = useReducedMotion()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!query.trim()) return

    setIsLoading(true)
    try {
      // Mock API call
      await new Promise((resolve) => setTimeout(resolve, 1500))
      setResult(`Resultados para: "${query}"`)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <section className="w-full py-12 sm:py-16 md:py-20 px-4 sm:px-6 bg-gradient-to-br from-dos-blue/5 to-dos-magenta/5">
      <div className="max-w-2xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: prefersReducedMotion ? 0 : 0.6 }}
          viewport={{ once: true }}
          className="text-center mb-8"
        >
          <h2 className="text-3xl sm:text-4xl font-heading font-bold text-dos-blue mb-3">
            Haz tu pregunta
          </h2>
          <p className="text-lg text-dos-gray-dark">
            Pregunta en español. Nuestro IA buscará en la BD y te dará respuestas precisas.
          </p>
        </motion.div>

        <motion.form
          onSubmit={handleSubmit}
          initial={{ opacity: 0, scale: 0.95 }}
          whileInView={{ opacity: 1, scale: 1 }}
          transition={{ duration: prefersReducedMotion ? 0 : 0.5 }}
          viewport={{ once: true }}
          className="relative backdrop-blur-md bg-dos-white/80 border-2 border-dos-magenta/20 rounded-xl p-6 sm:p-8 shadow-lg hover:border-dos-magenta/40 transition-colors duration-300"
        >
          <div className="flex gap-3">
            <div className="flex-1 relative">
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="¿Cuántos puntos promedio LeBron en 2024?"
                disabled={isLoading}
                className="w-full px-4 py-3 sm:py-4 bg-transparent text-dos-blue placeholder-dos-gray-dark font-body text-base sm:text-lg border-0 focus:outline-none disabled:opacity-50"
                aria-label="Escribe tu pregunta sobre baloncesto"
                minLength={3}
                maxLength={200}
              />
              {isLoading && (
                <span className="absolute right-4 top-1/2 -translate-y-1/2 text-dos-orange animate-spin">⏳</span>
              )}
            </div>
            <button
              type="submit"
              disabled={isLoading || !query.trim()}
              className="bg-dos-orange hover:opacity-90 disabled:opacity-50 text-dos-blue font-heading font-bold px-6 py-3 sm:py-4 rounded-lg transition-opacity duration-300 active:scale-95 flex items-center gap-2 min-h-[48px] sm:min-h-[44px]"
              aria-label="Enviar pregunta"
            >
              <span className="text-lg">🔍</span>
              <span className="hidden sm:inline">Buscar</span>
            </button>
          </div>

          {result && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="mt-6 p-4 bg-dos-orange/10 border-l-4 border-dos-orange rounded-lg"
              role="status"
              aria-live="polite"
            >
              <p className="text-dos-blue font-body">{result}</p>
            </motion.div>
          )}
        </motion.form>

        <motion.p
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          transition={{ duration: 0.6, delay: 0.3 }}
          viewport={{ once: true }}
          className="text-center text-sm text-dos-gray-dark mt-6"
        >
          Ejemplos: "¿Qué equipo ganó el ACB 2023?", "Asistencias de Vinicius vs Warriors", "Récords de mates en EuroLeague"
        </motion.p>
      </div>
    </section>
  )
}
