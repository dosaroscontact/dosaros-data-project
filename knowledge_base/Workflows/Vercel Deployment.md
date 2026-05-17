# 🚀 Vercel Deployment — Guía Completa

**Objetivo**: Publicar DOS AROS frontend en `dosaros.com` usando Vercel + DonDominio.

---

## 🎯 Arquitectura del Deploy

```
┌──────────────────────────────────────────────────────┐
│  GitHub (main)                                       │
│  github.com/dosaroscontact/dosaros-data-project     │
└────────────────────┬─────────────────────────────────┘
                     │ webhook on push
                     ↓
┌──────────────────────────────────────────────────────┐
│  Vercel                                              │
│  - Detecta push                                      │
│  - npm install --legacy-peer-deps                    │
│  - npm run build                                     │
│  - Deploy a CDN global                               │
└────────────────────┬─────────────────────────────────┘
                     │ DNS
                     ↓
┌──────────────────────────────────────────────────────┐
│  dosaros.com (DonDominio)                            │
│  A:    @ → 76.76.21.21                              │
│  CNAME: www → cname.vercel-dns.com                  │
└──────────────────────────────────────────────────────┘
```

---

## 📋 PASO 1 — Vercel: Conectar GitHub

### 1.1 Crear cuenta
1. https://vercel.com/signup
2. **Continue with GitHub** (login con `dosaroscontact`)
3. Aceptar permisos

### 1.2 Importar proyecto
1. Dashboard → **Add New... → Project**
2. Buscar `dosaros-data-project` → **Import**
3. Configuración:
   - **Framework Preset**: Next.js (auto-detectado)
   - **Root Directory**: `.`
   - **Build Command**: `npm run build` (default)
   - **Output Directory**: `.next` (default)
   - **Install Command**: `npm install --legacy-peer-deps` ⚠️ **IMPORTANTE** (React 19 + lucide-react peer deps)

### 1.3 Variables de Entorno
Por ahora ninguna. Si en el futuro se añaden, se configuran en:
**Settings → Environment Variables**

### 1.4 Deploy inicial
1. Click **Deploy**
2. Esperar 2-3 minutos
3. URL temporal: `dosaros-data-project.vercel.app`
4. Verificar que carga

---

## 🌐 PASO 2 — Vercel: Añadir dominio

1. Proyecto → **Settings** → **Domains**
2. Añadir `dosaros.com` → **Add**
3. Añadir `www.dosaros.com` (Vercel hará redirect automático)
4. Vercel mostrará los registros DNS necesarios

---

## 🟡 PASO 3 — DonDominio: Configurar DNS

### 3.1 Acceso
1. https://www.dondominio.com/panel/
2. **Mis dominios** → `dosaros.com`
3. Pestaña **Zona DNS**

### 3.2 Eliminar registros antiguos
- Borrar registros **A** previos (apuntando a otra IP)
- Borrar **CNAME** previo de `www`

### 3.3 Añadir registros Vercel

| Tipo | Nombre | Valor | TTL |
|------|--------|-------|-----|
| **A** | `@` (o vacío) | `76.76.21.21` | 3600 |
| **CNAME** | `www` | `cname.vercel-dns.com` | 3600 |

### 3.4 Propagación
- **15 min - 4 horas** habitual (hasta 24h máximo)
- Verificar en https://dnschecker.org/

---

## 🔒 PASO 4 — SSL automático

Cuando DNS propague:
1. Vercel detecta automáticamente
2. Emite certificado SSL Let's Encrypt (gratis)
3. `https://dosaros.com` activo

---

## 🔄 PASO 5 — Auto-deploy continuo

Cada `git push origin main` dispara:
1. Vercel detecta push (webhook)
2. Build automático (~2 min)
3. Deploy a producción

**Branches preview**: Cada PR genera URL preview única `dosaros-data-project-git-feature.vercel.app`.

---

## 📊 PASO 6 — Verificar GTM en producción

1. https://tagassistant.google.com/
2. **Add domain** → `https://dosaros.com`
3. Confirmar detección de `GTM-MWDXWXZN`
4. Verificar en Google Analytics tiempo real

---

## ✅ Checklist Pre-Deploy

- [x] `.gitignore` correcto (`node_modules/`, `.next/`, `.env`)
- [x] `package.json` con `next build`
- [x] Imágenes en `/public/` < 100MB
- [x] Variables sensibles NO commiteadas
- [x] GTM ID configurado (`GTM-MWDXWXZN`)
- [x] `next.config.ts` sin configs que rompan producción
- [x] Build local funciona (`npm run build` → OK)

---

## 💰 Costes

| Servicio | Plan | Coste |
|----------|------|-------|
| **Vercel** | Hobby | 0€/mes |
| **Dominio** | DonDominio | ya pagado (anual) |
| **SSL** | Let's Encrypt | 0€ |
| **GTM** | Google | 0€ |

**Total mensual**: 0€

### Límites Vercel Hobby
- 100 GB bandwidth/mes (suficiente para empezar)
- Builds ilimitados
- Funciones serverless: 100GB-hours/mes
- Soporte: comunidad

---

## 🚨 Troubleshooting

### Build falla con peer dep conflict
- **Causa**: React 19 vs `lucide-react@0.344` peer deps
- **Solución**: Install Command = `npm install --legacy-peer-deps`

### Domain not verified
- **Causa**: DNS aún no propagado
- **Solución**: Esperar 1-2h, refrescar Vercel

### 404 tras deploy
- **Causa**: Project importado desde subcarpeta incorrecta
- **Solución**: Settings → General → Root Directory = `.`

### Cambios no se reflejan
- **Causa**: Cache CDN
- **Solución**: Deployments → ... → Redeploy → Clear cache

### GTM no se detecta
- **Causa**: Script bloqueado por adblocker
- **Solución**: Verificar en modo incógnito sin extensiones

---

## 🔗 Recursos

- Vercel Docs: https://vercel.com/docs
- DonDominio DNS: https://www.dondominio.com/help/es/category/76/zona-dns
- Next.js on Vercel: https://nextjs.org/docs/deployment

---

## 📝 Estado del Deploy

**Último deploy**: Pendiente (esperando primer push a Vercel)
**URL producción**: `https://dosaros.com` (cuando DNS esté configurado)
**URL Vercel**: `dosaros-data-project.vercel.app` (después de import)

---

**Ver también**:
- [[../Project Root/STATUS|📊 STATUS]]
- [[../Architecture/Decisions Log|📝 ADRs]]
- [[Sync Obsidian to Claude|🔁 Workflow de sync]]
