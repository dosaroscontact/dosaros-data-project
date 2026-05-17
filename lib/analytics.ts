/**
 * Sistema de tracking de DOS AROS
 *
 * Push events to GTM dataLayer (GTM-MWDXWXZN).
 * Configurar en GTM: triggers de tipo "Custom Event" con cada nombre.
 *
 * Naming convention: lowercase_snake_case, object_action format.
 * Compatible GA4: parámetros estándar reciben el mismo nombre.
 */

declare global {
  interface Window {
    dataLayer?: Record<string, unknown>[]
  }
}

// ========== TIPOS DE EVENTOS ==========

export type NavLocation = 'header_desktop' | 'header_mobile' | 'footer'

export type CtaLocation =
  | 'hero_primary'
  | 'hero_secondary'
  | 'highlights_view_all'
  | 'products_view_all'
  | 'analysis_view_all'

export type SocialPlatform = 'twitter' | 'instagram'

export type SocialLocation = 'navbar' | 'footer' | 'mobile_menu'

export interface NavClickedEvent {
  event: 'nav_clicked'
  link_text: string
  link_url: string
  nav_location: NavLocation
}

export interface CtaClickedEvent {
  event: 'cta_clicked'
  cta_text: string
  cta_location: CtaLocation
  destination: string
}

export interface ProductInterestEvent {
  event: 'product_interest'
  product_name: string
  product_category: string
  action: 'view_disponibilidad'
}

export interface CategoryChangedEvent {
  event: 'category_changed'
  category_id: string
  category_name: string
}

export interface AnalysisClickedEvent {
  event: 'analysis_clicked'
  analysis_slug: string
  analysis_title: string
  analysis_date: string
}

export interface TagFilterClickedEvent {
  event: 'tag_filter_clicked'
  tag_name: string
}

export interface FormSubmittedEvent {
  event: 'form_submitted'
  form_name: 'contact'
  status: 'success' | 'error'
  source_product?: string
}

export interface SocialClickedEvent {
  event: 'social_clicked'
  platform: SocialPlatform
  handle: string
  location: SocialLocation
}

export interface PageViewEvent {
  event: 'page_view'
  page_path: string
  page_title: string
  page_referrer: string
}

export type DosArosEvent =
  | NavClickedEvent
  | CtaClickedEvent
  | ProductInterestEvent
  | CategoryChangedEvent
  | AnalysisClickedEvent
  | TagFilterClickedEvent
  | FormSubmittedEvent
  | SocialClickedEvent
  | PageViewEvent

// ========== HELPER ==========

/**
 * Push de un evento al dataLayer de GTM.
 * Safe en SSR (silently no-op).
 */
export function trackEvent(event: DosArosEvent): void {
  if (typeof window === 'undefined') return
  window.dataLayer = window.dataLayer || []
  window.dataLayer.push(event as unknown as Record<string, unknown>)

  // Debug en desarrollo
  if (process.env.NODE_ENV === 'development') {
    console.log('[analytics]', event)
  }
}
