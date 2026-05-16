# Landing Page Architecture

**Date:** 2026-05-16  
**Status:** Design Phase  
**Owner:** DOS Aros Web Team

## Overview

Public-facing landing page for DOS Aros platform. Serves as:
1. Marketing hub (brand showcase, live data proof)
2. Conversion funnel (queries, newsletter, merchandise)
3. Gateway to detailed analysis (match stats, player data)

## Design Pillars

### Premium yet Accessible
- Dark blue base (`#0D1321`) = professional, trustworthy
- Magenta accent (`#B1005A`) = energy, standout
- Orange highlights (`#F28C28`) = attention to key data
- Gray neutrals (`#E6E8EE`) = breathing room

### Mobile-First Strategy
- **Breakpoints:** 375px (mobile) → 640px (tablet) → 1024px (desktop)
- **Touch targets:** ≥44×44px with 8px gaps
- **Typography:** 16px minimum body (no iOS auto-zoom)
- **No horizontal scroll:** All content vertical on mobile
- **Ticker adaptation:** Vertical card stack on mobile (vs. horizontal scroll desktop)

### Data-Driven, Not Overwhelming
- Show 3-4 featured matches (not all 20+)
- 3 latest highlights (not news dump)
- Query box as hero (demonstrates AI power)
- Merchandise/newsletter below-the-fold

## Microservice Architecture

```
┌─────────────────────────────┐
│   Next.js Landing (Vercel)  │
├─────────────────────────────┤
│ /api/live-scores            │ ← mock/real API swap
│ /api/upcoming               │ ← mock data
│ /api/events                 │ ← mock data
│ /api/query                  │ → Pi backend
└─────────────────────────────┘
         ↓
┌─────────────────────────────┐
│  Pi Backend (Python)        │
├─────────────────────────────┤
│ /api/query/nl→sql          │ ← NL query
│ → SQLite search            │
│ → AI fallback (Gemini...)  │
└─────────────────────────────┘
```

**Mock Data Pattern:**
- Files: `src/api/mock/live-scores.ts`, etc.
- Structure: Return `{ leagues: { nba: [...], euro: [...] } }`
- Swappable: When real API ready, only change fetch logic
- No schema changes needed

## Sections & Components

### 1. Hero
- Compact: Logo + tagline + CTA
- Desktop: Side-by-side
- Mobile: Stacked vertical

### 2. Live Scores Ticker
- **Leagues:** NBA, WNBA, EuroLeague (M+W), Liga ACB (M+W), FIBA
- **Desktop:** Horizontal smooth scroll (Framer Motion)
- **Mobile:** Vertical card stack with auto-scroll (5s per item)
- **Data:** Team crest + Score + Period + Update time
- **Interaction:** Click → match detail page

### 3. Upcoming Games
- Next 2-3 featured matches
- Date + Teams + Competition
- Link to future match detail

### 4. Latest Highlights
- 3 most recent events (e.g., playoff series status)
- Thumbnail + Headline + Summary
- Link to full article

### 5. AI Query Box
- Text input: "Ask about basketball..."
- POST → `/api/query`
- Return: Result + source (db/ai) + query_time
- UX: Modal or inline results

### 6. Merchandise
- "DOS AROS Shop" cards
- 2-3 featured items
- Link to full catalog

### 7. Newsletter
- Email signup
- CTA: "Weekly Perlas + Predictions"
- Confirmation email + welcome gift

### 8. Footer
- Social links (X, Instagram, TikTok)
- Legal (Privacy, Terms)
- Copyright

## Animation Strategy (Framer Motion)

| Element | Trigger | Duration | Easing | Purpose |
|---------|---------|----------|--------|---------|
| Ticker scroll | Page load | Continuous | Linear | Convey live data |
| Card fade-in | Viewport enter | 300ms | ease-out | Hierarchy |
| Hover feedback | Tap/hover | 150ms | ease-out | Interactivity |
| Loading spinner | Query submit | - | spring | User feedback |
| CTA pulse | Hero | 2s loop | ease-in-out | Conversion focus |

**Respect `prefers-reduced-motion`:** Disable all animations if user has set preference.

## Performance Budget

| Metric | Target | How |
|--------|--------|-----|
| FCP | < 2.5s | Inline critical CSS, lazy load images |
| LCP | < 4s | Optimize images (WebP), preload fonts |
| CLS | < 0.1 | Declare image dimensions, reserve space |
| TTI | < 3.5s | Code splitting, defer non-critical JS |

## Testing Checklist (Mobile-First)

- [ ] Responsive at 375px (iPhone SE), 768px (iPad), 1440px (desktop)
- [ ] Landscape orientation works
- [ ] Touch targets ≥44×44px, no mis-taps
- [ ] Ticker scroll smooth, no jank
- [ ] Query box returns result <2s
- [ ] Keyboard navigation works (Tab, Enter)
- [ ] Screen reader announces all links/buttons
- [ ] Dark mode contrast ≥4.5:1
- [ ] No layout shift during image load (CLS)
- [ ] Newsletter form works, email captured

## Links

- [[Landing Page Design]] — Visual design decisions
- [[Mobile-First Strategy]] — Responsive design deep-dive
- [[API Microservices]] — Backend architecture
- [[Newsletter Strategy]] — Growth & monetization
