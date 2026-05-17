import fs from 'fs'
import path from 'path'
import matter from 'gray-matter'

export interface AnalysisSection {
  league: string
  icon?: string
  title: string
  subtitle?: string
}

export interface AnalysisMeta {
  slug: string
  date: string
  title: string
  summary: string
  tags: string[]
  sections: AnalysisSection[]
  published: boolean
}

export interface Analysis extends AnalysisMeta {
  content: string
}

const CONTENT_ROOT = path.join(process.cwd(), 'content', 'analysis')

/**
 * Recorre recursivamente content/analysis/ y devuelve todos los archivos .md
 */
function walkMarkdownFiles(dir: string): string[] {
  if (!fs.existsSync(dir)) return []

  const results: string[] = []
  const entries = fs.readdirSync(dir, { withFileTypes: true })

  for (const entry of entries) {
    const fullPath = path.join(dir, entry.name)
    if (entry.isDirectory()) {
      results.push(...walkMarkdownFiles(fullPath))
    } else if (entry.isFile() && entry.name.endsWith('.md')) {
      results.push(fullPath)
    }
  }

  return results
}

/**
 * Lee y parsea un .md de análisis
 */
/**
 * Elimina emojis decorativos al inicio de los H2 (banderas, círculos, etc.)
 * que no renderizan consistentemente en todas las plataformas.
 * El branding por color ya distingue las ligas en los badges.
 */
function stripFlagEmojis(text: string): string {
  // Solo strip al INICIO de líneas H2 (## ...)
  return text.replace(/^(##\s+)((?:\uD83C[\uDDE6-\uDDFF]){2}|🟠|🟡|🟢|🔵|🟣|🔴|⚫|⚪)\s*/gm, '$1')
}

function parseAnalysisFile(filePath: string): Analysis | null {
  try {
    const raw = fs.readFileSync(filePath, 'utf-8')
    const { data, content } = matter(raw)

    if (data.published === false) return null

    // YAML puede parsear 2026-05-16 como Date — normalizar a string YYYY-MM-DD
    let dateStr = ''
    if (data.date instanceof Date) {
      dateStr = data.date.toISOString().split('T')[0]
    } else if (data.date) {
      dateStr = String(data.date)
    }

    return {
      slug: String(data.slug || path.basename(filePath, '.md')),
      date: dateStr,
      title: String(data.title || 'Sin título'),
      summary: String(data.summary || ''),
      tags: Array.isArray(data.tags) ? data.tags.map(String) : [],
      sections: Array.isArray(data.sections) ? data.sections : [],
      published: data.published !== false,
      content: stripFlagEmojis(content),
    }
  } catch (err) {
    console.error(`Error parsing ${filePath}:`, err)
    return null
  }
}

/**
 * Devuelve todos los análisis publicados, ordenados por fecha descendente
 */
export function getAllAnalyses(): AnalysisMeta[] {
  const files = walkMarkdownFiles(CONTENT_ROOT)
  const analyses = files
    .map(parseAnalysisFile)
    .filter((a): a is Analysis => a !== null)
    .sort((a, b) => b.date.localeCompare(a.date))

  // Devolver sin el content (más ligero para listings)
  return analyses.map(({ content, ...meta }) => meta)
}

/**
 * Devuelve un análisis específico por slug
 */
export function getAnalysisBySlug(slug: string): Analysis | null {
  const files = walkMarkdownFiles(CONTENT_ROOT)
  for (const file of files) {
    const parsed = parseAnalysisFile(file)
    if (parsed && parsed.slug === slug) {
      return parsed
    }
  }
  return null
}

/**
 * Devuelve los slugs de todos los análisis (para generateStaticParams)
 */
export function getAllSlugs(): string[] {
  return getAllAnalyses().map((a) => a.slug)
}

/**
 * Devuelve todos los tags únicos con conteo
 */
export function getAllTags(): { tag: string; count: number }[] {
  const counts = new Map<string, number>()
  for (const analysis of getAllAnalyses()) {
    for (const tag of analysis.tags) {
      counts.set(tag, (counts.get(tag) || 0) + 1)
    }
  }
  return Array.from(counts.entries())
    .map(([tag, count]) => ({ tag, count }))
    .sort((a, b) => b.count - a.count)
}

/**
 * Filtra análisis por tag
 */
export function getAnalysesByTag(tag: string): AnalysisMeta[] {
  return getAllAnalyses().filter((a) =>
    a.tags.some((t) => t.toLowerCase() === tag.toLowerCase())
  )
}

/**
 * Formatea fecha YYYY-MM-DD a "16 de mayo de 2026"
 */
export function formatDateES(dateStr: string): string {
  const [y, m, d] = dateStr.split('-')
  const months = [
    'enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
    'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre',
  ]
  const monthName = months[parseInt(m, 10) - 1]
  return `${parseInt(d, 10)} de ${monthName} de ${y}`
}
