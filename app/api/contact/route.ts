import { NextRequest, NextResponse } from 'next/server'

/**
 * POST /api/contact — recibe el formulario de contacto y reenvía via email.
 *
 * Proveedor: Web3Forms (gratis, 250 envíos/mes, sin backend)
 * Setup: https://web3forms.com → crea cuenta → copia Access Key →
 *        en Vercel añade env var WEB3FORMS_ACCESS_KEY
 *
 * Fallback: si Web3Forms falla, intenta FormSubmit.co
 */
export async function POST(request: NextRequest) {
  try {
    const { nombre, email, mensaje } = await request.json()

    // Validación básica
    if (!nombre || !email || !mensaje) {
      return NextResponse.json({ error: 'Faltan campos requeridos' }, { status: 400 })
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    if (!emailRegex.test(email)) {
      return NextResponse.json({ error: 'Email inválido' }, { status: 400 })
    }

    const accessKey = process.env.WEB3FORMS_ACCESS_KEY

    // Si no hay access key configurada, fallback a FormSubmit
    if (!accessKey) {
      return await sendViaFormSubmit({ nombre, email, mensaje })
    }

    // Intento principal: Web3Forms
    const w3Response = await fetch('https://api.web3forms.com/submit', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Accept: 'application/json',
      },
      body: JSON.stringify({
        access_key: accessKey,
        subject: `Nuevo mensaje DOS AROS — ${nombre}`,
        from_name: 'DOS AROS Contact Form',
        name: nombre,
        email,
        message: mensaje,
        botcheck: '', // honeypot anti-spam
      }),
    })

    if (w3Response.ok) {
      const data = await w3Response.json()
      if (data.success) {
        return NextResponse.json(
          { success: true, message: 'Mensaje enviado correctamente' },
          { status: 200 }
        )
      }
    }

    // Fallback a FormSubmit
    console.warn('Web3Forms falló, intentando FormSubmit fallback')
    return await sendViaFormSubmit({ nombre, email, mensaje })
  } catch (error) {
    console.error('Error en contact API:', error)
    return NextResponse.json({ error: 'Error al procesar la solicitud' }, { status: 500 })
  }
}

/**
 * Fallback: enviar via FormSubmit.co cuando Web3Forms no está configurado o falla.
 */
async function sendViaFormSubmit({
  nombre,
  email,
  mensaje,
}: {
  nombre: string
  email: string
  mensaje: string
}) {
  try {
    const destEmail = process.env.CONTACT_EMAIL || 'dosaroscontact@gmail.com'

    const formData = new FormData()
    formData.append('name', nombre)
    formData.append('email', email)
    formData.append('message', mensaje)
    formData.append('_subject', `Nuevo mensaje DOS AROS — ${nombre}`)
    formData.append('_captcha', 'false')
    formData.append('_template', 'table')

    const response = await fetch(`https://formsubmit.co/ajax/${destEmail}`, {
      method: 'POST',
      headers: { Accept: 'application/json' },
      body: formData,
    })

    if (response.ok) {
      return NextResponse.json(
        { success: true, message: 'Mensaje enviado correctamente' },
        { status: 200 }
      )
    }

    const text = await response.text()
    console.error('FormSubmit fallback error:', response.status, text.slice(0, 200))
    return NextResponse.json(
      {
        error:
          'No pudimos enviar el mensaje ahora mismo. Escríbenos directamente a dosaroscontact@gmail.com y te respondemos.',
      },
      { status: 500 }
    )
  } catch (error) {
    console.error('FormSubmit fallback exception:', error)
    return NextResponse.json(
      {
        error:
          'No pudimos enviar el mensaje ahora mismo. Escríbenos directamente a dosaroscontact@gmail.com y te respondemos.',
      },
      { status: 500 }
    )
  }
}
