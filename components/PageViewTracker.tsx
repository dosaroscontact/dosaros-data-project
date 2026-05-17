'use client'

import { useEffect } from 'react'
import { usePathname, useSearchParams } from 'next/navigation'
import { Suspense } from 'react'
import { trackEvent } from '@/lib/analytics'

function Inner() {
  const pathname = usePathname()
  const searchParams = useSearchParams()

  useEffect(() => {
    if (typeof window === 'undefined') return
    const fullPath = pathname + (searchParams.toString() ? `?${searchParams.toString()}` : '')
    trackEvent({
      event: 'page_view',
      page_path: fullPath,
      page_title: document.title,
      page_referrer: document.referrer || '',
    })
  }, [pathname, searchParams])

  return null
}

/**
 * Trackea page_view en cada navegación SPA.
 * El primer page view automático lo hace GTM al cargar.
 * Este componente captura las navegaciones client-side posteriores.
 */
export default function PageViewTracker() {
  return (
    <Suspense fallback={null}>
      <Inner />
    </Suspense>
  )
}
