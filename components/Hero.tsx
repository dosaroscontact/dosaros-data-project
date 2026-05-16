'use client'

import Image from 'next/image'
import { motion } from 'framer-motion'
import { useReducedMotion } from '@/lib/hooks'

export default function Hero() {
  const prefersReducedMotion = useReducedMotion()

  const logoVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: { duration: prefersReducedMotion ? 0 : 0.6, ease: 'easeOut' },
    },
  }

  const headlineVariants = {
    hidden: { y: 20, opacity: 0 },
    visible: {
      y: 0,
      opacity: 1,
      transition: { duration: prefersReducedMotion ? 0 : 0.8, ease: 'easeOut', delay: 0.2 },
    },
  }

  const ctaVariants = {
    hidden: { opacity: 0, scale: 0.9 },
    visible: {
      opacity: 1,
      scale: 1,
      transition: { duration: prefersReducedMotion ? 0 : 0.6, ease: 'easeOut', delay: 0.4 },
    },
  }

  return (
    <section className="relative w-full min-h-[60vh] pt-24 sm:pt-32 pb-12 sm:pb-16 bg-gradient-to-br from-dos-blue to-dos-blue-dark flex items-center justify-center px-4 sm:px-6 overflow-hidden">
      {/* Decorative background elements */}
      <div className="absolute inset-0 opacity-10">
        <div className="absolute top-10 left-10 w-64 h-64 bg-dos-magenta rounded-full mix-blend-screen blur-3xl"></div>
        <div className="absolute bottom-10 right-10 w-80 h-80 bg-dos-orange rounded-full mix-blend-screen blur-3xl"></div>
      </div>

      <motion.div
        initial="hidden"
        animate="visible"
        variants={{
          visible: { transition: { staggerChildren: 0.1 } },
        }}
        className="relative z-10 w-full max-w-2xl text-center"
      >
        {/* Logo */}
        <motion.div variants={logoVariants} className="mb-8 sm:mb-12">
          <Image
            src="/logo-dos-aros-official.png"
            alt="DOS AROS logo"
            width={40}
            height={40}
            className="w-8 h-8 sm:w-10 sm:h-10"
            priority
          />
        </motion.div>

        {/* Headline with Lettering Banner */}
        <motion.div
          variants={headlineVariants}
          className="w-full max-w-2xl mx-auto mb-4 sm:mb-6"
        >
          <Image
            src="/banners/letering-orange.png"
            alt="DOS AROS - Analytics para el deporte que amamos"
            width={2744}
            height={447}
            className="w-full h-auto"
            priority
          />
        </motion.div>

        {/* Subheading */}
        <motion.p
          variants={headlineVariants}
          className="text-lg sm:text-xl text-dos-gray mb-8 sm:mb-12 max-w-xl mx-auto leading-relaxed"
        >
          Data-driven insights para NBA, EuroLeague, y más. Haz preguntas. Obtén respuestas.
        </motion.p>

        {/* CTA Buttons */}
        <motion.div
          variants={ctaVariants}
          className="flex flex-col sm:flex-row gap-4 sm:gap-6 justify-center items-center"
        >
          <button
            className="w-full sm:w-auto px-8 py-3 bg-dos-orange text-dos-blue font-heading font-bold rounded-lg hover:opacity-90 focus:outline-2 focus:outline-offset-2 focus:outline-dos-magenta transition-opacity duration-300 active:scale-95 min-h-[48px] sm:min-h-[44px]"
            aria-label="Explorar partidos en vivo"
          >
            Explora partidos en vivo
          </button>
          <button
            className="w-full sm:w-auto px-8 py-3 border-2 border-dos-magenta text-dos-white font-heading font-bold rounded-lg hover:bg-dos-magenta/10 focus:outline-2 focus:outline-offset-2 focus:outline-dos-magenta transition-colors duration-300 active:scale-95 min-h-[48px] sm:min-h-[44px]"
            aria-label="Haz una pregunta"
          >
            Haz una pregunta
          </button>
        </motion.div>

        {/* Scroll indicator */}
        <motion.div
          animate={prefersReducedMotion ? {} : { y: [0, 8, 0] }}
          transition={{ duration: 2, repeat: Infinity }}
          className="absolute bottom-8 left-1/2 -translate-x-1/2 text-dos-gray"
          aria-hidden="true"
        >
          <svg
            className="w-6 h-6"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M19 14l-7 7m0 0l-7-7m7 7V3"
            />
          </svg>
        </motion.div>
      </motion.div>
    </section>
  )
}
