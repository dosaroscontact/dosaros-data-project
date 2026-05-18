import { NextResponse } from 'next/server'

/**
 * GET /api/debug-smtp
 *
 * Endpoint TEMPORAL para verificar que las env vars SMTP están bien configuradas.
 * No expone el password completo, solo metadata (longitud, primer/último char).
 *
 * ⚠️ ELIMINAR este archivo cuando la verificación esté hecha.
 *
 * Protección básica: requiere un token simple en la URL (?key=...)
 * Cambia DEBUG_KEY en producción si te preocupa.
 */
const DEBUG_KEY = 'dosaros-debug-2026'

function mask(value: string | undefined, showChars = 3): string {
  if (!value) return '(NO CONFIGURADA)'
  if (value.length <= showChars * 2) return '*'.repeat(value.length)
  return `${value.slice(0, showChars)}***${value.slice(-showChars)} (length: ${value.length})`
}

export async function GET(request: Request) {
  const url = new URL(request.url)
  const key = url.searchParams.get('key')

  if (key !== DEBUG_KEY) {
    return NextResponse.json({ error: 'Unauthorized. Add ?key=...' }, { status: 401 })
  }

  // Detectar caracteres invisibles/problemáticos
  const passRaw = process.env.SMTP_PASS || ''
  const passHasLeadingSpace = passRaw.length !== passRaw.trimStart().length
  const passHasTrailingSpace = passRaw.length !== passRaw.trimEnd().length
  const passHasSpecialChars = /[<>&"'\\]/.test(passRaw)
  const passByteLength = Buffer.from(passRaw, 'utf8').length

  return NextResponse.json({
    environment: process.env.VERCEL_ENV || 'unknown',
    region: process.env.VERCEL_REGION || 'unknown',
    smtp_config: {
      SMTP_HOST: process.env.SMTP_HOST || '(NO CONFIGURADA)',
      SMTP_PORT: process.env.SMTP_PORT || '(NO CONFIGURADA)',
      SMTP_USER: process.env.SMTP_USER || '(NO CONFIGURADA)',
      SMTP_PASS_metadata: {
        configured: !!process.env.SMTP_PASS,
        masked: mask(process.env.SMTP_PASS, 2),
        length: passRaw.length,
        byte_length: passByteLength,
        has_leading_space: passHasLeadingSpace,
        has_trailing_space: passHasTrailingSpace,
        has_special_chars: passHasSpecialChars,
        first_char_code: passRaw.length > 0 ? passRaw.charCodeAt(0) : null,
        last_char_code: passRaw.length > 0 ? passRaw.charCodeAt(passRaw.length - 1) : null,
      },
      CONTACT_EMAIL: process.env.CONTACT_EMAIL || '(NO CONFIGURADA)',
    },
    fallback_providers: {
      WEB3FORMS_ACCESS_KEY: process.env.WEB3FORMS_ACCESS_KEY ? mask(process.env.WEB3FORMS_ACCESS_KEY) : '(NO CONFIGURADA)',
    },
    diagnostico: {
      smtp_user_matches_contact: process.env.SMTP_USER === process.env.CONTACT_EMAIL,
      smtp_user_format_ok: /^[^@]+@[^@]+\.[^@]+$/.test(process.env.SMTP_USER || ''),
      port_is_587: process.env.SMTP_PORT === '587',
      port_is_465: process.env.SMTP_PORT === '465',
    },
  })
}
