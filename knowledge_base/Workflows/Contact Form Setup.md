# 📨 Contact Form — Setup y Troubleshooting

**Endpoint**: `/api/contact` (Next.js Route Handler)
**Componente**: `components/ContactForm.tsx`

---

## 🎯 Arquitectura (Cascade de Proveedores)

```
Usuario rellena form
      ↓
POST /api/contact
      ↓
1️⃣ SMTP DonDominio  (recomendado, dominio propio)
      ↓ falla
2️⃣ Web3Forms        (gratis, fallback)
      ↓ falla
3️⃣ FormSubmit       (último recurso)
      ↓ falla
🆘 Error UI con email manual: dosaroscontact@gmail.com
```

El sistema usa el primero que tenga credenciales válidas.

---

## ⭐ Setup Recomendado: SMTP DonDominio

**Ventajas vs servicios externos**:
- ✅ Usa tu dominio propio (`contact@dosaros.com`)
- ✅ Sin límites de mensajes
- ✅ Sin dependencia de terceros
- ✅ Ya está pagado (incluido con DonDominio)
- ✅ Más profesional ("from contact@dosaros.com" vs "from form@web3forms.com")

### Paso 1 — Crear/Verificar email en DonDominio

1. 👉 https://www.dondominio.com/panel/
2. Login → **Mis dominios** → `dosaros.com`
3. **Correo** o **Email** en el menú lateral
4. Verificar que existe `contact@dosaros.com` (o crearlo)
5. **Copiar la contraseña** (la necesitarás en Vercel)

⚠️ Si no recuerdas la contraseña, puedes resetearla desde el panel de DonDominio.

### Paso 2 — Datos SMTP de DonDominio

| Campo | Valor |
|-------|-------|
| **Servidor SMTP** | `mailsrv1.dondominio.com` |
| **Puerto** | `587` (STARTTLS) |
| **Usuario** | `contact@dosaros.com` |
| **Contraseña** | la del email |
| **Seguridad** | STARTTLS |

Alternativa con SSL: puerto `465` (más legacy)

### Paso 3 — Añadir env vars en Vercel

👉 https://vercel.com/dashboard → tu proyecto → **Settings → Environment Variables**

Añade estas **5 variables**:

| Key | Value | Environments |
|-----|-------|--------------|
| `SMTP_HOST` | `mailsrv1.dondominio.com` | Production, Preview, Development |
| `SMTP_PORT` | `587` | Production, Preview, Development |
| `SMTP_USER` | `contact@dosaros.com` | Production, Preview, Development |
| `SMTP_PASS` | (tu contraseña) | Production (solo, por seguridad) |
| `CONTACT_EMAIL` | `contact@dosaros.com` | Production, Preview, Development |

⚠️ `SMTP_PASS` **solo en Production** para que no se exponga en preview deployments.

### Paso 4 — Redeploy

1. Vercel → **Deployments**
2. Último deployment → **...** → **Redeploy**
3. Esperar ~2 min

### Paso 5 — Verificar

Visita https://www.dosaros.com/contact en incógnito, rellena el form, envía.

Deberías recibir el email en `contact@dosaros.com` con formato bonito:

```
┌─────────────────────────────────────────┐
│ DOS AROS                                │
│ Nuevo mensaje desde dosaros.com         │
├─────────────────────────────────────────┤
│ NOMBRE   │ Test User                    │
│ EMAIL    │ test@example.com             │
│ MENSAJE  │ Hola, me interesa...         │
├─────────────────────────────────────────┤
│ dosaros.com                             │
└─────────────────────────────────────────┘
```

---

## 🧪 Test Local (sin Vercel)

Para probar SMTP en local antes de subir:

1. Crea archivo `.env.local` en raíz del proyecto:

```
SMTP_HOST=mailsrv1.dondominio.com
SMTP_PORT=587
SMTP_USER=contact@dosaros.com
SMTP_PASS=tu-contraseña-aqui
CONTACT_EMAIL=contact@dosaros.com
```

2. `npm run dev`
3. Visita `http://localhost:3000/contact` y prueba

⚠️ `.env.local` está en `.gitignore` (NO se sube a GitHub). Si lo creas, no lo commitees nunca.

---

## 🔧 Fallbacks Configurados

### Web3Forms (opcional, 250 envíos/mes)
- Var: `WEB3FORMS_ACCESS_KEY`
- Setup: https://web3forms.com
- Usado si SMTP no está configurado o falla

### FormSubmit (último recurso)
- Sin configuración necesaria
- Va a `dosaroscontact@gmail.com` (gmail personal)
- A veces caído (522), no fiable para producción

---

## 🚨 Troubleshooting

### Email no llega tras configurar SMTP

1. **Revisar carpeta spam** del destinatario
2. **Revisar logs Vercel**: Deployments → último → Functions → `/api/contact`
3. **Confirmar credenciales SMTP** son correctas
4. **Verificar email account activa** en DonDominio

### Error "Invalid login"

- Contraseña incorrecta o expirada
- Verifica copy-paste sin espacios
- DonDominio puede requerir "contraseñas de aplicación" si tienes 2FA

### Error "Connection timeout"

- Puerto bloqueado por Vercel (raro, suelen permitir 587/465)
- Probar puerto alternativo: cambiar `SMTP_PORT` a `465`

### Email llega pero como spam

- DonDominio incluye SPF en los DNS (ya lo vimos: `v=spf1 include:spf.dondominio.com`)
- Verificar que SPF está activo en DonDominio
- Considerar añadir DKIM (más config en DonDominio)

---

## 📋 Datos del Email Enviado

| Campo | Contenido |
|-------|-----------|
| **From** | `"DOS AROS Contact" <contact@dosaros.com>` |
| **To** | `contact@dosaros.com` (o CONTACT_EMAIL) |
| **Reply-To** | email del visitante (para responder directo) |
| **Subject** | `Nuevo mensaje DOS AROS — [nombre]` |
| **Body** | HTML branded con paleta DOS AROS + texto plano |

### Body HTML incluye

- Header con logo "DOS AROS" naranja sobre azul
- Tabla con: Nombre, Email (clickeable), Mensaje
- Footer con link a dosaros.com
- Branding completo

---

## 🔒 Seguridad

- ✅ HTML escapado para prevenir XSS
- ✅ Validación de email
- ✅ Campos requeridos verificados
- ✅ `SMTP_PASS` solo en Production (no en preview/dev)
- ✅ Reply-To = email visitante (permite responder sin exponer remitente)

---

## 🔗 Referencias

- Código: `app/api/contact/route.ts`
- Component: `components/ContactForm.tsx`
- DonDominio SMTP: https://www.dondominio.com/help/es/article/2/cliente-correo-pop3-imap-smtp/
- Nodemailer docs: https://nodemailer.com
- [[Analytics Tracking Plan|📊 Tracking eventos]]
