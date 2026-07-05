# CRXSSWEI — Horizon Theme (Landing Page Build)

This package is the **Horizon** theme export (`crxsswei.myshopify.com`) with the
custom landing-page design from `design-handoff/landing-page/` implemented as a
native Shopify Liquid section. It is ready to upload as-is.

**Every piece of copy on every custom page/section — headings, field labels,
placeholders, button text, hint/success messages, social URLs, nav links —
is a Shopify setting, editable from Customize. Nothing requires a code
change to update wording.** See "After uploading" below for exactly where
each one lives.

## What changed vs. the raw theme export

1. **`sections/landing-page.liquid`** (new) — the full-viewport splash screen:
   animated particle-field canvas, floating logo, live EST clock, glowing nav
   pills, a disabled "Coming Soon" slot, and Instagram/YouTube icons. Built
   pixel-accurate to `design-handoff/landing-page/README.md` using Horizon's
   own conventions (`{% stylesheet %}`, section-scoped script, `image_picker`,
   block-based nav links).
   - **Entrance preloader** (from `design-handoff/preloader/`): a full-black
     overlay — glowing logo that scales/spins in, a progress bar that fills
     over ~3.6s with a shimmer sweep, and a scanning highlight line — that
     covers the landing page on arrival, then fades away to reveal it.
     Reuses the same **Logo image** setting (inverted to render white on the
     black overlay), so no second image upload is needed. Plays **once per
     browser session** (tracked via `sessionStorage`, so bouncing between
     the shop and home again doesn't replay it), is skipped entirely for
     visitors with `prefers-reduced-motion` set, and can be clicked to skip.
     Toggle it off anytime from Customize → `Landing page` → **"Show
     entrance preloader"**. Lives **only** on this section/page — no other
     template references it.
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
5. **`sections/contact-page.liquid`** (new) — the full-viewport contact
   screen from `design-handoff` (starfield canvas, CONTACT heading,
   minimalist Name/Email/Message form, social icons), built on a **real,
   working Shopify contact form** (`{% form 'contact' %}` — the same engine
   `blocks/contact-form.liquid` already used) so submissions actually reach
   your Shopify inbox and get spam-filtered like normal. On submit, Shopify
   reloads the page and this section shows "MESSAGE SENT — THANK YOU." in
   place of the status line, or the email-validation error if one occurred.
   The original design's "← BACK" link was removed — navigation is handled
   by the site nav bar instead (see item 8).
6. **`templates/page.contact.json`** (replaced) — your existing Contact page
   renders the `contact-page` section, matching the splash-screen aesthetic.
   It runs on the **standard** theme layout (not the header-free `landing`
   layout), so the site nav bar and footer appear above/below it — see item
   8.
7. **`snippets/site-skin.liquid`** (new) — a site-wide visual skin, rendered
   from `layout/theme.liquid` so it applies everywhere the standard Horizon
   header shows up (catalog, product pages, cart, search, blog, etc.):
   - **Header/nav**: white background, Bebas Neue wordmark and nav links
     (uppercase, letter-spaced), a subtle glow on hover/active — the same
     visual language as the landing page's nav pills, without changing any
     of the header's underlying functionality (mega menu, search modal,
     account, cart drawer all work exactly as before).
   - **Catalog grid**: filter labels ("Availability", "Price"), the item
     count, and the sort control now use Share Tech Mono, matching the
     landing page's clock/data styling. Product card titles and prices pick
     up the same mono treatment for a consistent "terminal" look.
   - This is pure CSS layered on top of the existing markup — no Liquid
     logic, JS, or functionality was touched, so cart, checkout, filtering,
     and search behave exactly as they did before.
   - Note: the skin forces the header to a solid white background, which
     will override Horizon's "transparent header" setting if you ever
     enable it (it's off by default in this theme).
8. **`sections/main-policy.liquid`** (new) — a real, styled Policies page:
   lists every policy you've filled in under **Settings → Policies** (Refund,
   Privacy, Terms of Service, Shipping, etc.) as a simple Share Tech Mono
   link list, skipping any you haven't written. On an individual policy
   page it renders that policy's title/body with a "← All policies" link.
   Runs on the standard layout, so it gets the same nav bar/footer as the
   rest of the site (see item 7).
9. **`templates/page.policies.json`** (new) — the reliable home for the
   Policies list, at **`/pages/policies`**. Shopify also has its own
   built-in `/policies` route (`templates/policies.json`, included too), but
   that route **404s until at least one policy has real text in Settings →
   Policies** — it doesn't fail gracefully. Since that's store content we
   can't guarantee is filled in, the **POLICIES** nav button points at the
   `/pages/policies` Page instead, which always renders (with an empty list
   until you add policy text, never a 404). Needs one setup step — see below.
10. **Swipe page transitions** (`snippets/site-skin.liquid`) — Horizon
    already ships a full page-transition system built on the browser's View
    Transitions API (`assets/view-transitions.js`, and the
    `--view-transition-old-main-content` / `--view-transition-new-main-content`
    custom properties in `assets/base.css`); by default it's a fade + slide
    up. The skin overrides just those two custom properties with a
    horizontal swipe (old content slides out left, new content slides in
    from the right) — no JS changes, so it's the same battle-tested
    transition engine Horizon already uses, just a different animation.
    Because product pages reuse the same `--view-transition-new-main-content`
    property for their detail-panel entrance, the swipe applies there too
    when you land on a product from the catalog. Applies to standard
    navigation everywhere `site-skin` renders (catalog, product, cart,
    search, contact, policies) — the landing splash page is intentionally
    excluded since it isn't part of that page-to-page flow. Respects
    `prefers-reduced-motion` automatically, same as Horizon's default.
11. **`sections/password-page.liquid` + `layout/password-page.liquid`**
    (new) — restyles Shopify's storefront password page (shown automatically
    when your store is password-protected under Online Store → Preferences)
    to match the design in `design-handoff/password-page/`: starfield
    canvas, floating wordmark + live EST clock, lock icon, "Coming soon"
    heading, and a password field with the same glow/mono aesthetic as the
    rest of the site.
    - **Important:** the prototype file used a hardcoded JavaScript password
      check (`if (val === 'crxsswei')`) purely for the design preview — that
      check does **not** exist anywhere in this theme. The real password
      field is wired to Shopify's actual `{% form 'storefront_password' %}`,
      the same one `layout/password.liquid` already used, so it validates
      against the real password you set in **Online Store → Preferences**
      and genuinely unlocks the store. A wrong password re-shows the page
      with a shake animation and "Wrong password" hint (via Shopify's real
      `form.errors`); a correct one redirects immediately, server-side —
      there's no client-side "Access granted" moment to show, since Shopify
      never returns control to the page on a correct password.
    - The original `layout/password.liquid` (dialog-based password modal)
      is left in the theme untouched, just no longer referenced — nothing
      was deleted.
    - Wordmark, heading, and hint text are all editable from Customize →
      the `Password page` section — no code changes needed.

## Manual setup required — 2 steps

Both are the same "create a Page, assign its template" pattern, needed
because Shopify Pages are store content and can't be created from theme
files:

1. **Shop page** (optional — SHOP currently links straight to
   `/collections/all`, which works with no setup):
   - **Online Store → Pages → Add page**, title it `Shop`, set its
     **Theme template** to `page.shop`, save.
   - Customize the theme → `Landing page` section → edit the **SHOP**
     block's **Link** to `/pages/shop`.
2. **Policies page** (needed — this is what POLICIES links to):
   - **Online Store → Pages → Add page**, title it `Policies` (this makes
     its URL `/pages/policies`, matching the nav link already wired up).
   - In the **Theme template** dropdown, choose **`page.policies`**.
   - Save. The page will render even if no policies are filled in yet — it
     just shows an empty list until you add text in **Settings → Policies**.

**CONTACT** needs no setup — it links to `/pages/contact`, which already
exists in this theme/store.

**Optional — restyle your nav menu labels to "Home / Catalog / Contact":**
the header's nav links come from your **Main menu** (Online Store →
Navigation), which is store content, not theme code, so it can't be set from
a theme file. To match the reference layout:
1. **Online Store → Navigation → Main menu → Edit**.
2. Set/reorder the links: `Home` → `/`, `Catalog` → `/collections/all`,
   `Contact` → `/pages/contact`.
3. Save. The new Bebas Neue styling applies automatically — no theme changes
   needed for this step.

## After uploading

- **Set the logo image**: Customize the theme → the `Landing page` section →
  set the **Logo image**. Until you do, the section falls back to your store
  name as text so nothing looks broken.
- **Social links**: already pre-filled with the Instagram/YouTube URLs found
  in your footer settings. Editable from the same section in the theme
  editor if they ever change.
- **Nav links**: editable as blocks on the `Landing page` section (label,
  URL, and glow-animation delay per link) — no code changes needed.
- **Preloader**: uses the same Logo image as the rest of the landing page —
  no separate upload needed. Toggle it on/off from Customize → `Landing
  page` → "Show entrance preloader".
- **Contact page copy**: heading, subheading, every field label/placeholder
  (Name, Email, Message), the submit button label, the success message, and
  the social URLs are all editable from Customize → the `Contact page`
  section — no code changes needed for any of it.
- **Page transitions**: if you'd rather not have the swipe effect, turn it
  off entirely from Theme settings → the existing Horizon **"Page
  transition"** checkbox (`settings.page_transition_enabled`) — no code
  changes needed. That checkbox is what the swipe is layered on top of.
- **Policies page copy**: the index heading and the "← All policies" back
  link text are both editable from Customize → the `Policy` section on the
  `page.policies` template.
- **Password page**: your actual store password is set (and password
  protection turned on/off) from **Online Store → Preferences**, same as
  always — that's unrelated to this theme. Wordmark, heading, hint text,
  the password field placeholder, the submit button label, and social URLs
  are all editable from Customize → open the `password` template
  → the `Password page` section.

## Validation performed

- Every `{% schema %}` block in the theme (139 total) parses as valid JSON.
- `templates/index.json`, `templates/page.shop.json`,
  `templates/page.contact.json`, `templates/policies.json`,
  `templates/page.policies.json`, and `templates/password.json` are strict,
  valid JSON.
- The password form uses the same `name="password"` field and
  `form.errors` handling as Shopify's own `layout/password.liquid` dialog,
  so it's the genuine `storefront_password` form, not a decorative one.
- All Liquid snippets referenced by `layout/landing.liquid`
  (`meta-tags`, `stylesheets`, `fonts`, `scripts`, `theme-styles-variables`,
  `color-palette`, `theme-editor`, `skip-to-content-link`) exist in
  `snippets/`.
- Liquid block tags (`if/endif`, `for/endfor`, `case/endcase`, `form/endform`,
  `schema/endschema`, `stylesheet/endstylesheet`, etc.) are balanced in the
  new files.
- No unresolved translation keys — the sections use static English strings
  where no matching key existed in `locales/en.default.json` (e.g. the nav
  `aria-label`, the contact form's status text), so nothing renders
  "Translation missing."
- The contact form uses the same `contact[name]` / `contact[email]` /
  `contact[body]` field names and `form.posted_successfully?` /
  `form.errors` handling as the theme's own `blocks/contact-form.liquid`,
  so it's a genuine Shopify contact form, not a decorative one.
