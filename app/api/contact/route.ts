import { NextRequest, NextResponse } from 'next/server'

export async function POST(request: NextRequest) {
  try {
    const { nombre, email, mensaje } = await request.json()

    // Validación básica
    if (!nombre || !email || !mensaje) {
      return NextResponse.json(
        { error: 'Faltan campos requeridos' },
        { status: 400 }
      )
    }

    // Validar formato de email
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    if (!emailRegex.test(email)) {
      return NextResponse.json(
        { error: 'Email inválido' },
        { status: 400 }
      )
    }

    // Usar FormSubmit.co para enviar el email (servicio gratuito)
    const formData = new FormData()
    formData.append('name', nombre)
    formData.append('email', email)
    formData.append('message', mensaje)
    formData.append('_subject', 'Nuevo mensaje desde DOS AROS')
    formData.append('_captcha', 'false')
    formData.append('_next', 'https://dosaros.vercel.app')

    const response = await fetch('https://formsubmit.co/contact@dosaros.com', {
      method: 'POST',
      body: formData,
    })

    if (response.ok) {
      return NextResponse.json(
        { success: true, message: 'Mensaje enviado correctamente' },
        { status: 200 }
      )
    } else {
      return NextResponse.json(
        { error: 'Error al enviar el mensaje' },
        { status: 500 }
      )
    }
  } catch (error) {
    console.error('Error en contact API:', error)
    return NextResponse.json(
      { error: 'Error al procesar la solicitud' },
      { status: 500 }
    )
  }
}
