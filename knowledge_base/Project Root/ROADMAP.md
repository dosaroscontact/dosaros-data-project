# 🗺️ ROADMAP

Plan futuro del proyecto DOS AROS.

---

## 🎯 Q2 2026 — Consolidación

### Knowledge Base
- [x] Migrar contenido a Obsidian (Fase 1)
- [ ] Implementar sincronización Obsidian → CLAUDE.md (Fase 2)
- [ ] Documentar workflow integrado (Fase 3)
- [ ] Crear plantillas (Templater) para nuevos análisis

### Frontend
- [ ] Implementar `/analisis` con datos reales (NBA + Euro)
- [ ] Implementar `/predicciones` con modelo ML básico
- [ ] Implementar `/comunidad` (foro/chat)
- [ ] Conectar Newsletter a BD
- [ ] Mejorar SEO (meta tags, OG images)

### Backend
- [ ] Reparar bug DeepSeek/Kimi en `api_manager.py`
- [ ] Tests automatizados para ETL críticos
- [ ] Sistema de alertas para fallos de cron

### Datos
- [ ] Completar carga histórica NBA 2018-2019
- [ ] Completar carga histórica EuroLeague E2010-E2021
- [ ] Implementar backups automáticos a Supabase

---

## 🚀 Q3 2026 — Expansión

### Visualizaciones
- [ ] Mapas de tiro NBA con coordenadas reales
- [ ] Mapas de tiro EuroLeague con normalización
- [ ] Comparativas head-to-head jugadores
- [ ] Dashboard de equipo personalizado

### Automatización
- [ ] Publicación automática a X/Twitter (no solo borrador)
- [ ] Stories automáticas a Instagram
- [ ] Newsletter semanal por email
- [ ] Bot de Discord (replicar Telegram)

### Avatar
- [ ] Generación automática diaria de stories
- [ ] Variantes por temporada/playoff
- [ ] Versiones de jugadores específicos

---

## 🌟 Q4 2026 — Producto Real

### Comercialización
- [ ] Sistema de pedidos integrado (productos físicos)
- [ ] Pasarela de pago (Stripe)
- [ ] Inventario y gestión de stock
- [ ] Logística y envíos

### Comunidad
- [ ] Sistema de cuentas (login)
- [ ] Notificaciones personalizadas
- [ ] Suscripciones premium (acceso a analytics avanzados)

### Mobile
- [ ] App React Native (iOS + Android)
- [ ] Push notifications
- [ ] Modo offline para datos críticos

---

## 🔬 2027+ — Investigación

### ML/AI
- [ ] Modelo predictivo de resultados
- [ ] Detección automática de patrones tácticos
- [ ] Análisis sentimental de comentarios sociales
- [ ] Generación automática de highlights

### Plataformas
- [ ] API pública para developers
- [ ] Integración con TV (resúmenes en vivo)
- [ ] Realidad aumentada para stats en pista

---

## 📊 Métricas de Éxito

### Corto Plazo (Q2-Q3 2026)
- 100% cobertura PBP NBA 2015-presente
- 100% cobertura PBP EuroLeague E2007-presente
- 50+ usuarios activos del bot Telegram
- 5+ productos vendidos del catálogo

### Mediano Plazo (Q4 2026)
- 500+ usuarios activos
- 100+ ventas/mes
- 1000+ followers en redes sociales
- App publicada en stores

### Largo Plazo (2027+)
- Referente español en análisis de baloncesto data-driven
- 5000+ usuarios activos
- Modelo de revenue sostenible
- Equipo de 2-3 colaboradores

---

## 🚫 Anti-Patterns (Lo que NO haremos)

- ❌ Especulación sin datos
- ❌ Clickbait
- ❌ Análisis emotivo
- ❌ Plataforma cerrada (todo abierto cuando posible)
- ❌ Dependencia de un solo proveedor (multi-LLM, multi-DB)
- ❌ Tecnología por moda (solo lo que añade valor real)

---

## 🔗 Referencias

- [[STATUS|📊 Estado actual]]
- [[CHANGELOG|📅 Histórico de cambios]]
- [[../Architecture/Decisions Log|📝 ADRs]]
