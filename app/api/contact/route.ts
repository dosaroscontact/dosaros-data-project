import { NextRequest, NextResponse } from 'next/server'
import nodemailer from 'nodemailer'

/**
 * POST /api/contact — recibe el formulario y reenvía por email.
 *
 * Cascada de proveedores (primero que tenga credenciales gana):
 *  1. SMTP DonDominio (recomendado - dominio propio)
 *  2. Web3Forms (gratis, fallback)
 *  3. FormSubmit (último recurso)
 *
 * Env vars para SMTP DonDominio:
 *   SMTP_HOST  = mailsrv1.dondominio.com
 *   SMTP_PORT  = 587
 *   SMTP_USER  = contact@dosaros.com  (la dirección que envía)
 *   SMTP_PASS  = (contraseña del email)
 *   CONTACT_EMAIL = contact@dosaros.com  (destinatario)
 */
export async function POST(request: NextRequest) {
  try {
    const { nombre, email, mensaje } = await request.json()

    if (!nombre || !email || !mensaje) {
      return NextResponse.json({ error: 'Faltan campos requeridos' }, { status: 400 })
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    if (!emailRegex.test(email)) {
      return NextResponse.json({ error: 'Email inválido' }, { status: 400 })
    }

    // 1) Intentar SMTP (DonDominio o cualquier proveedor SMTP)
    if (process.env.SMTP_HOST && process.env.SMTP_USER && process.env.SMTP_PASS) {
      const smtpResult = await sendViaSMTP({ nombre, email, mensaje })
      if (smtpResult) return smtpResult
    }

    // 2) Fallback: Web3Forms
    if (process.env.WEB3FORMS_ACCESS_KEY) {
      const w3Result = await sendViaWeb3Forms({ nombre, email, mensaje })
      if (w3Result) return w3Result
    }

    // 3) Último recurso: FormSubmit
    return await sendViaFormSubmit({ nombre, email, mensaje })
  } catch (error) {
    console.error('Error en contact API:', error)
    return NextResponse.json({ error: 'Error al procesar la solicitud' }, { status: 500 })
  }
}

// ============================================================
// PROVEEDOR 1: SMTP (DonDominio / cualquier SMTP)
// ============================================================
async function sendViaSMTP({
  nombre,
  email,
  mensaje,
}: {
  nombre: string
  email: string
  mensaje: string
}): Promise<NextResponse | null> {
  try {
    const port = parseInt(process.env.SMTP_PORT || '587', 10)

    const transporter = nodemailer.createTransport({
      host: process.env.SMTP_HOST!,
      port,
      secure: port === 465, // SSL on 465, STARTTLS on 587
      auth: {
        user: process.env.SMTP_USER!,
        pass: process.env.SMTP_PASS!,
      },
    })

    const destEmail = process.env.CONTACT_EMAIL || process.env.SMTP_USER!

    // HTML body con branding DOS AROS
    const htmlBody = `
      <div style="font-family: 'Helvetica Neue', Arial, sans-serif; max-width: 600px; margin: 0 auto; background: #FFFFFF; color: #011E3B;">
        <div style="background: #011E3B; padding: 30px 40px;">
          <h1 style="color: #FF7D28; margin: 0; font-size: 28px; letter-spacing: -0.02em;">DOS AROS</h1>
          <p style="color: #E6E8EE; margin: 8px 0 0; font-size: 14px;">Nuevo mensaje desde dosaros.com</p>
        </div>

        <div style="padding: 40px;">
          <table style="width: 100%; border-collapse: collapse;">
            <tr>
              <td style="padding: 12px 0; border-bottom: 1px solid #E6E8EE; width: 120px;">
                <strong style="color: #B1005A; font-size: 12px; text-transform: uppercase; letter-spacing: 0.1em;">Nombre</strong>
              </td>
              <td style="padding: 12px 0; border-bottom: 1px solid #E6E8EE;">
                ${escapeHtml(nombre)}
              </td>
            </tr>
            <tr>
              <td style="padding: 12px 0; border-bottom: 1px solid #E6E8EE;">
                <strong style="color: #B1005A; font-size: 12px; text-transform: uppercase; letter-spacing: 0.1em;">Email</strong>
              </td>
              <td style="padding: 12px 0; border-bottom: 1px solid #E6E8EE;">
                <a href="mailto:${escapeHtml(email)}" style="color: #FF7D28; text-decoration: none;">${escapeHtml(email)}</a>
              </td>
            </tr>
            <tr>
              <td style="padding: 12px 0; vertical-align: top;">
                <strong style="color: #B1005A; font-size: 12px; text-transform: uppercase; letter-spacing: 0.1em;">Mensaje</strong>
              </td>
              <td style="padding: 12px 0; white-space: pre-wrap; line-height: 1.6;">
                ${escapeHtml(mensaje)}
              </td>
            </tr>
          </table>
        </div>

        <div style="background: #E6E8EE; padding: 20px 40px; font-size: 12px; color: #011E3B; opacity: 0.7;">
          Enviado desde el formulario de contacto · <a href="https://www.dosaros.com" style="color: #FF7D28;">dosaros.com</a>
        </div>
      </div>
    `

    await transporter.sendMail({
      from: `"DOS AROS Contact" <${process.env.SMTP_USER}>`,
      to: destEmail,
      replyTo: email,
      subject: `Nuevo mensaje DOS AROS — ${nombre}`,
      text: `Nombre: ${nombre}\nEmail: ${email}\n\nMensaje:\n${mensaje}`,
      html: htmlBody,
    })

    return NextResponse.json(
      { success: true, message: 'Mensaje enviado correctamente', via: 'smtp' },
      { status: 200 }
    )
  } catch (error) {
    console.error('SMTP error:', error)
    return null // Permite cascada al siguiente proveedor
  }
}

// ============================================================
// PROVEEDOR 2: Web3Forms
// ============================================================
async function sendViaWeb3Forms({
  nombre,
  email,
  mensaje,
}: {
  nombre: string
  email: string
  mensaje: string
}): Promise<NextResponse | null> {
  try {
    const response = await fetch('https://api.web3forms.com/submit', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify({
        access_key: process.env.WEB3FORMS_ACCESS_KEY,
        subject: `Nuevo mensaje DOS AROS — ${nombre}`,
        from_name: 'DOS AROS Contact Form',
        name: nombre,
        email,
        message: mensaje,
        botcheck: '',
      }),
    })

    if (response.ok) {
      const data = await response.json()
      if (data.success) {
        return NextResponse.json(
          { success: true, message: 'Mensaje enviado correctamente', via: 'web3forms' },
          { status: 200 }
        )
      }
    }
    console.error('Web3Forms error:', response.status)
    return null
  } catch (error) {
    console.error('Web3Forms exception:', error)
    return null
  }
}

// ============================================================
// PROVEEDOR 3: FormSubmit (último recurso)
// ============================================================
async function sendViaFormSubmit({
  nombre,
  email,
  mensaje,
}: {
  nombre: string
  email: string
  mensaje: string
}): Promise<NextResponse> {
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
        { success: true, message: 'Mensaje enviado correctamente', via: 'formsubmit' },
        { status: 200 }
      )
    }

    return NextResponse.json(
      {
        error:
          'No pudimos enviar el mensaje ahora mismo. Escríbenos directamente a dosaroscontact@gmail.com y te respondemos.',
      },
      { status: 500 }
    )
  } catch (error) {
    console.error('FormSubmit exception:', error)
    return NextResponse.json(
      {
        error:
          'No pudimos enviar el mensaje ahora mismo. Escríbenos directamente a dosaroscontact@gmail.com y te respondemos.',
      },
      { status: 500 }
    )
  }
}

// ============================================================
// Utility: escape HTML para prevenir XSS en el email
// ============================================================
function escapeHtml(text: string): string {
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;')
}
