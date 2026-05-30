# Time 2 Eat (T2E) — Vision & Concept Document
**Date:** May 30, 2026
**Status:** WIP — Brainstorm & Planning Phase

---

## The Name
**T2E = Time 2 Eat**

A platform built for the people who feed communities. The name is consumer-friendly, memorable, and scales from a business tool into a full community marketplace without ever needing a rebrand.

**Tagline ideas:**
- *"It's always Time 2 Eat"*
- *"Your business, on time, every time"*

---

## The Problem
Restaurant owners, catering companies, and food entrepreneurs are running businesses on group chats, handwritten notes, spreadsheets, and sheer willpower. They lack:
- A centralized place to manage jobs, menus, staff, and clients
- Professional invoicing and payment collection tools
- Inventory visibility and food waste tracking
- Online presence to reach new customers in their community

---

## Who We're Building For
**Primary Users (MVP):**
- Independent restaurant owners (1–5 locations)
- Catering business owners and event caterers
- Food truck operators

---

## What the Full Build Does

### For the Business Owner

**Operations Management**
- Create and manage catering events/jobs from booking to completion
- Build digital menus with pricing, photos, dietary tags, and categories
- Assign staff to events and manage shift scheduling
- Track inventory levels with low-stock alerts
- See all orders (dine-in, catering, delivery) in one dashboard

**Financial Tools**
- Auto-generate professional invoices from job details in seconds
- Collect client deposits online via Stripe
- Track revenue, expenses, and profit margins
- Identify best and worst performing menu items

**Client Management**
- Full client list with contact info and job history
- Shareable event links for clients to confirm menus and details
- Automated reminders for upcoming events and unpaid balances

**Insights & Intelligence**
- Sales trends by day, week, and season
- Food waste tracking — know what's being thrown away and what it costs
- AI-suggested daily specials based on near-expiry inventory

---

### For the Community

- Community members discover local caterers, food trucks, and restaurants
- Book a caterer directly for birthdays, graduations, church events, corporate lunches
- Support small and independent food businesses instead of defaulting to big chains
- Levels the playing field — gives small businesses the same professional tools as large operations
- Long-term: redirect surplus food from events to local food banks and community fridges
- Amplifies cultural food traditions and minority-owned food businesses

---

## Platform Phases

### Phase 1 — Business Tool (MVP)
Restaurant and catering owners manage their full operation in one app.
- Jobs & Events
- Menu Builder
- Client Management
- Invoice Generator
- Inventory Tracker
- Staff Scheduler
- Dashboard & Analytics

### Phase 2 — Community Marketplace
Customers discover and book local caterers and restaurants.
- Business profiles and menus visible to the public
- Online booking and ordering
- Reviews and ratings
- Event catering requests

### Phase 3 — Ecosystem
- Supplier ordering (restock ingredients directly in-app)
- Food surplus redistribution to community fridges and food banks
- Resources and training for aspiring food entrepreneurs
- Grant and micro-loan discovery for small food business owners

---

## Recommended Tech Stack

| Layer | Tool | Reason |
|---|---|---|
| Frontend | HTML / CSS / JS (mobile-first) | Already started, dark UI (Stratus template) |
| Database + Auth | Supabase | Free tier, real-time, easy setup |
| Hosting | Vercel | Already configured |
| Payments | Stripe | Deposits, invoicing, payouts |

---

## MVP — 6 Core Screens

1. **Dashboard** — Upcoming jobs, revenue summary, alerts
2. **Jobs / Events** — Create event, attach client, assign menu and staff
3. **Menu Builder** — Build menus with pricing, photos, and dietary tags
4. **Clients** — Contact list with full job history per client
5. **Invoice Generator** — Auto-built from job details, shareable via link
6. **Inventory** — Stock levels with low-stock alerts

---

## The Impact

Time 2 Eat is built for the people who feed communities — the catering company working out of a home kitchen, the restaurant family that's been open 20 years, the food truck operator grinding every weekend. T2E gives them professional infrastructure, saves them hours every week, helps them stop losing money to waste and disorganization, and puts them in front of new customers who want exactly what they offer. When small food businesses win, neighborhoods win — more jobs, more food culture, more money staying local.

---

## Next Steps
- [ ] Confirm MVP feature set with full team
- [ ] Wireframe the 6 core screens
- [ ] Set up Supabase project and authentication
- [ ] Build dashboard shell using Stratus UI as design base
- [ ] Implement Jobs/Events CRUD as first feature
