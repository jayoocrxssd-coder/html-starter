# CRXSSWEI — Horizon Theme (Landing Page Build)

This package is the **Horizon** theme export (`crxsswei.myshopify.com`) with the
custom landing-page design from `design-handoff/landing-page/` implemented as a
native Shopify Liquid section. It is ready to upload as-is.

## What changed vs. the raw theme export

1. **`sections/landing-page.liquid`** (new) — the full-viewport splash screen:
   animated particle-field canvas, floating logo, live EST clock, glowing nav
   pills, a disabled "Coming Soon" slot, and Instagram/YouTube icons. Built
   pixel-accurate to `design-handoff/landing-page/README.md` using Horizon's
   own conventions (`{% stylesheet %}`, section-scoped script, `image_picker`,
   block-based nav links).
2. **`layout/landing.liquid`** (new) — a header/footer-free layout (same
   pattern Horizon already uses for `layout/password.liquid`). It still
   includes `content_for_header`, so theme/app-embed blocks (chat widget,
   preloader, confetti, etc.) keep working.
3. **`templates/index.json`** (replaced) — the homepage now renders only the
   `landing-page` section on the `landing` layout, so visitors land on the
   splash screen with no header/footer.
4. **`templates/page.shop.json`** (new) — your **original** homepage content
   (Hero + Featured Collection + Marquee) was moved here, unchanged, so
   nothing was lost. The landing page's **SHOP** nav pill links to
   `/pages/shop`, which uses this template.

## One manual step required in Shopify admin

Shopify page templates must be attached to an actual **Page** — that can't be
done from a theme file alone. After uploading the theme:

1. Go to **Online Store → Pages → Add page**.
2. Title it `Shop` (this also sets its URL to `/pages/shop`, matching the
   nav link already wired up).
3. In the **Theme template** dropdown on the right, choose **`page.shop`**.
4. Save.

That's the only manual step. Everything else — nav links, social icons,
Contact page, Return Policy — points at URLs/templates that already exist in
this theme (`page.contact`, `/policies/refund-policy`).

## After uploading

- **Set the logo image**: Customize the theme → the `Landing page` section →
  set the **Logo image**. Until you do, the section falls back to your store
  name as text so nothing looks broken.
- **Social links**: already pre-filled with the Instagram/YouTube URLs found
  in your footer settings. Editable from the same section in the theme
  editor if they ever change.
- **Nav links**: editable as blocks on the `Landing page` section (label,
  URL, and glow-animation delay per link) — no code changes needed.

## Validation performed

- Every `{% schema %}` block in the theme (136 total) parses as valid JSON.
- `templates/index.json` and `templates/page.shop.json` are strict, valid
  JSON.
- All Liquid snippets referenced by `layout/landing.liquid`
  (`meta-tags`, `stylesheets`, `fonts`, `scripts`, `theme-styles-variables`,
  `color-palette`, `theme-editor`, `skip-to-content-link`) exist in
  `snippets/`.
- Liquid block tags (`if/endif`, `for/endfor`, `case/endcase`, `schema/endschema`,
  `stylesheet/endstylesheet`, etc.) are balanced in the new files.
- No unresolved translation keys — the section uses static English strings
  where no matching key existed in `locales/en.default.json` (e.g. the nav
  `aria-label`), so nothing renders "Translation missing."
