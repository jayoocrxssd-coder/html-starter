# T2E — Time 2 Eat | Build Log & Session Summary
**Date:** May 30, 2026  
**Branch:** `claude/bold-meitner-Icc8M`  
**Status:** Frontend complete — backend pending

---

## Project Overview

T2E (Time 2 Eat) is a food industry platform with three core goals:

1. **Community Blog** — A dedicated content hub for food operators and food lovers. Builds community, drives SEO, and positions T2E as the voice of the independent food industry.
2. **White-Label Dashboard Sales** — Selling branded food operations dashboards to businesses via the **T2E × Warroom** partnership.
3. **Business Traction & Discovery** — Helping businesses on T2E gain visibility and customers through the marketplace — an upgraded alternative to Yelp where operators have real tools, not just star ratings.

---

## Site Structure (Multi-Page)

| File | Page | Purpose |
|---|---|---|
| `index.html` | Landing Page | Primary CTA, 3-path routing, pricing, demo form |
| `blog.html` | The T2E Journal | Content hub — articles, categories, newsletter |
| `article.html` | Blog Article | Full editorial article page template |
| `for-businesses.html` | For Businesses | B2B white-label pitch (T2E × Warroom) |
| `discover.html` | Discover | Marketplace — find and book food businesses |

---

## Tech Stack

| Layer | Tool | Notes |
|---|---|---|
| Frontend | HTML / CSS / JS | Self-contained, no build step, mobile-first |
| Fonts | Playfair Display + DM Sans | Google Fonts |
| Hosting | Vercel | Already configured, Vercel analytics script included |
| Database + Auth | Supabase | **Backend — not yet implemented** |
| Payments | Stripe | **Backend — not yet implemented** |

---

## Design System

- **Primary color:** `#8B5CF6` (purple)
- **Dark:** `#0F172A` (navy)
- **Font display:** Playfair Display (headings, logo)
- **Font body:** DM Sans (all other text)
- **Border radius:** 12–24px cards, 100px pills
- **Shadows:** 3-level system (`--shadow-sm`, `--shadow-md`, `--shadow-lg`)
- **Animations:** IntersectionObserver scroll reveal, nav scroll blur

---

## Build Phases

### Phase 1 — Multi-Page Restructure
**Commit:** `56f959a`

Converted the original single-page `index.html` into a full multi-page site.

**What changed:**
- `index.html` slimmed down to a focused landing page with 3 audience paths:
  - "I run a food business" → demo form
  - "I want to grow on T2E" → `discover.html`
  - "I want to read about food" → `blog.html`
- Created `blog.html` — full content hub with category filters, featured post scroll, 6-article grid, trending topics, newsletter signup
- Created `for-businesses.html` — B2B white-label pitch page (initial version)
- Created `discover.html` — marketplace/discovery page (initial version)
- Consistent nav and footer across all pages
- Active nav link marked per page

---

### Phase 2 — Full Blog Article Experience
**Commit:** `43906ab`

Built out the blog into a real editorial publication.

**What was built (`article.html`):**
- Scroll progress bar (thin purple bar fills as you read)
- Magazine-style article hero: category pill, read time, publish date, author row with follow button
- Full ~900-word article: "How to Stop Losing Money to Food Waste — The Operator's Playbook"
- Two-column layout: article content (65%) + sticky sidebar (35%)
- Sidebar: author bio card, "More from Marcus," trending articles, tag cloud, newsletter mini-card
- Emoji reaction buttons with JS toggle and count (later upgraded to SVG)
- Share buttons: Twitter/X, LinkedIn, Copy Link (with clipboard API)
- Related articles grid below article
- Newsletter CTA section
- All `blog.html` article card links updated to route to `article.html`

---

### Phase 3 — White-Label B2B Page (Warroom)
**Commits:** `445709c`, `40be212`

Full rebuild of `for-businesses.html` as a polished B2B pitch.

**Sections built:**
- Hero: dark navy/purple gradient, "Powered by T2E × Warroom" badge, stat chips (72hr setup / $0 upfront / Rev Share model)
- "What You Get" — 3 cards: Your Brand, Full Operator Suite, Revenue Partnership
- 8-feature SVG icon grid (all inline stroke SVGs — no emoji, no external libraries)
- "Who This Is For" — 4 audience cards: Restaurant Groups, Catering Networks, Food Tech Startups, Hospitality Brands
- How It Works — 3-step flow with numbered circles + dashed connector
- Comparison table — T2E Partner vs. Build It Yourself (green ✓ / red ✗)
- Partner inquiry form with full validation and success confirm state

**Note:** Partner was renamed from `aionvsn` → **Warroom** during this phase.

---

### Phase 4 — Discover Marketplace
**Commit:** `249feb6`

Full rebuild of `discover.html` as the community marketplace experience.

**Sections built:**
- Search hero: pill search bar, popular category tags, stat strip (2,400+ businesses / 47 cities / 18K+ bookings)
- 8-category SVG chip strip (horizontally scrollable, single-select JS toggle)
- 6 business profile cards: gradient banner, avatar, verified badge, star rating, stats row, "Request Booking" button
- "Why T2E Beats Yelp" — 2-column comparison with VS badge
- 6-city explore grid: Atlanta, Houston, Miami, Orlando, Chicago, Los Angeles
- Operator CTA strip (dark navy background)
- CRES Ventures Kitchen full profile preview
- Booking toast notification (slides up, auto-dismisses after 3s)

---

### Bug Fixes & Code Review Findings
**Commits:** `ef71791`, `40be212`

Issues caught and fixed during `/code-review` passes:

1. **Reaction buttons allowed multi-select** — Fixed to single-select only (picking one deactivates the others)
2. **Emoji reaction buttons** — Replaced with custom inline SVG icons (flame, info circle, chat bubble, heart). Heart fills solid on active state.
3. **Silent clipboard catch** — Updated error state to show `⚠ Copy failed` feedback instead of hanging silently
4. **Warroom rebrand** — `aionvsn` → `Warroom` in `for-businesses.html`

---

### Launch Polish — Phases A, B, C
**Commits:** `132c489`, `54e3deb`, `a589971`

Final pass to make the frontend fully launch-ready.

**Phase A — SEO Meta Tags** (all 5 pages)
- Open Graph tags: `og:type`, `og:title`, `og:description`, `og:url`, `og:site_name`
- Twitter card meta: `twitter:card`, `twitter:title`, `twitter:description`
- Canonical URLs per page
- `author` meta on article page

**Phase B — Links & Forms**
- All dead `href="#"` footer links routed to real pages/anchors
- Footer social links converted to proper `<a>` tags with `target="_blank" rel="noopener noreferrer"`
- `discover.html` popular tag links and footer social divs converted to proper anchors
- Newsletter form submit handlers verified across blog and article pages

**Phase C — UX Polish**
- Pricing: "Coming Soon" → "Free to start / Early Access / Custom"
- Pricing note updated to founder pricing copy
- "Book Now" → "Request Booking" on discover page (pre-launch accuracy)
- Toast message updated: "Added to waitlist! We'll notify you when booking goes live."
- Nav mobile toggle null guards added to all pages
- Demo form confirmation updated with Instagram follow prompt
- Hero food chips aligned with discover categories
- City card hover improved (lift + deeper shadow)

---

## What's Left (Backend)

Everything below requires Supabase + Stripe integration. The frontend is fully wired with placeholder states and form confirm flows — just needs real endpoints.

| Feature | What's needed |
|---|---|
| Demo / waitlist form | Supabase table insert on form submit |
| Partner inquiry form | Supabase table insert on form submit |
| Newsletter signup | Email list integration (Supabase or Resend) |
| User auth | Supabase Auth (email/password or magic link) |
| Operator dashboard | Full app build — see vision doc Phase 1 features |
| Marketplace booking | Calendar availability + Stripe deposit |
| Business profiles | Supabase DB — operators, menus, reviews |
| Blog CMS | Supabase or headless CMS (Sanity/Contentful) |
| Stripe payments | Deposits, invoicing, Stripe Connect for white-label |

---

## Primary Users (MVP)

- Independent restaurant owners (1–5 locations)
- Catering business owners and event caterers
- Food truck operators

---

## Key Decisions Made This Session

- **Multi-page over single-page** — More room for CTAs, better SEO per page, cleaner audience routing
- **No emoji in UI elements** — All icons are inline SVGs for consistency and professionalism
- **Warroom (not aionvsn)** — White-label partner name confirmed as Warroom
- **"Request Booking" not "Book Now"** — Pre-launch accuracy; toast directs to waitlist
- **Single-select reactions** — One reaction per article per session, not multi-select
- **Self-contained HTML** — No build step, no bundler, opens directly in browser

---

*T2E — It's Always Time 2 Eat.*  
*Built for the people who feed communities.*
