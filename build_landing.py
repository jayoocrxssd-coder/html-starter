#!/usr/bin/env python3
"""
build_landing.py — Transform WAR ROOM landing page HTML to v5.1
"""

import re
import json
import os

SOURCE_LANDING = "/root/.claude/uploads/ebaa8db0-1d8f-4c5d-8c25-ecfc69489ff7/f3f333c7-Warroom_Landing__standalone.html"
SOURCE_INDEX8  = "/root/.claude/uploads/ebaa8db0-1d8f-4c5d-8c25-ecfc69489ff7/7ba5cd1d-index_8.html"
OUTPUT_FILE    = "/home/user/html-starter/index.html"

# ─── Step 1: Read source landing page ────────────────────────────────────────
print("Step 1: Reading source landing page...")
with open(SOURCE_LANDING, "r", encoding="utf-8") as f:
    content = f.read()

# ─── Step 1b: Extract inner HTML from bundle ─────────────────────────────────
print("Step 1b: Extracting inner HTML from bundle...")
m = re.search(r'<script type="__bundler/template">(.*?)</script>', content, re.DOTALL)
if not m:
    raise RuntimeError("Could not find <script type='__bundler/template'> tag")

raw = m.group(1).strip()
raw = raw.replace('<\\/script>', '</script>').replace('<script', '<script')
inner = json.loads(raw)
print(f"  Inner HTML decoded, length: {len(inner)} chars")

# ─── Step 2: Update inner HTML ───────────────────────────────────────────────
print("Step 2: Applying text replacements to inner HTML...")
updated = inner

# A. Hero eyebrow
OLD_A = "v5.0 · Now with JARVIS Co-Pilot"
NEW_A = "v5.1 · Video Calls · Payroll · SVG Icons"
assert OLD_A in updated, f"FAIL A: could not find: {OLD_A!r}"
updated = updated.replace(OLD_A, NEW_A, 1)
print("  A. Hero eyebrow updated")

# B. Hero sub paragraph
OLD_B = "Your personal command center for the operator running 3 businesses out of 17 browser tabs. <b>Missions, P&amp;L, intel, calendar, bills, focus</b> — and an AI co-pilot that has read all of it."
NEW_B = "Your personal command center for the operator running 3 businesses out of 17 browser tabs. <b>Missions, P&amp;L, payroll, calendar, video calls, intel, bills, focus</b> — and an AI co-pilot that has read all of it."
assert OLD_B in updated, f"FAIL B: could not find hero sub paragraph"
updated = updated.replace(OLD_B, NEW_B, 1)
print("  B. Hero sub paragraph updated")

# C. Marquee items
OLD_C = """    <span class="marquee-item">Mission Board <span class="sep">◆</span></span>
    <span class="marquee-item">P&amp;L Tracker <span class="sep">◆</span></span>
    <span class="marquee-item">JARVIS Co-Pilot <span class="sep">◆</span></span>
    <span class="marquee-item">Focus Timer <span class="sep">◆</span></span>
    <span class="marquee-item">Intel Notes <span class="sep">◆</span></span>
    <span class="marquee-item">Calendar <span class="sep">◆</span></span>
    <span class="marquee-item">Bills &amp; Expenses <span class="sep">◆</span></span>
    <span class="marquee-item">Goals <span class="sep">◆</span></span>
    <span class="marquee-item">Multi-Business <span class="sep">◆</span></span>
    <span class="marquee-item">Cloud Sync <span class="sep">◆</span></span>
    <!-- duplicate -->
    <span class="marquee-item">Mission Board <span class="sep">◆</span></span>
    <span class="marquee-item">P&amp;L Tracker <span class="sep">◆</span></span>
    <span class="marquee-item">JARVIS Co-Pilot <span class="sep">◆</span></span>
    <span class="marquee-item">Focus Timer <span class="sep">◆</span></span>
    <span class="marquee-item">Intel Notes <span class="sep">◆</span></span>
    <span class="marquee-item">Calendar <span class="sep">◆</span></span>
    <span class="marquee-item">Bills &amp; Expenses <span class="sep">◆</span></span>
    <span class="marquee-item">Goals <span class="sep">◆</span></span>
    <span class="marquee-item">Multi-Business <span class="sep">◆</span></span>
    <span class="marquee-item">Cloud Sync <span class="sep">◆</span></span>"""
NEW_C = """    <span class="marquee-item">Mission Board <span class="sep">◆</span></span>
    <span class="marquee-item">P&amp;L Tracker <span class="sep">◆</span></span>
    <span class="marquee-item">JARVIS Co-Pilot <span class="sep">◆</span></span>
    <span class="marquee-item">Video Calls <span class="sep">◆</span></span>
    <span class="marquee-item">Payroll <span class="sep">◆</span></span>
    <span class="marquee-item">Focus Timer <span class="sep">◆</span></span>
    <span class="marquee-item">Intel Notes <span class="sep">◆</span></span>
    <span class="marquee-item">Calendar <span class="sep">◆</span></span>
    <span class="marquee-item">Bills &amp; Expenses <span class="sep">◆</span></span>
    <span class="marquee-item">Goals <span class="sep">◆</span></span>
    <span class="marquee-item">Daily Debrief <span class="sep">◆</span></span>
    <span class="marquee-item">Cloud Sync <span class="sep">◆</span></span>
    <!-- duplicate -->
    <span class="marquee-item">Mission Board <span class="sep">◆</span></span>
    <span class="marquee-item">P&amp;L Tracker <span class="sep">◆</span></span>
    <span class="marquee-item">JARVIS Co-Pilot <span class="sep">◆</span></span>
    <span class="marquee-item">Video Calls <span class="sep">◆</span></span>
    <span class="marquee-item">Payroll <span class="sep">◆</span></span>
    <span class="marquee-item">Focus Timer <span class="sep">◆</span></span>
    <span class="marquee-item">Intel Notes <span class="sep">◆</span></span>
    <span class="marquee-item">Calendar <span class="sep">◆</span></span>
    <span class="marquee-item">Bills &amp; Expenses <span class="sep">◆</span></span>
    <span class="marquee-item">Goals <span class="sep">◆</span></span>
    <span class="marquee-item">Daily Debrief <span class="sep">◆</span></span>
    <span class="marquee-item">Cloud Sync <span class="sep">◆</span></span>"""
assert OLD_C in updated, "FAIL C: could not find marquee items block"
updated = updated.replace(OLD_C, NEW_C, 1)
print("  C. Marquee items updated")

# D. Features section heading
OLD_D = '      <h2 class="sec-title">Eight purpose-built modules. <em style="color:var(--ink2);font-style:normal">One unified surface.</em></h2>'
NEW_D = '      <h2 class="sec-title">Ten purpose-built modules. <em style="color:var(--ink2);font-style:normal">One unified surface.</em></h2>'
assert OLD_D in updated, "FAIL D: could not find features section heading"
updated = updated.replace(OLD_D, NEW_D, 1)
print("  D. Features section heading updated")

# E. Bento grid — add Video Calls after Goals, add Payroll after Bills
OLD_E_GOALS = """      <!-- Goals -->
      <div class="mod mod-goals">
        <div class="mod-head">
          <div class="mod-glyph">◉</div>
          <div class="mod-title">Goals</div>
          <div class="mod-num">03</div>
        </div>
        <div class="mod-desc">Quarterly targets with rings. See drift before it costs you.</div>
        <div class="mod-body" style="display:flex;align-items:center;gap:14px">
          <div class="ring-wrap">
            <svg width="64" height="64" viewBox="0 0 64 64">
              <circle cx="32" cy="32" r="26" fill="none" stroke="var(--bg3)" stroke-width="6"></circle>
              <circle cx="32" cy="32" r="26" fill="none" stroke="var(--blue)" stroke-width="6" stroke-dasharray="163" stroke-dashoffset="50" stroke-linecap="round" transform="rotate(-90 32 32)"></circle>
            </svg>
            <div class="pct" style="color:var(--blue)">69%</div>
          </div>
          <div style="font-size:11px;color:var(--ink2);line-height:1.5">
            <div><b style="color:var(--ink);font-weight:700">Q3 Revenue</b></div>
            <div class="mono" style="color:var(--ink3);font-size:10px;">$69k / $100k</div>
          </div>
        </div>
      </div>"""
NEW_E_GOALS = OLD_E_GOALS + """

      <!-- Video Calls -->
      <div class="mod mod-vcall">
        <div class="mod-head">
          <div class="mod-glyph">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><polygon points="23 7 16 12 23 17 23 7"/><rect x="1" y="5" width="15" height="14" rx="2" ry="2"/></svg>
          </div>
          <div class="mod-title">Video Calls</div>
          <div class="mod-num">09</div>
        </div>
        <div class="mod-desc">Built-in video meetings — lobby preview, screen share, live chat, speaking detection.</div>
        <div class="mod-body" style="display:flex;gap:6px;flex-wrap:wrap;align-items:center">
          <div style="width:36px;height:36px;border-radius:8px;background:var(--bg3);display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:700">M</div>
          <div style="width:36px;height:36px;border-radius:8px;background:var(--bg3);display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:700">J</div>
          <div style="width:36px;height:36px;border-radius:8px;background:var(--green);opacity:.7;display:flex;align-items:center;justify-content:center;font-size:9px;font-weight:800;color:#fff">YOU</div>
          <div style="font-size:9px;font-family:'DM Mono',monospace;color:var(--green);letter-spacing:0.06em;margin-left:4px">● LIVE · 3 IN CALL</div>
        </div>
      </div>"""
assert OLD_E_GOALS in updated, "FAIL E (Goals block): could not find Goals module"
updated = updated.replace(OLD_E_GOALS, NEW_E_GOALS, 1)
print("  E1. Video Calls module added after Goals")

OLD_E_BILLS_END = """      <!-- Bills & Expenses -->
      <div class="mod mod-bills">
        <div class="mod-head">
          <div class="mod-glyph">◫</div>
          <div class="mod-title">Bills</div>
          <div class="mod-num">08</div>
        </div>
        <div class="mod-desc">Recurring bills with due-soon alerts.</div>
        <div class="mod-body">
          <div style="display:flex;justify-content:space-between;align-items:baseline;margin-bottom:6px">
            <div style="font-size:11px;color:var(--ink2)">Due this week</div>
            <div style="font-size:18px;font-weight:800;letter-spacing:-0.02em" class="mono">$2,840</div>
          </div>
          <div style="height:6px;background:var(--bg2);border-radius:100px;overflow:hidden">
            <div style="width:64%;height:100%;background:var(--blue);border-radius:100px"></div>
          </div>
          <div style="font-size:9px;font-family:'DM Mono',monospace;color:var(--ink3);margin-top:6px;letter-spacing:0.06em">5 OF 8 PAID · NEXT: STRIPE $89 IN 2D</div>
        </div>
      </div>
    </div>"""
NEW_E_BILLS_END = """      <!-- Bills & Expenses -->
      <div class="mod mod-bills">
        <div class="mod-head">
          <div class="mod-glyph">◫</div>
          <div class="mod-title">Bills</div>
          <div class="mod-num">08</div>
        </div>
        <div class="mod-desc">Recurring bills with due-soon alerts.</div>
        <div class="mod-body">
          <div style="display:flex;justify-content:space-between;align-items:baseline;margin-bottom:6px">
            <div style="font-size:11px;color:var(--ink2)">Due this week</div>
            <div style="font-size:18px;font-weight:800;letter-spacing:-0.02em" class="mono">$2,840</div>
          </div>
          <div style="height:6px;background:var(--bg2);border-radius:100px;overflow:hidden">
            <div style="width:64%;height:100%;background:var(--blue);border-radius:100px"></div>
          </div>
          <div style="font-size:9px;font-family:'DM Mono',monospace;color:var(--ink3);margin-top:6px;letter-spacing:0.06em">5 OF 8 PAID · NEXT: STRIPE $89 IN 2D</div>
        </div>
      </div>

      <!-- Payroll -->
      <div class="mod mod-payroll">
        <div class="mod-head">
          <div class="mod-glyph">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><rect x="2" y="7" width="20" height="14" rx="2"/><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/></svg>
          </div>
          <div class="mod-title">Payroll</div>
          <div class="mod-num">10</div>
        </div>
        <div class="mod-desc">Employee roster per business. Hourly, salary, contractor — headcount and cost at a glance.</div>
        <div class="mod-body">
          <div style="display:flex;justify-content:space-between;align-items:baseline;margin-bottom:8px">
            <div style="font-size:11px;color:var(--ink2)">Monthly payroll</div>
            <div style="font-size:18px;font-weight:800;letter-spacing:-0.02em" class="mono">$18,400</div>
          </div>
          <div style="font-size:9px;font-family:'DM Mono',monospace;color:var(--ink3);letter-spacing:0.06em">6 EMPLOYEES · $220.8K / YR</div>
        </div>
      </div>
    </div>"""
assert OLD_E_BILLS_END in updated, "FAIL E (Bills end): could not find Bills module closing"
updated = updated.replace(OLD_E_BILLS_END, NEW_E_BILLS_END, 1)
print("  E2. Payroll module added after Bills")

# F. Demo sidebar nav items
OLD_F = """          <div class="ni"><span class="ic">◫</span>Bills</div>
          <div class="lbl" style="margin-top:14px">Businesses</div>"""
NEW_F = """          <div class="ni"><span class="ic">◫</span>Bills</div>
          <div class="ni"><span class="ic">
            <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><polygon points="23 7 16 12 23 17 23 7"/><rect x="1" y="5" width="15" height="14" rx="2"/></svg>
          </span>Video Calls</div>
          <div class="ni"><span class="ic">
            <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><rect x="2" y="7" width="20" height="14" rx="2"/><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/></svg>
          </span>Payroll</div>
          <div class="lbl" style="margin-top:14px">Businesses</div>"""
assert OLD_F in updated, "FAIL F: could not find Bills nav item"
updated = updated.replace(OLD_F, NEW_F, 1)
print("  F. Demo sidebar nav items updated")

# G. Compare card heading
OLD_G1 = "        <h4>One surface. Eight modules. One brain.</h4>"
NEW_G1 = "        <h4>One surface. Ten modules. One brain.</h4>"
assert OLD_G1 in updated, "FAIL G1: could not find compare card heading"
updated = updated.replace(OLD_G1, NEW_G1, 1)
print("  G1. Compare card heading updated")

OLD_G2 = """          <li>Local-first, cloud-synced. Your data is yours.</li>
        </ul>"""
NEW_G2 = """          <li>Local-first, cloud-synced. Your data is yours.</li>
          <li>Built-in video calls — no Zoom subscription needed</li>
          <li>Payroll tracker — headcount and cost per business, always visible</li>
        </ul>"""
assert OLD_G2 in updated, "FAIL G2: could not find compare list end"
updated = updated.replace(OLD_G2, NEW_G2, 1)
print("  G2. Compare list items added")

# H. Version strings — replace all v5.0 with v5.1
count_h = updated.count("v5.0")
updated = updated.replace("v5.0", "v5.1")
print(f"  H. Replaced {count_h} occurrences of v5.0 → v5.1")

# I. JARVIS version chip (already handled by H above, but double-check)
# The replace in H covers this. No separate action needed.
print("  I. JARVIS version chip covered by step H")

# J. Navigation — add Video nav link
OLD_J = '      <a href="#compare">vs. Tabs</a>'
NEW_J = '      <a href="#features">Video</a>\n      <a href="#compare">vs. Tabs</a>'
assert OLD_J in updated, "FAIL J: could not find compare nav link"
updated = updated.replace(OLD_J, NEW_J, 1)
print("  J. Navigation Video link added")

# K. What's new section — insert before COMPARE section
WHATS_NEW = """<!-- ═════════ WHAT'S NEW ═════════ -->
<section style="background:var(--bg2);padding:56px 0 40px">
  <div class="wrap">
    <div class="sec-head">
      <div class="sec-eyebrow"><span class="lin"></span> Changelog · v5.1</div>
      <h2 class="sec-title">Eight commits. <em style="color:var(--red);font-style:normal">Forty improvements.</em></h2>
      <p class="sec-sub">Every release is a focused deep-dive. Here's what shipped in the latest war room update.</p>
    </div>
    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:16px;max-width:1280px;margin:0 auto">
      <div style="background:var(--surface);border:0.5px solid var(--border2);border-radius:14px;padding:20px 22px">
        <div style="font-size:10px;font-weight:700;letter-spacing:0.14em;color:var(--green);margin-bottom:8px">VIDEO CALLS</div>
        <div style="font-size:14px;font-weight:700;margin-bottom:6px">Full in-app video meetings</div>
        <div style="font-size:12px;color:var(--ink2);line-height:1.5">Lobby preview, real mic/cam controls, speaking detection, dynamic grid, custom screen share picker (monitor · window · tab), in-call chat, meeting history.</div>
      </div>
      <div style="background:var(--surface);border:0.5px solid var(--border2);border-radius:14px;padding:20px 22px">
        <div style="font-size:10px;font-weight:700;letter-spacing:0.14em;color:var(--blue);margin-bottom:8px">PAYROLL</div>
        <div style="font-size:14px;font-weight:700;margin-bottom:6px">Employee roster per business</div>
        <div style="font-size:12px;color:var(--ink2);line-height:1.5">Full CRUD for employees — hourly, salary, or contractor. Headcount, monthly cost, and annual cost summary auto-calculated per business.</div>
      </div>
      <div style="background:var(--surface);border:0.5px solid var(--border2);border-radius:14px;padding:20px 22px">
        <div style="font-size:10px;font-weight:700;letter-spacing:0.14em;color:var(--amber);margin-bottom:8px">UI POLISH</div>
        <div style="font-size:14px;font-weight:700;margin-bottom:6px">Emoji replaced with SVG icons</div>
        <div style="font-size:12px;color:var(--ink2);line-height:1.5">30+ emoji swapped for Lucide-style stroke SVGs app-wide. 19 native browser popups replaced with branded dark-theme dialogs. Zero jank.</div>
      </div>
      <div style="background:var(--surface);border:0.5px solid var(--border2);border-radius:14px;padding:20px 22px">
        <div style="font-size:10px;font-weight:700;letter-spacing:0.14em;color:var(--red);margin-bottom:8px">DAILY DEBRIEF</div>
        <div style="font-size:14px;font-weight:700;margin-bottom:6px">Custom icons per step</div>
        <div style="font-size:12px;color:var(--ink2);line-height:1.5">Energy, intention, businesses, blockers, summary — each debrief step now has a unique Lucide icon. Energy check and blocker quick-tags fully icon-ified.</div>
      </div>
    </div>
  </div>
</section>

"""
OLD_K = "<!-- ═════════ COMPARE ═════════ -->"
assert OLD_K in updated, "FAIL K: could not find COMPARE section marker"
updated = updated.replace(OLD_K, WHATS_NEW + OLD_K, 1)
print("  K. What's new in v5.1 section inserted")

print(f"  Inner HTML updated, new length: {len(updated)} chars")

# ─── Step 3: Re-encode inner HTML back into bundle ────────────────────────────
print("Step 3: Re-encoding inner HTML into bundle...")
updated_inner_json = json.dumps(updated)
updated_inner_json = updated_inner_json.replace('</script>', '<\\/script>').replace('<script', '<script')

# Replace the original template content in the outer file
original_template_content = m.group(1)
new_template_tag = f'<script type="__bundler/template">{updated_inner_json}</script>'
original_template_tag = m.group(0)
content_updated = content.replace(original_template_tag, new_template_tag, 1)
print(f"  Bundle re-encoded, outer file length: {len(content_updated)} chars")

# ─── Step 4: Update outer wrapper thumbnail SVG ───────────────────────────────
print("Step 4: Updating outer thumbnail SVG...")

OLD_SVG = """  <svg viewBox="0 0 1200 800" xmlns="http://www.w3.org/2000/svg">
    <rect width="1200" height="800" fill="#f4f4f2"></rect>
    <g transform="translate(600 400)" text-anchor="middle" font-family="Syne, sans-serif" font-weight="800">
      <rect x="-70" y="-180" width="140" height="140" rx="28" fill="#0e0e0d"></rect>
      <text x="0" y="-90" fill="#f4f4f2" font-size="92">◈</text>
      <text x="0" y="20" fill="#0e0e0d" font-size="64" letter-spacing="14">WAR ROOM</text>
      <text x="0" y="70" fill="#9a9a98" font-size="20" letter-spacing="6">v5.0 · LOADING</text>
      <circle cx="0" cy="130" r="6" fill="#1ea96b">
        <animate attributeName="opacity" values="1;0.2;1" dur="1.4s" repeatCount="indefinite"></animate>
      </circle>
    </g>
  </svg>"""
NEW_SVG = """  <svg viewBox="0 0 1200 800" xmlns="http://www.w3.org/2000/svg">
    <rect width="1200" height="800" fill="#0f0f0e"></rect>
    <g transform="translate(600 400)">
      <rect x="-110" y="-110" width="220" height="220" rx="32" fill="#f0f0ee"></rect>
      <text x="0" y="22" text-anchor="middle" font-family="Syne, Helvetica, sans-serif" font-weight="800" font-size="72" letter-spacing="6" fill="#0f0f0e">WR</text>
    </g>
    <text x="600" y="600" text-anchor="middle" font-family="Syne, Helvetica, sans-serif" font-weight="800" font-size="36" letter-spacing="14" fill="#f0f0ee">WAR  ROOM</text>
    <text x="600" y="650" text-anchor="middle" font-family="Helvetica, sans-serif" font-weight="400" font-size="14" letter-spacing="6" fill="#666660">v5.1 · LOADING</text>
    <circle cx="600" cy="690" r="6" fill="#1ea96b">
      <animate attributeName="opacity" values="1;0.2;1" dur="1.4s" repeatCount="indefinite"/>
    </circle>
  </svg>"""
assert OLD_SVG in content_updated, "FAIL SVG: could not find old thumbnail SVG"
content_updated = content_updated.replace(OLD_SVG, NEW_SVG, 1)
print("  SVG thumbnail replaced with dark version")

# Update outer body background color #f4f4f2 -> #0f0f0e
# Also update thumbnail background in CSS
OLD_BG_BODY = "body { background: #f4f4f2;"
NEW_BG_BODY = "body { background: #0f0f0e;"
assert OLD_BG_BODY in content_updated, "FAIL BG BODY: could not find body background"
content_updated = content_updated.replace(OLD_BG_BODY, NEW_BG_BODY, 1)
print("  Body background updated to dark")

OLD_BG_THUMB = "background: #f4f4f2; z-index: 9999;"
NEW_BG_THUMB = "background: #0f0f0e; z-index: 9999;"
assert OLD_BG_THUMB in content_updated, "FAIL BG THUMB: could not find thumbnail background in CSS"
content_updated = content_updated.replace(OLD_BG_THUMB, NEW_BG_THUMB, 1)
print("  Thumbnail background CSS updated to dark")

# ─── Step 5: Write output ─────────────────────────────────────────────────────
print(f"Step 5: Writing output to {OUTPUT_FILE}...")
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write(content_updated)

size = os.path.getsize(OUTPUT_FILE)
print(f"\nSUCCESS: Written {OUTPUT_FILE}")
print(f"         File size: {size:,} bytes ({size/1024:.1f} KB)")
