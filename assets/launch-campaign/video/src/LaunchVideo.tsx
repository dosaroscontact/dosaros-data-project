import {
  AbsoluteFill,
  Img,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  spring,
  Sequence,
} from 'remotion'
import { loadFont as loadSpaceGrotesk } from '@remotion/google-fonts/SpaceGrotesk'
import { loadFont as loadInter } from '@remotion/google-fonts/Inter'
import { loadFont as loadJetBrainsMono } from '@remotion/google-fonts/JetBrainsMono'

const { fontFamily: SPACE_GROTESK } = loadSpaceGrotesk()
const { fontFamily: INTER } = loadInter()
const { fontFamily: JETBRAINS } = loadJetBrainsMono()

// DOS AROS brand palette
const BRAND = {
  blue: '#011E3B',
  orange: '#FF7D28',
  orangeDark: '#FF3E04',
  magenta: '#B1005A',
  gray: '#E6E8EE',
  white: '#FFFFFF',
}

const FONT_HEADING = SPACE_GROTESK
const FONT_BODY = INTER
const FONT_MONO = JETBRAINS

type LaunchProps = { format: 'vertical' | 'square' | 'horizontal' }

export const LaunchVideo: React.FC<LaunchProps> = ({ format }) => {
  return (
    <AbsoluteFill style={{ backgroundColor: BRAND.white, fontFamily: FONT_BODY }}>
      {/* SCENE 1 — Brand intro (0-90 frames = 0-3s) */}
      <Sequence from={0} durationInFrames={120}>
        <BrandIntro format={format} />
      </Sequence>

      {/* SCENE 2 — Datos primero (90-180 = 3-6s) */}
      <Sequence from={90} durationInFrames={120}>
        <PhilosophyLine text="Datos primero." color={BRAND.blue} format={format} />
      </Sequence>

      {/* SCENE 3 — Contexto después (180-270 = 6-9s) */}
      <Sequence from={180} durationInFrames={120}>
        <PhilosophyLine text="Contexto después." color={BRAND.blue} format={format} />
      </Sequence>

      {/* SCENE 4 — Opinión al final (270-390 = 9-13s) */}
      <Sequence from={270} durationInFrames={150}>
        <PhilosophyLine text="Opinión al final." color={BRAND.blue} format={format} showAccent />
      </Sequence>

      {/* SCENE 5 — Productos catálogo (390-540 = 13-18s) */}
      <Sequence from={390} durationInFrames={180}>
        <CatalogScene format={format} />
      </Sequence>

      {/* SCENE 6 — CTA (540-750 = 18-25s) */}
      <Sequence from={540} durationInFrames={210}>
        <CtaScene format={format} />
      </Sequence>
    </AbsoluteFill>
  )
}

// ============================================================
// SCENE COMPONENTS
// ============================================================

const BrandIntro: React.FC<{ format: string }> = ({ format }) => {
  const frame = useCurrentFrame()
  const { fps } = useVideoConfig()

  const logoOpacity = spring({ frame, fps, config: { damping: 14, stiffness: 100 } })
  const logoScale = spring({ frame, fps, from: 0.85, to: 1, config: { damping: 12, stiffness: 100 } })

  const letteringOpacity = interpolate(frame, [15, 40], [0, 1], { extrapolateRight: 'clamp' })
  const letteringX = interpolate(frame, [15, 40], [-30, 0], { extrapolateRight: 'clamp' })

  const isVertical = format === 'vertical'
  const logoSize = isVertical ? 220 : 180
  const letteringHeight = isVertical ? 220 : 180

  return (
    <AbsoluteFill style={{ alignItems: 'center', justifyContent: 'center', flexDirection: 'column' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 40 }}>
        <Img
          src={staticFile('logo-dos-aros-official.png')}
          style={{
            width: logoSize,
            height: logoSize,
            objectFit: 'contain',
            opacity: logoOpacity,
            transform: `scale(${logoScale})`,
          }}
        />
        <Img
          src={staticFile('letering-orange.png')}
          style={{
            height: letteringHeight,
            objectFit: 'contain',
            opacity: letteringOpacity,
            transform: `translateX(${letteringX}px)`,
          }}
        />
      </div>
    </AbsoluteFill>
  )
}

const PhilosophyLine: React.FC<{
  text: string
  color: string
  format: string
  showAccent?: boolean
}> = ({ text, color, format, showAccent }) => {
  const frame = useCurrentFrame()
  const { fps } = useVideoConfig()

  const textOpacity = spring({ frame, fps, config: { damping: 18, stiffness: 80 } })
  const textY = interpolate(spring({ frame, fps, config: { damping: 18, stiffness: 80 } }), [0, 1], [40, 0])

  const accentWidth = showAccent
    ? spring({ frame: Math.max(0, frame - 25), fps, from: 0, to: 1, config: { damping: 16, stiffness: 110 } })
    : 0

  const isVertical = format === 'vertical'
  const fontSize = isVertical ? 140 : 110

  return (
    <AbsoluteFill style={{ alignItems: 'center', justifyContent: 'center', flexDirection: 'column' }}>
      <div
        style={{
          fontFamily: FONT_HEADING,
          fontWeight: 700,
          fontSize,
          letterSpacing: '-0.04em',
          color,
          opacity: textOpacity,
          transform: `translateY(${textY}px)`,
          lineHeight: 1,
        }}
      >
        {text}
      </div>
      {showAccent && (
        <div
          style={{
            width: 280 * accentWidth,
            height: 14,
            background: BRAND.orange,
            borderRadius: 4,
            marginTop: 40,
          }}
        />
      )}
    </AbsoluteFill>
  )
}

const CatalogScene: React.FC<{ format: string }> = ({ format }) => {
  const frame = useCurrentFrame()
  const { fps } = useVideoConfig()

  const imgOpacity = spring({ frame, fps, config: { damping: 18, stiffness: 80 } })
  const imgScale = interpolate(frame, [0, 180], [1.08, 1], { extrapolateRight: 'clamp' })

  const labelOpacity = interpolate(frame, [20, 50], [0, 1], { extrapolateRight: 'clamp' })
  const subtitleOpacity = interpolate(frame, [40, 70], [0, 1], { extrapolateRight: 'clamp' })

  const isVertical = format === 'vertical'

  return (
    <AbsoluteFill style={{ alignItems: 'center', justifyContent: 'center' }}>
      {/* Catalog image background */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          opacity: imgOpacity,
          overflow: 'hidden',
        }}
      >
        <Img
          src={staticFile('catalogo-dos-aros.png')}
          style={{
            width: '100%',
            height: '100%',
            objectFit: 'cover',
            transform: `scale(${imgScale})`,
          }}
        />
        <div
          style={{
            position: 'absolute',
            inset: 0,
            background: 'linear-gradient(180deg, rgba(255,255,255,0.95) 0%, rgba(255,255,255,0.5) 30%, rgba(255,255,255,0.5) 70%, rgba(255,255,255,0.95) 100%)',
          }}
        />
      </div>

      {/* Label */}
      <div
        style={{
          position: 'relative',
          fontFamily: FONT_MONO,
          fontSize: isVertical ? 32 : 26,
          fontWeight: 500,
          letterSpacing: '0.16em',
          textTransform: 'uppercase',
          color: BRAND.magenta,
          opacity: labelOpacity,
          marginBottom: 28,
        }}
      >
        Catálogo oficial
      </div>

      {/* Subtitle */}
      <div
        style={{
          position: 'relative',
          fontFamily: FONT_HEADING,
          fontSize: isVertical ? 80 : 60,
          fontWeight: 700,
          color: BRAND.blue,
          opacity: subtitleOpacity,
          textAlign: 'center',
          lineHeight: 1.1,
          letterSpacing: '-0.03em',
          padding: '0 60px',
        }}
      >
        Camisetas · Sudaderas<br />Gorras · Totebags
      </div>
    </AbsoluteFill>
  )
}

const CtaScene: React.FC<{ format: string }> = ({ format }) => {
  const frame = useCurrentFrame()
  const { fps } = useVideoConfig()

  const labelOpacity = spring({ frame, fps, config: { damping: 18, stiffness: 80 } })
  const ctaOpacity = interpolate(frame, [25, 55], [0, 1], { extrapolateRight: 'clamp' })
  const ctaY = interpolate(spring({ frame: Math.max(0, frame - 25), fps, config: { damping: 18, stiffness: 80 } }), [0, 1], [40, 0])

  // Pulse en el CTA: scale sutil
  const pulse = 1 + 0.025 * Math.sin((frame - 60) / 8)
  const ctaScale = frame > 60 ? pulse : 1

  const isVertical = format === 'vertical'

  return (
    <AbsoluteFill style={{ alignItems: 'center', justifyContent: 'center', flexDirection: 'column' }}>
      <div
        style={{
          fontFamily: FONT_MONO,
          fontSize: isVertical ? 32 : 26,
          fontWeight: 500,
          letterSpacing: '0.16em',
          textTransform: 'uppercase',
          color: BRAND.magenta,
          opacity: labelOpacity,
          marginBottom: 40,
        }}
      >
        Ya disponible
      </div>

      <div
        style={{
          fontFamily: FONT_HEADING,
          fontSize: isVertical ? 100 : 80,
          fontWeight: 700,
          color: BRAND.blue,
          opacity: labelOpacity,
          letterSpacing: '-0.03em',
          marginBottom: 60,
          textAlign: 'center',
        }}
      >
        Análisis diario<br />NBA + EuroLeague
      </div>

      <div
        style={{
          background: BRAND.orange,
          color: BRAND.blue,
          padding: isVertical ? '40px 80px' : '32px 64px',
          fontFamily: FONT_HEADING,
          fontWeight: 700,
          fontSize: isVertical ? 72 : 56,
          borderRadius: 20,
          opacity: ctaOpacity,
          transform: `translateY(${ctaY}px) scale(${ctaScale})`,
          display: 'flex',
          alignItems: 'center',
          gap: 20,
          boxShadow: '0 20px 60px rgba(255,125,40,0.3)',
        }}
      >
        <span>dosaros.com</span>
        <span style={{ fontSize: isVertical ? 80 : 64 }}>→</span>
      </div>
    </AbsoluteFill>
  )
}
