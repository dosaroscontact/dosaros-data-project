'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { useReducedMotion } from '@/lib/hooks'

export default function Newsletter() {
  const [email, setEmail] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [submitted, setSubmitted] = useState(false)
  const [error, setError] = useState('')
  const prefersReducedMotion = useReducedMotion()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    if (!email || !email.includes('@')) {
      setError('Por favor, ingresa un email válido.')
      return
    }

    setIsSubmitting(true)
    try {
      // Mock API call
      await new Promise((resolve) => setTimeout(resolve, 1000))
      setSubmitted(true)
      setEmail('')
      setTimeout(() => setSubmitted(false), 4000)
    } catch (err) {
      setError('Algo salió mal. Intenta de nuevo.')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <section className="w-full py-12 sm:py-16 md:py-20 px-4 sm:px-6 bg-dos-gray/20">
      <div className="max-w-2xl mx-auto text-center">
        <motion.h2
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: prefersReducedMotion ? 0 : 0.6 }}
          viewport={{ once: true }}
          className="text-2xl sm:text-3xl font-heading font-bold text-dos-blue mb-3"
        >
          Perlas semanales
        </motion.h2>

        <motion.p
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          transition={{ duration: 0.6, delay: 0.1 }}
          viewport={{ once: true }}
          className="text-dos-gray-dark mb-6 text-base sm:text-lg"
        >
          Recibe las mejores actuaciones, predicciones, y análisis cada semana.
        </motion.p>

        <motion.form
          onSubmit={handleSubmit}
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: prefersReducedMotion ? 0 : 0.5, delay: 0.2 }}
          viewport={{ once: true }}
          className="flex flex-col sm:flex-row gap-3"
        >
          <div className="flex-1 relative">
            <label htmlFor="newsletter-email" className="sr-only">
              Email
            </label>
            <input
              id="newsletter-email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="tu@email.com"
              disabled={isSubmitting}
              required
              className="w-full px-4 py-3 sm:py-4 bg-dos-white border-2 border-dos-gray text-dos-blue placeholder-dos-gray-dark rounded-lg font-body text-base focus:outline-none focus:border-dos-magenta disabled:opacity-50 transition-colors duration-200 min-h-[48px]"
              aria-label="Tu dirección de email"
              aria-describedby="newsletter-error"
            />
            {error && (
              <motion.p
                initial={{ opacity: 0, y: -5 }}
                animate={{ opacity: 1, y: 0 }}
                id="newsletter-error"
                className="text-red-600 text-sm mt-2 text-left"
                role="alert"
              >
                {error}
              </motion.p>
            )}
          </div>

          <button
            type="submit"
            disabled={isSubmitting || submitted}
            className="bg-dos-orange hover:opacity-90 disabled:opacity-50 text-dos-blue font-heading font-bold px-6 sm:px-8 py-3 sm:py-4 rounded-lg transition-opacity duration-300 active:scale-95 whitespace-nowrap min-h-[48px] sm:min-h-[44px]"
            aria-label="Suscribirse al boletín"
          >
            {isSubmitting ? 'Enviando...' : submitted ? '✓ Suscrito' : 'Suscribirse'}
          </button>
        </motion.form>

        {submitted && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="mt-4 p-3 bg-green-100 border border-green-300 rounded-lg text-green-800 text-sm"
            role="status"
            aria-live="polite"
          >
            ¡Gracias! Revisa tu email para confirmar la suscripción.
          </motion.div>
        )}

        <motion.p
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          transition={{ duration: 0.6, delay: 0.3 }}
          viewport={{ once: true }}
          className="text-xs text-dos-gray-dark mt-4"
        >
          No spam. Solo perlas de baloncesto. Puedes desuscriberte en cualquier momento.
        </motion.p>
      </div>
    </section>
  )
}
