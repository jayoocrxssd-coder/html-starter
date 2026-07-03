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
   nothing was lost. It's kept in the theme as an optional page template in
   case you ever want a dedicated "Shop" landing page in addition to your
   catalog — see below.

## No manual setup required

The landing page's **SHOP** nav pill links straight to `/collections/all`
— Shopify's built-in "all products" catalog — so it works immediately after
upload, no admin setup needed. Contact and Return Policy also point at
things that already exist in this theme (`page.contact`,
`/policies/refund-policy`).

**Optional:** if you'd rather SHOP land on the custom page built from your
old homepage (Hero + Featured Collection + Marquee) instead of the raw
catalog, you can wire that up later:
1. **Online Store → Pages → Add page**, title it `Shop`, set its
   **Theme template** to `page.shop`, save.
2. Customize the theme → `Landing page` section → edit the **SHOP** block's
   **Link** to `/pages/shop`.

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
