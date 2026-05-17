/**
 * Renderiza los HTMLs de la campaña de lanzamiento a PNG con dimensiones exactas.
 *
 * Uso:
 *   cd assets/launch-campaign
 *   node render.mjs
 *
 * Requiere puppeteer (instalación automática):
 *   npm install --no-save puppeteer
 */

import puppeteer from 'puppeteer'
import { fileURLToPath } from 'url'
import { dirname, resolve } from 'path'

const __dirname = dirname(fileURLToPath(import.meta.url))

const TARGETS = [
  {
    name: 'whatsapp-instagram-story',
    html: 'story-vertical.html',
    width: 1080,
    height: 1920,
    output: 'launch-story-1080x1920.png',
  },
  {
    name: 'twitter-x-post',
    html: 'twitter-horizontal.html',
    width: 1200,
    height: 675,
    output: 'launch-twitter-1200x675.png',
  },
  {
    name: 'instagram-post-square',
    html: 'instagram-post-square.html',
    width: 1080,
    height: 1080,
    output: 'launch-instagram-post-1080x1080.png',
  },
]

console.log('🚀 Iniciando renderer Puppeteer...\n')

const browser = await puppeteer.launch({
  headless: 'new',
  args: ['--font-render-hinting=none'],
})

for (const t of TARGETS) {
  console.log(`📸 Renderizando ${t.name} (${t.width}x${t.height})...`)
  const page = await browser.newPage()
  await page.setViewport({
    width: t.width,
    height: t.height,
    deviceScaleFactor: 2, // Retina quality
  })

  const fileUrl = `file:///${resolve(__dirname, t.html).replace(/\\/g, '/')}`
  await page.goto(fileUrl, { waitUntil: 'networkidle0' })

  // Esperar fonts de Google
  await page.evaluateHandle('document.fonts.ready')
  await new Promise(r => setTimeout(r, 800))

  const outputPath = resolve(__dirname, t.output)
  await page.screenshot({
    path: outputPath,
    type: 'png',
    clip: { x: 0, y: 0, width: t.width, height: t.height },
  })

  console.log(`   ✅ ${t.output} (${t.width * 2}x${t.height * 2} @2x retina)`)
  await page.close()
}

await browser.close()
console.log('\n✨ Listo. PNGs en assets/launch-campaign/')
