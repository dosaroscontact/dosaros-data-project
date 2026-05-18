# 📨 Contact Form — Setup y Troubleshooting

**Endpoint**: `/api/contact` (Next.js Route Handler)
**Componente**: `components/ContactForm.tsx`

---

## 🎯 Arquitectura

```
Usuario rellena form
      ↓
POST /api/contact  (route.ts)
      ↓
Web3Forms (PRIMARIO) ← gratis, fiable
      ↓
Si falla: FormSubmit.co (FALLBACK)
      ↓
Si falla: error UI con fallback email manual
      ↓
✉️ dosaroscontact@gmail.com
```

---

## 🔧 Configurar Web3Forms (Recomendado — 3 min)

Web3Forms es más fiable que FormSubmit y tiene 250 envíos/mes gratis.

### Paso 1 — Crear cuenta

1. 👉 https://web3forms.com
2. Click **"Get Started Free"** o **"Create Access Key"**
3. Introduce tu email: `dosaroscontact@gmail.com`
4. Confirma el email (te llega un access key)

### Paso 2 — Copiar el Access Key

Te darán un código tipo: `abc12345-def6-7890-ghij-klmn0pqrstuv`

### Paso 3 — Añadir como env var en Vercel

1. 👉 https://vercel.com/dashboard
2. Click en tu proyecto `dosaros-data-project`
3. **Settings → Environment Variables**
4. **Add New**:
   - **Key**: `WEB3FORMS_ACCESS_KEY`
   - **Value**: (pega tu access key)
   - **Environments**: marcar `Production`, `Preview`, `Development`
5. **Save**

### Paso 4 — Redeploy

Vercel necesita re-desplegar para usar la nueva env var:

1. **Deployments** (menú izquierda)
2. Último deployment → **...** (tres puntos) → **Redeploy**
3. Esperar ~2 min

### Paso 5 — Verificar

```bash
curl -X POST "https://www.dosaros.com/api/contact" \
  -H "Content-Type: application/json" \
  -d '{"nombre":"Test","email":"test@example.com","mensaje":"Hola"}'
```

Esperado: `{"success":true,...}`

---

## 🔄 Fallback Automático

Si Web3Forms falla (o no está configurado), el endpoint intenta FormSubmit.co automáticamente.

Si AMBOS fallan, el usuario ve:
> "No pudimos enviar el mensaje ahora mismo. Escríbenos directamente a dosaroscontact@gmail.com y te respondemos."

Esto evita que pierdas leads aunque haya outages.

---

## 🚨 Troubleshooting

### Error: "Error al enviar el mensaje"

**Causa más común**: Web3Forms access key no configurado en Vercel.

**Solución**:
1. Verificar `WEB3FORMS_ACCESS_KEY` existe en Vercel env vars
2. Verificar que está en environment `Production`
3. Hacer redeploy si acabas de añadirlo

### Error 522 desde FormSubmit

FormSubmit.co tiene caídas frecuentes (Cloudflare 522). Por eso usamos Web3Forms como primario.

### Email no llega a la bandeja

1. Revisar carpeta **Spam**
2. Verificar que activaste el email en el proveedor (Web3Forms te envía un confirmation email la primera vez)
3. Ver logs en Vercel: `Deployments → [last] → Functions → /api/contact`

### Form se quedaba colgado

Antes del fix de 2026-05-18, FormSubmit caído provocaba que el form mostrara error genérico.

Ahora el fallback es:
- Web3Forms → FormSubmit → error UI con email manual

---

## 📋 Datos del Form

Campos enviados al destinatario:

| Campo | Valor enviado |
|-------|---------------|
| Subject | `Nuevo mensaje DOS AROS — [nombre]` |
| Name | nombre del visitante |
| Email | email del visitante |
| Message | mensaje |
| Origen | `from DOS AROS Contact Form` |

### Pre-fill por URL

Si el usuario viene de `/productos`, el form pre-rellena el mensaje:
```
Hola, me interesa: Camiseta Hombre Crema.
¿Cuáles son las opciones disponibles (talla, stock) y el precio? Gracias.
```

Esto se trackea en GA4 como `form_submitted` con `source_product` parameter.

---

## 🔗 Referencias

- Código: `app/api/contact/route.ts`
- Component: `components/ContactForm.tsx`
- Web3Forms docs: https://docs.web3forms.com
- FormSubmit docs: https://formsubmit.co
- [[Analytics Tracking Plan|📊 Tracking eventos]]
