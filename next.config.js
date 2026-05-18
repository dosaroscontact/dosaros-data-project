/** @type {import('next').NextConfig} */

/**
 * Tabla de redirects de campaña: dosaros.com/r/<slug> → URL UTM completa
 *
 * Cada entry: { slug, dest, utm_content }
 * El medium/source se infiere del slug para mantener consistencia.
 *
 * Filosofía:
 * - Slugs cortos y memorables
 * - Misma campaña launch_2026_05
 * - 302 temporal (la campaña terminará)
 */
const CAMPAIGN = 'launch_2026_05'

function buildUtmUrl(path, source, medium, content) {
  const params = new URLSearchParams({
    utm_source: source,
    utm_medium: medium,
    utm_campaign: CAMPAIGN,
    utm_content: content,
  })
  return `https://www.dosaros.com${path}?${params.toString()}`
}

const REDIRECTS = [
  // ===== DÍA 1 (DROP DAY) =====
  { slug: 'd1-x',         dest: buildUtmUrl('/', 'twitter',   'organic_post',   'day1_drop') },
  { slug: 'd1-ig',        dest: buildUtmUrl('/', 'instagram', 'organic_post',   'day1_feed') },
  { slug: 'd1-story',     dest: buildUtmUrl('/', 'instagram', 'organic_story',  'day1_story') },
  { slug: 'd1-wa',        dest: buildUtmUrl('/', 'whatsapp',  'organic_status', 'day1_status') },
  { slug: 'd1-reel',      dest: buildUtmUrl('/', 'instagram', 'organic_reel',   'day1_reel') },
  { slug: 'd1-xvideo',    dest: buildUtmUrl('/', 'twitter',   'organic_video',  'day1_video') },

  // ===== DÍA 2 (X Thread) =====
  { slug: 'd2-analisis',  dest: buildUtmUrl('/analisis',     'twitter',   'organic_thread',   'day2_thread_analisis') },
  { slug: 'd2-productos', dest: buildUtmUrl('/productos',    'twitter',   'organic_thread',   'day2_thread_productos') },
  { slug: 'd2-compes',    dest: buildUtmUrl('/competiciones','twitter',   'organic_thread',   'day2_thread_competiciones') },
  { slug: 'd2-cierre',    dest: buildUtmUrl('/',             'twitter',   'organic_thread',   'day2_thread_cierre') },
  { slug: 'd2-story',     dest: buildUtmUrl('/',             'instagram', 'organic_story',    'day2_story') },

  // ===== DÍA 3 (IG Reel productos) =====
  { slug: 'd3-reel',      dest: buildUtmUrl('/productos', 'instagram', 'organic_reel', 'day3_reel_productos') },
  { slug: 'd3-analisis',  dest: buildUtmUrl('/analisis',  'twitter',   'organic_post', 'day3_analisis') },

  // ===== DÍA 4 (EuroLeague) =====
  { slug: 'd4-preview',   dest: buildUtmUrl('/analisis', 'twitter',   'organic_post',  'day4_euro_preview') },
  { slug: 'd4-recap',     dest: buildUtmUrl('/analisis', 'instagram', 'organic_story', 'day4_euro_recap') },

  // ===== DÍA 5 (Resumen + carrusel) =====
  { slug: 'd5-weekly',    dest: buildUtmUrl('/analisis',  'twitter',   'organic_post',     'day5_weekly_recap') },
  { slug: 'd5-carousel',  dest: buildUtmUrl('/productos', 'instagram', 'organic_carousel', 'day5_carousel') },
  { slug: 'd5-repost-ig', dest: buildUtmUrl('/',          'instagram', 'organic_story',    'day5_repost') },
  { slug: 'd5-repost-wa', dest: buildUtmUrl('/',          'whatsapp',  'organic_status',   'day5_repost') },

  // ===== DÍA 6 (Sábado) =====
  { slug: 'd6-reel',      dest: buildUtmUrl('/productos', 'instagram', 'organic_reel', 'day6_reel_catalogo') },

  // ===== DÍA 7 (Domingo recap) =====
  { slug: 'd7-summary',   dest: buildUtmUrl('/',         'twitter',   'organic_thread', 'day7_weekly_summary') },
  { slug: 'd7-poll',      dest: buildUtmUrl('/analisis', 'instagram', 'organic_story',  'day7_poll') },

  // ===== Bio Links permanentes =====
  { slug: 'ig',           dest: buildUtmUrl('/', 'instagram', 'bio_link', 'bio_permanent') },
  { slug: 'x',            dest: buildUtmUrl('/', 'twitter',   'bio_link', 'bio_permanent') },
  { slug: 'wa',           dest: buildUtmUrl('/', 'whatsapp',  'bio_link', 'bio_permanent') },
]

const nextConfig = {
  images: {
    formats: ['image/avif', 'image/webp'],
  },
  headers: async () => {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'Cache-Control',
            value: 'public, max-age=3600, stale-while-revalidate=86400',
          },
        ],
      },
    ]
  },
  redirects: async () => {
    return REDIRECTS.map(({ slug, dest }) => ({
      source: `/r/${slug}`,
      destination: dest,
      permanent: false, // 302 — son links de campaña temporal
    }))
  },
}

module.exports = nextConfig
