'use client'

import { Suspense, useEffect, useState } from 'react'
import { useSearchParams } from 'next/navigation'
import { motion } from 'framer-motion'
import { useReducedMotion } from '@/lib/hooks'
import { trackEvent } from '@/lib/analytics'

function buildProductMessage(product: string) {
  return `Hola, me interesa: ${product}. ¿Cuáles son las opciones disponibles (talla, stock) y el precio? Gracias.`
}

function ContactFormInner() {
  const prefersReducedMotion = useReducedMotion()
  const searchParams = useSearchParams()
  const productParam = searchParams.get('product')

  const [formData, setFormData] = useState({
    nombre: '',
    email: '',
    mensaje: '',
  })
  const [loading, setLoading] = useState(false)
  const [submitted, setSubmitted] = useState(false)
  const [error, setError] = useState('')

  // Pre-rellenar mensaje con producto si viene por URL
  useEffect(() => {
    if (productParam) {
      setFormData((prev) => ({
        ...prev,
        mensaje: buildProductMessage(productParam),
      }))
    }
  }, [productParam])

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    })
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!formData.nombre || !formData.email || !formData.mensaje) {
      setError('Por favor completa todos los campos')
      return
    }

    setLoading(true)
    setError('')

    try {
      const response = await fetch('/api/contact', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      })

      if (response.ok) {
        trackEvent({
          event: 'form_submitted',
          form_name: 'contact',
          status: 'success',
          source_product: productParam || undefined,
        })
        setSubmitted(true)
        setFormData({ nombre: '', email: '', mensaje: '' })
        setTimeout(() => setSubmitted(false), 5000)
      } else {
        trackEvent({
          event: 'form_submitted',
          form_name: 'contact',
          status: 'error',
          source_product: productParam || undefined,
        })
        setError('Error al enviar el mensaje. Por favor intenta nuevamente.')
      }
    } catch (err) {
      trackEvent({
        event: 'form_submitted',
        form_name: 'contact',
        status: 'error',
        source_product: productParam || undefined,
      })
      setError('Error al enviar el mensaje. Por favor intenta nuevamente.')
    } finally {
      setLoading(false)
    }
  }

  const containerVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: { duration: prefersReducedMotion ? 0 : 0.6, ease: 'easeOut' },
    },
  }

  return (
    <section className="relative w-full py-16 sm:py-24 bg-dos-blue-dark px-4 sm:px-6">
      <div className="max-w-2xl mx-auto">
        <motion.div
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          variants={containerVariants}
          className="text-center mb-12"
        >
          <h2 className="text-3xl sm:text-4xl font-heading font-bold text-dos-white mb-4">
            {productParam ? 'Consulta de producto' : 'Ponte en contacto'}
          </h2>
          <p className="text-dos-gray text-base sm:text-lg mb-6">
            {productParam
              ? `Te pondremos en contacto para resolver tu consulta sobre ${productParam}.`
              : 'La web está en fase de lanzamiento. Completa el formulario y nos pondremos en contacto contigo pronto.'}
          </p>
        </motion.div>

        <motion.div
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          variants={containerVariants}
          className="bg-dos-white/5 backdrop-blur-sm rounded-lg border border-dos-magenta/20 p-6 sm:p-8"
        >
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label htmlFor="nombre" className="block text-dos-white font-medium mb-2">
                Nombre
              </label>
              <input
                type="text"
                id="nombre"
                name="nombre"
                value={formData.nombre}
                onChange={handleChange}
                placeholder="Tu nombre"
                className="w-full px-4 py-3 bg-dos-blue/50 text-dos-white placeholder-dos-gray/50 rounded-lg border border-dos-magenta/20 focus:outline-2 focus:outline-offset-0 focus:outline-dos-orange transition-all"
                aria-label="Nombre"
              />
            </div>

            <div>
              <label htmlFor="email" className="block text-dos-white font-medium mb-2">
                Email
              </label>
              <input
                type="email"
                id="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                placeholder="tu@email.com"
                className="w-full px-4 py-3 bg-dos-blue/50 text-dos-white placeholder-dos-gray/50 rounded-lg border border-dos-magenta/20 focus:outline-2 focus:outline-offset-0 focus:outline-dos-orange transition-all"
                aria-label="Email"
              />
            </div>

            <div>
              <label htmlFor="mensaje" className="block text-dos-white font-medium mb-2">
                Mensaje
              </label>
              <textarea
                id="mensaje"
                name="mensaje"
                value={formData.mensaje}
                onChange={handleChange}
                placeholder="Tu mensaje aquí..."
                rows={5}
                className="w-full px-4 py-3 bg-dos-blue/50 text-dos-white placeholder-dos-gray/50 rounded-lg border border-dos-magenta/20 focus:outline-2 focus:outline-offset-0 focus:outline-dos-orange transition-all resize-none"
                aria-label="Mensaje"
              />
            </div>

            {error && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="text-dos-orange text-sm"
              >
                {error}
              </motion.div>
            )}

            {submitted && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="bg-dos-magenta/20 border border-dos-magenta/40 rounded-lg p-4 text-dos-white text-center"
              >
                ✓ Mensaje enviado correctamente. Nos pondremos en contacto pronto.
              </motion.div>
            )}

            <button
              type="submit"
              disabled={loading || submitted}
              className="w-full px-8 py-3 bg-dos-orange text-dos-blue font-heading font-bold rounded-lg hover:opacity-90 disabled:opacity-50 focus:outline-2 focus:outline-offset-2 focus:outline-dos-magenta transition-opacity duration-300 active:scale-95 min-h-[48px] sm:min-h-[44px]"
              aria-label="Enviar mensaje"
            >
              {loading ? '⏳ Enviando...' : submitted ? '✓ Enviado' : 'Enviar'}
            </button>
          </form>
        </motion.div>
      </div>
    </section>
  )
}

export default function ContactForm() {
  return (
    <Suspense fallback={<div className="min-h-[400px]" />}>
      <ContactFormInner />
    </Suspense>
  )
}
