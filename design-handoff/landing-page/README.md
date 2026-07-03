# Handoff: Landing Page — Shopify Horizon Theme

## Overview
A full-viewport landing page for the store. White background with animated black particle field, centered logo image, live EST clock, vertical nav links, and social icons. Designed to be implemented as a custom Shopify Liquid section replacing or augmenting the Horizon theme's home page.

## About the Design Files
The files in this bundle are **HTML design references** — high-fidelity prototypes showing the intended look, layout, and behavior. They are **not** production code to copy directly. The task is to recreate these designs as Shopify Liquid sections/snippets inside the existing Horizon theme, using Liquid templating, CSS, and vanilla JavaScript as the theme already does.

## Fidelity
**High-fidelity.** Colors, typography, spacing, and animations are final. Recreate pixel-accurately using the Horizon theme's existing CSS architecture (custom properties, `base.css` tokens, inline section styles).

---

## Screen: Home Landing Page

### Purpose
A single full-viewport splash screen. Acts as the store's entry point — brand image, nav, and social links centered on screen.

### Layout
- **Container:** `position: fixed; inset: 0; background: #ffffff; overflow: hidden;`
- **Canvas layer:** `position: absolute; inset: 0; width: 100%; height: 100%;` — sits behind all content, renders the particle field
- **Shooting-star accent:** `position: absolute; top: 48%; right: 15%; width: 80px; height: 1px;` — a subtle horizontal gradient line, `rotate(-5deg)`
- **Content column:** `position: absolute; inset: 0; display: flex; flex-direction: column; align-items: center; justify-content: center;`

### Components

#### 1. Logo / Brand Image
- **Position:** Top of content column, centered
- **Size:** `160px × 120px`
- **Fit:** `object-fit: contain` — no crop, transparent background (no box or border)
- **Animation:** Gentle vertical float
  ```css
  @keyframes float {
    0%, 100% { transform: translateY(0px); }
    50%       { transform: translateY(-8px); }
  }
  animation: float 4s ease-in-out infinite;
  ```
- **Implementation note:** Wire to a Shopify theme image setting (`settings.logo` or a dedicated section image setting) so the merchant can swap it in the theme editor.
- **Margin below:** `margin-bottom: 32px` (wraps image + clock together)

#### 2. Live EST Clock
- **Position:** Directly below the logo image, `gap: 6px`
- **Font:** `'Share Tech Mono', monospace` — load from Google Fonts
- **Size:** `9px`
- **Color:** `rgba(0, 0, 0, 0.45)`
- **Letter-spacing:** `0.08em`
- **Content:** Live ticking timestamp in EST, format: `MM/DD/YYYY H:MM:SS AM/PM EST`
- **JavaScript:**
  ```js
  function startClock(el) {
    function tick() {
      const now = new Date();
      const est = new Date(now.toLocaleString('en-US', { timeZone: 'America/New_York' }));
      const mm   = String(est.getMonth() + 1).padStart(2, '0');
      const dd   = String(est.getDate()).padStart(2, '0');
      const yyyy = est.getFullYear();
      let h      = est.getHours();
      const ampm = h >= 12 ? 'PM' : 'AM';
      h = h % 12 || 12;
      const min  = String(est.getMinutes()).padStart(2, '0');
      const sec  = String(est.getSeconds()).padStart(2, '0');
      el.textContent = `${mm}/${dd}/${yyyy} ${h}:${min}:${sec} ${ampm} EST`;
    }
    tick();
    setInterval(tick, 1000);
  }
  ```

#### 3. Navigation Links
- **Layout:** `display: flex; flex-direction: column; align-items: center; gap: 6px; margin-bottom: 48px;`
- **Font:** `'Bebas Neue', sans-serif` — load from Google Fonts
- **Size:** `13px`
- **Letter-spacing:** `0.18em`
- **Color:** `#000000`
- **Text transform:** already uppercase (use literal uppercase copy)
- **Border:** `1px solid rgba(0, 0, 0, 0.55)`
- **Padding:** `4px 20px 2px`
- **Min-width:** `110px`
- **Text-align:** `center`
- **Hover state:** `border-color: #000; background: rgba(0, 0, 0, 0.06);`
- **Animation (each link, staggered):**
  ```css
  @keyframes glowPulse {
    0%, 100% { text-shadow: 0 0 4px rgba(0,0,0,0.12); }
    50%       { text-shadow: 0 0 8px rgba(0,0,0,0.25); }
  }
  animation: glowPulse 3s ease-in-out infinite;
  /* Stagger: SHOP 0s, CONTACT 0.3s, RETURN POLICY 0.6s */
  ```

**Links (in order):**
| Label | Link target |
|---|---|
| SHOP | `/collections/all` |
| CONTACT | `/pages/contact` |
| RETURN POLICY | `/policies/refund-policy` |

**Coming Soon item (4th slot):**
- Same dimensions as nav links but **disabled** — not an `<a>` tag, use a `<span>` or `<div>`
- Color: `rgba(0, 0, 0, 0.3)`
- Border: `1px solid rgba(0, 0, 0, 0.2)`
- `cursor: default`
- Prepend an inline lock SVG icon (9×11px, stroke-only):
  ```html
  <svg width="9" height="11" viewBox="0 0 9 11" fill="none"
       stroke="currentColor" stroke-width="1.3"
       stroke-linecap="round" stroke-linejoin="round">
    <rect x="1" y="4.5" width="7" height="6" rx="1"></rect>
    <path d="M2.5 4.5V3a2 2 0 0 1 4 0v1.5"></path>
  </svg>
  ```
- Label text: `COMING SOON`

#### 4. Social Icons
- **Layout:** `display: flex; flex-direction: row; align-items: center; gap: 14px;`
- **Icon size:** `16×16px`
- **Color:** `rgba(0, 0, 0, 0.5)` at rest; `#000000` on hover
- **Platforms:** Instagram, YouTube only

**Instagram SVG** (stroke style, `stroke-width: 1.5`):
```html
<svg width="16" height="16" viewBox="0 0 24 24" fill="none"
     stroke="currentColor" stroke-width="1.5"
     stroke-linecap="round" stroke-linejoin="round">
  <rect x="2" y="2" width="20" height="20" rx="5" ry="5"></rect>
  <circle cx="12" cy="12" r="4"></circle>
  <circle cx="17.5" cy="6.5" r="1" fill="currentColor" stroke="none"></circle>
</svg>
```

**YouTube SVG** (filled):
```html
<svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
  <path d="M23.5 6.2s-.3-1.9-1.1-2.7c-1.1-1.1-2.3-1.1-2.8-1.2C16.8 2 12 2 12 2s-4.8 0-7.6.3c-.6.1-1.8.1-2.8 1.2C.8 4.3.5 6.2.5 6.2S.2 8.4.2 10.6v2.1c0 2.2.3 4.4.3 4.4s.3 1.9 1.1 2.7c1.1 1.1 2.5 1.1 3.1 1.2C6.7 21.1 12 21.1 12 21.1s4.8 0 7.6-.3c.6-.1 1.8-.1 2.8-1.2.8-.8 1.1-2.7 1.1-2.7s.3-2.2.3-4.4v-2.1c0-2.2-.3-4.4-.3-4.4zM9.7 15.5V8.4l7.6 3.6-7.6 3.5z"></path>
</svg>
```

- **Implementation note:** Wire href values to Shopify social link settings (`settings.social_instagram_link`, `settings.social_youtube_link`) so the merchant can update them in the theme editor.

---

## Interactions & Behavior

### Particle Field (Canvas)
Render 320 animated black dots on a `<canvas>` behind all content. Each particle has:

| Property | Value |
|---|---|
| Base radius | `0.3–1.7px` (random) |
| Base alpha | `0.1–0.65` (random) |
| Twinkle | `sin()` oscillation on alpha, speed `0.6–2.4 Hz` |
| Size pulse | Independent `sin()` on radius, speed `0.4–1.6 Hz` |
| Drift | Slow random XY drift, `±0.09px/frame` |
| Wrap | Particles that exit bounds re-enter opposite side |
| Burst flash | Every `7–17s` each particle briefly flares — alpha +0.6, radius ×2.2, with a tiny cross stroke |
| Accent color | 4% of particles render as `rgba(80,100,180,a)` instead of black |

Resize handler: re-initialize canvas on `window.resize`.

### Shooting-Star Accent
Static decorative element — no interaction. A `1px` horizontal line `width: 80px`, `background: linear-gradient(to right, rgba(0,0,0,0.4), transparent)`, positioned `top: 48%; right: 15%; transform: rotate(-5deg)`.

### Nav Link Hover
`transition: background 0.15s ease, border-color 0.15s ease;`

---

## Design Tokens

| Token | Value |
|---|---|
| Background | `#ffffff` |
| Foreground | `#000000` |
| Nav border (active) | `rgba(0,0,0,0.55)` |
| Nav border (disabled) | `rgba(0,0,0,0.20)` |
| Nav hover bg | `rgba(0,0,0,0.06)` |
| Icon default | `rgba(0,0,0,0.50)` |
| Clock color | `rgba(0,0,0,0.45)` |
| Disabled text | `rgba(0,0,0,0.30)` |
| Heading font | `'Bebas Neue'`, Google Fonts |
| Mono font | `'Share Tech Mono'`, Google Fonts |
| Nav font size | `13px` |
| Nav letter-spacing | `0.18em` |
| Clock font size | `9px` |
| Float animation | `4s ease-in-out infinite` |
| Glow pulse animation | `3s ease-in-out infinite` |

---

## Shopify Liquid Implementation Notes

1. **Create as a standalone section** (`sections/landing-page.liquid`) with its own `{% schema %}`. Add it to `templates/index.json` as the sole or primary section.
2. **Logo image:** Add a section setting of type `image_picker` so the merchant can set the brand image from the theme editor.
3. **Social links:** Read from `settings.social_instagram_link` and `settings.social_youtube_link` (global theme settings already present in Horizon). Hide the icon if the setting is blank.
4. **Nav links:** Hardcode or expose as section blocks (type: `link`) so the merchant can edit labels and URLs in the editor.
5. **Coming Soon slot:** Can be a section block with `type: coming_soon` that renders the locked pill. Or hardcode for now and remove when the feature goes live.
6. **Fonts:** Add `<link>` preconnects + stylesheet for `Bebas Neue` and `Share Tech Mono` inside the section's `{% style %}` or in `snippets/fonts.liquid`.
7. **Canvas JS:** Inline `<script>` at the bottom of the section file (scoped with a unique section ID) — Horizon sections already follow this pattern.
8. **Clock JS:** Same inline `<script>`, initialize on `DOMContentLoaded` or immediately after the element.
9. **No header/footer:** This page intentionally has no Horizon header or footer. If the template needs them removed, use a custom template JSON that omits the header-group and footer-group sections.

---

## Assets
- **Logo/brand image:** Supplied by the merchant — add via `image_picker` setting. Placeholder: 160×120px, `object-fit: contain`, transparent background.
- **Icons:** All inline SVG — no external icon files needed.
- **Fonts:** Google Fonts CDN — `Bebas Neue` (display/nav), `Share Tech Mono` (clock).

---

## Files in This Bundle
| File | Description |
|---|---|
| `Landing Page.dc.html` | High-fidelity HTML prototype — reference for all visual specs |
| `README.md` | This document |
