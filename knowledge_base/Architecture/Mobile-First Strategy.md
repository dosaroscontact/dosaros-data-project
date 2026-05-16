# Mobile-First Strategy

**Date:** 2026-05-16  
**Scope:** DOS Aros Landing Page  
**Priority:** CRITICAL

---

## Why Mobile-First?

**Market Reality:**
- 68% of web traffic is mobile (2026)
- DOS Aros audience: Young, sports-savvy, mobile-first behavior
- Search engines prioritize mobile performance (Core Web Vitals)

**UX Truth:**
- Designing desktop-first → mobile is painful
- Designing mobile-first → scale to desktop is natural
- Mobile has constraints that force clarity (no room for fluff)

---

## Breakpoints

```
Mobile      Tablet      Desktop
375px       768px       1440px
─────────────────────────────
narrow      medium      wide
touch       touch/      mouse
primary     mouse       secondary
```

**Why these numbers?**
- **375px:** iPhone SE (smallest common phone)
- **768px:** iPad portrait
- **1440px:** Common desktop resolution

---

## Mobile Layout — Section by Section

### 1. Hero
**Desktop Layout:**
```
[Logo] | Headline        
       | Subheading      
       | [CTA Button]    
```

**Mobile Layout:**
```
[Logo - small]

Headline
(2 lines max)

Subheading

[CTA Button - full width]
```

**CSS:**
```css
@media (max-width: 640px) {
  .hero {
    flex-direction: column;
    padding: 16px;
  }
  .cta-button {
    width: 100%;
  }
}
```

---

### 2. Live Scores Ticker

**Desktop:** Horizontal smooth scroll
```
[LAL 98-102 BOS Q3] [GSW 110-105 LAC Q4] [...→
```

**Mobile:** Vertical card stack (auto-scroll)
```
┌─────────────────┐
│ LAL             │
│ 98 - 102        │
│ BOS             │
│ Q3, 4:23 left   │
└─────────────────┘
↓
┌─────────────────┐
│ GSW             │
│ 110 - 105       │
│ LAC             │
│ Q4, 2:10 left   │
└─────────────────┘
```

**Why vertical on mobile?**
- No horizontal scroll (confusing on mobile)
- Full viewport width = readable scores
- Auto-scroll = feels live/dynamic
- Tap = expand to details

**CSS:**
```css
@media (max-width: 768px) {
  .ticker {
    flex-direction: column;
    gap: 12px;
    max-height: 60vh;
    overflow-y: auto;
  }
}
```

---

### 3. Query Box

**Desktop:** Inline with hero or prominent card
```
┌─────────────────────────────────┐
│ Ask about basketball...          │
│ ┌─────────────────────────────┐ │
│ │ [Text input here]         [🔍] │
│ └─────────────────────────────┘ │
└─────────────────────────────────┘
```

**Mobile:** Full-width, possibly sticky bottom
```
┌──────────────────────────┐
│ Ask about basketball...   │
│ ┌──────────────────────┐ │
│ │ [Input]           [🔍]│
│ └──────────────────────┘ │
└──────────────────────────┘ (sticky on scroll)
```

**Considerations:**
- Button ≥44px height (touch target)
- Placeholder text readable (16px+)
- No keyboard covers input (test on real devices)

---

### 4. Typography

**Mobile Sizes:**
- **H1 (Headline):** 24-28px (Space Grotesk, 600)
- **H2 (Subheading):** 18-20px (Space Grotesk, 500)
- **Body:** 16px (Inter, 400) — NO SMALLER
- **Caption:** 14px (Inter, 400)

**Why 16px minimum?**
- Avoids iOS auto-zoom on input focus
- Readable without zoom
- Accessibility standard

**Line height:**
- Body: 1.5 (24px leading)
- Headings: 1.2 (28px for 24px headline)

---

### 5. Spacing

**4/8px System:**
```
Margins:   4px, 8px, 12px, 16px, 24px, 32px, 48px
           ↑    ↑    ↑     ↑     ↑     ↑     ↑
           1x   2x   3x    4x    6x    8x    12x
```

**Mobile Spacing:**
- Section padding: 16px (not 24px like desktop)
- Component gaps: 8-12px (not 16px)
- Card padding: 12px (not 16px)

**Example:**
```css
/* Desktop */
@media (min-width: 1024px) {
  .section { padding: 48px; }
  .card { gap: 16px; }
}

/* Mobile */
@media (max-width: 640px) {
  .section { padding: 16px; }
  .card { gap: 8px; }
}
```

---

### 6. Touch Targets

**Minimum Size:**
- iOS: 44×44px
- Android: 48×48dp
- Desktop: 40×40px (ok, but larger is better)

**Spacing Between:**
- Minimum 8px gap (no accidental mis-taps)

**Example Button:**
```css
.button {
  min-height: 44px;
  min-width: 44px;
  padding: 12px 16px; /* ensures 44px height */
  border-radius: 8px;
}

.button + .button {
  margin-left: 8px; /* 8px gap between buttons */
}
```

**Expanding Hit Areas:**
- If icon is small (20px), use `hitSlop` (React Native) or padding (Web)
- Visible size ≠ Touch size

```css
/* Icon button: visible 24px, but tap area 44px */
.icon-button {
  width: 24px;
  height: 24px;
  padding: 10px; /* expands tap area to 44×44 */
}
```

---

### 7. Images

**Optimization:**
1. Use WebP (fallback PNG for older browsers)
2. Responsive images (`srcset`, `sizes`)
3. Lazy loading (`loading="lazy"`)
4. Declare dimensions (prevent CLS)

**Example:**
```html
<img 
  src="match.webp" 
  alt="Lakers vs Celtics live score"
  width="800"
  height="600"
  loading="lazy"
/>
```

**Mobile vs Desktop:**
- Mobile: 320px wide images
- Tablet: 640px wide
- Desktop: 1200px wide

---

### 8. Animations

**Respect `prefers-reduced-motion`:**
```css
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

**Mobile Animation Budget:**
- Keep animations <150ms (snappy)
- Disable on low-end devices (detect via `-webkit-` prefixes)
- Use `transform` only (GPU accelerated), not `width`/`height`

---

### 9. Keyboard & Accessibility

**Keyboard Navigation:**
- Tab order matches visual order
- Focus visible (2-4px ring, high contrast)
- Enter activates buttons/links

```css
button:focus {
  outline: 3px solid #B1005A; /* magenta focus ring */
  outline-offset: 2px;
}
```

**Screen Reader Labels:**
- All images have `alt` text
- Icon buttons have `aria-label`
- Form inputs have visible `<label>`

```html
<label for="email">Email:</label>
<input id="email" type="email" required />

<button aria-label="Search">🔍</button>
```

---

## Testing Checklist

**Real Devices:**
- [ ] iPhone SE (375px) in portrait
- [ ] iPhone 14 (390px) in portrait + landscape
- [ ] iPad (768px) in portrait + landscape
- [ ] Pixel 6 (412px) Android

**Emulation:**
- [ ] Chrome DevTools: 375px, 768px, 1440px
- [ ] Test with network throttling (4G)
- [ ] Test with `prefers-reduced-motion: reduce`

**Interaction:**
- [ ] Touch targets don't overlap (no mis-taps)
- [ ] Keyboard Tab works, focus visible
- [ ] Scroll smooth, no jank
- [ ] Form input doesn't get hidden by keyboard

**Performance:**
- [ ] Images load without CLS
- [ ] FCP < 2.5s on 4G
- [ ] LCP < 4s on 4G

---

## Links

- [[Landing Page Architecture]] — Overall design
- [[Design System (DOS Aros)]] — Colors, typography, components
