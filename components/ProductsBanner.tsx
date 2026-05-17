'use client'

import Image from 'next/image'
import { useEffect, useRef, useState } from 'react'
import { motion, useMotionValue, useSpring, useTransform } from 'framer-motion'
import { useReducedMotion } from '@/lib/hooks'

export default function ProductsBanner() {
  const prefersReducedMotion = useReducedMotion()
  const containerRef = useRef<HTMLDivElement>(null)
  const [isDesktop, setIsDesktop] = useState(false)

  // Motion values para tilt con mouse (solo desktop)
  const mouseX = useMotionValue(0)
  const mouseY = useMotionValue(0)
  const springConfig = { stiffness: 80, damping: 20, mass: 0.8 }
  const rotateXSpring = useSpring(useTransform(mouseY, [-1, 1], [4, -4]), springConfig)
  const rotateYSpring = useSpring(useTransform(mouseX, [-1, 1], [-4, 4]), springConfig)

  useEffect(() => {
    // Detectar desktop (mobile-first: por defecto NO desktop)
    const mql = window.matchMedia('(min-width: 768px) and (hover: hover) and (pointer: fine)')
    setIsDesktop(mql.matches)
    const handler = (e: MediaQueryListEvent) => setIsDesktop(e.matches)
    mql.addEventListener('change', handler)
    return () => mql.removeEventListener('change', handler)
  }, [])

  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!isDesktop || prefersReducedMotion || !containerRef.current) return
    const rect = containerRef.current.getBoundingClientRect()
    const x = ((e.clientX - rect.left) / rect.width - 0.5) * 2
    const y = ((e.clientY - rect.top) / rect.height - 0.5) * 2
    mouseX.set(x)
    mouseY.set(y)
  }

  const handleMouseLeave = () => {
    mouseX.set(0)
    mouseY.set(0)
  }

  return (
    <section
      className="relative w-full px-4 sm:px-6 pt-8 pb-12 sm:pt-12 sm:pb-16 overflow-hidden"
      aria-label="Banner del catálogo DOS AROS"
    >
      {/* Soft gradient backdrop matching the rest of the catalog */}
      <div className="absolute inset-0 bg-gradient-to-br from-dos-blue/5 to-dos-magenta/5 pointer-events-none" />

      {/* Decorative animated blobs (subtle background depth) */}
      <div className="absolute inset-0 opacity-50 pointer-events-none" aria-hidden="true">
        <motion.div
          className="absolute top-0 left-1/4 w-64 sm:w-96 h-64 sm:h-96 bg-dos-orange/20 rounded-full mix-blend-multiply dark:mix-blend-screen blur-3xl"
          animate={prefersReducedMotion ? {} : { x: [0, 30, 0], y: [0, -20, 0] }}
          transition={{ duration: 12, repeat: Infinity, ease: 'easeInOut' }}
        />
        <motion.div
          className="absolute bottom-0 right-1/4 w-64 sm:w-96 h-64 sm:h-96 bg-dos-magenta/20 rounded-full mix-blend-multiply dark:mix-blend-screen blur-3xl"
          animate={prefersReducedMotion ? {} : { x: [0, -30, 0], y: [0, 20, 0] }}
          transition={{ duration: 14, repeat: Infinity, ease: 'easeInOut' }}
        />
      </div>

      <div
        className="relative max-w-6xl mx-auto"
        style={{ perspective: '1500px' }}
      >
        {/* Wrapper para tilt mouse-follow + floating continuo */}
        <motion.div
          ref={containerRef}
          onMouseMove={handleMouseMove}
          onMouseLeave={handleMouseLeave}
          initial={
            prefersReducedMotion
              ? { opacity: 0 }
              : { opacity: 0, y: 60, rotateX: -12, scale: 0.9 }
          }
          animate={
            prefersReducedMotion
              ? { opacity: 1 }
              : { opacity: 1, y: 0, rotateX: 0, scale: 1 }
          }
          transition={{
            duration: prefersReducedMotion ? 0 : 1.2,
            ease: [0.16, 1, 0.3, 1],
            scale: { type: 'spring', stiffness: 120, damping: 14 },
          }}
          style={
            prefersReducedMotion
              ? undefined
              : {
                  rotateX: isDesktop ? rotateXSpring : undefined,
                  rotateY: isDesktop ? rotateYSpring : undefined,
                  transformStyle: 'preserve-3d',
                }
          }
          className="relative rounded-2xl overflow-hidden shadow-2xl shadow-dos-blue/30 border border-dos-gray/20 dark:border-dos-magenta/30 bg-dos-white dark:bg-dos-blue-dark"
        >
          {/* Floating continuo (todos los dispositivos) */}
          <motion.div
            animate={
              prefersReducedMotion
                ? {}
                : { y: [0, -6, 0] }
            }
            transition={{ duration: 5, repeat: Infinity, ease: 'easeInOut' }}
            className="relative"
          >
            {/* Banner image con Ken Burns lento */}
            <motion.div
              className="relative w-full aspect-[16/9] sm:aspect-[24/9]"
              initial={prefersReducedMotion ? { scale: 1 } : { scale: 1.15 }}
              animate={prefersReducedMotion ? { scale: 1 } : { scale: 1 }}
              transition={{ duration: 2.5, ease: [0.22, 1, 0.36, 1] }}
            >
              <motion.div
                className="absolute inset-0"
                animate={
                  prefersReducedMotion
                    ? {}
                    : { scale: [1, 1.04, 1] }
                }
                transition={{ duration: 18, repeat: Infinity, ease: 'easeInOut' }}
              >
                <Image
                  src="/productos/catalogo-banner.png"
                  alt="Catálogo DOS AROS — colección oficial"
                  fill
                  priority
                  sizes="(max-width: 768px) 100vw, (max-width: 1280px) 90vw, 1152px"
                  className="object-cover"
                />
              </motion.div>

              {/* Light sweep — pasa una vez al entrar */}
              {!prefersReducedMotion && (
                <motion.div
                  aria-hidden="true"
                  className="absolute inset-0 pointer-events-none"
                  initial={{ x: '-100%', opacity: 0 }}
                  animate={{ x: '120%', opacity: [0, 0.5, 0] }}
                  transition={{ duration: 1.6, delay: 0.6, ease: 'easeOut' }}
                  style={{
                    background:
                      'linear-gradient(105deg, transparent 30%, rgba(255,255,255,0.35) 50%, transparent 70%)',
                    mixBlendMode: 'overlay',
                  }}
                />
              )}

              {/* Gloss reflection sutil (respira) */}
              {!prefersReducedMotion && (
                <motion.div
                  aria-hidden="true"
                  className="absolute inset-x-0 top-0 h-1/3 bg-gradient-to-b from-dos-white/15 to-transparent pointer-events-none"
                  animate={{ opacity: [0.4, 0.65, 0.4] }}
                  transition={{ duration: 6, repeat: Infinity, ease: 'easeInOut' }}
                />
              )}
            </motion.div>
          </motion.div>

          {/* Borde glow pulsante en esquinas (decorativo) */}
          {!prefersReducedMotion && (
            <>
              <motion.div
                aria-hidden="true"
                className="absolute -top-px -left-px w-16 h-16 sm:w-24 sm:h-24 border-t-2 border-l-2 border-dos-orange/0 rounded-tl-2xl pointer-events-none"
                animate={{ borderColor: ['rgba(255,125,40,0)', 'rgba(255,125,40,0.6)', 'rgba(255,125,40,0)'] }}
                transition={{ duration: 4, repeat: Infinity, ease: 'easeInOut', delay: 1.2 }}
              />
              <motion.div
                aria-hidden="true"
                className="absolute -bottom-px -right-px w-16 h-16 sm:w-24 sm:h-24 border-b-2 border-r-2 border-dos-magenta/0 rounded-br-2xl pointer-events-none"
                animate={{ borderColor: ['rgba(177,0,90,0)', 'rgba(177,0,90,0.6)', 'rgba(177,0,90,0)'] }}
                transition={{ duration: 4, repeat: Infinity, ease: 'easeInOut', delay: 2.2 }}
              />
            </>
          )}
        </motion.div>
      </div>
    </section>
  )
}
