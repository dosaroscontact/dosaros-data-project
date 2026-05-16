'use client'

import Image from 'next/image'
import { motion } from 'framer-motion'
import { useReducedMotion } from '@/lib/hooks'

interface UnderConstructionProps {
  title: string
  description?: string
}

export default function UnderConstruction({
  title,
  description = 'Esta página está siendo desarrollada. Vuelve pronto para ver contenido increíble.',
}: UnderConstructionProps) {
  const prefersReducedMotion = useReducedMotion()

  const containerVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: { duration: prefersReducedMotion ? 0 : 0.6, ease: 'easeOut' },
    },
  }

  return (
    <section className="relative w-full min-h-[70vh] bg-gradient-to-br from-dos-blue to-dos-blue-dark flex items-center justify-center px-4 sm:px-6 py-24">
      {/* Decorative background elements */}
      <div className="absolute inset-0 opacity-10">
        <div className="absolute top-10 left-10 w-64 h-64 bg-dos-magenta rounded-full mix-blend-screen blur-3xl"></div>
        <div className="absolute bottom-10 right-10 w-80 h-80 bg-dos-orange rounded-full mix-blend-screen blur-3xl"></div>
      </div>

      <motion.div
        initial="hidden"
        animate="visible"
        variants={containerVariants}
        className="relative z-10 text-center max-w-2xl"
      >
        {/* Logo */}
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: prefersReducedMotion ? 0 : 0.6, ease: 'easeOut' }}
          className="mb-8"
        >
          <Image
            src="/logo-dos-aros-official.png"
            alt="DOS AROS logo"
            width={80}
            height={80}
            className="w-20 h-20 mx-auto"
            priority
          />
        </motion.div>

        {/* Banner */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: prefersReducedMotion ? 0 : 0.8, delay: 0.2 }}
          className="mb-8"
        >
          <Image
            src="/banners/letering-orange.png"
            alt="DOS AROS"
            width={2744}
            height={447}
            className="w-full h-auto max-w-md mx-auto"
            priority
          />
        </motion.div>

        {/* Content */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: prefersReducedMotion ? 0 : 0.8, delay: 0.4 }}
          className="space-y-6"
        >
          <h1 className="text-3xl sm:text-4xl font-heading font-bold text-dos-white">
            {title}
          </h1>

          <div className="flex items-center justify-center gap-2">
            <div className="w-12 h-1 bg-dos-orange rounded"></div>
            <span className="text-dos-orange font-heading font-bold">EN CONSTRUCCIÓN</span>
            <div className="w-12 h-1 bg-dos-orange rounded"></div>
          </div>

          <p className="text-dos-gray text-lg leading-relaxed max-w-xl mx-auto">
            {description}
          </p>

          <motion.div
            animate={prefersReducedMotion ? {} : { y: [0, 8, 0] }}
            transition={{ duration: 2, repeat: Infinity }}
            className="pt-8 text-dos-orange text-3xl"
          >
            ⚙️
          </motion.div>
        </motion.div>
      </motion.div>
    </section>
  )
}
