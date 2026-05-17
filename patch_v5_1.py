#!/usr/bin/env python3
"""
patch_v5_1.py — Apply three targeted changes to the WAR ROOM landing page:
  1. JARVIS → AXIS (co-pilot rename, everywhere)
  2. "Try a prompt" → Interactive FAQ for buyers (hardcoded answers, no API)
  3. Changelog → WAR ROOM differentiators
"""

import re, json

SRC = "/home/user/html-starter/index.html"
OUT = "/home/user/html-starter/index.html"

print("Reading index.html...")
with open(SRC, "r", encoding="utf-8") as f:
    content = f.read()

# ── Extract inner HTML ────────────────────────────────────────────────────────
m = re.search(r'<script type="__bundler/template">(.*?)</script>', content, re.DOTALL)
if not m:
    raise RuntimeError("No __bundler/template tag found")

raw = m.group(1).strip()
raw = raw.replace('<\\/script>', '</script>').replace('<script', '<script')
inner = json.loads(raw)
print(f"  Decoded inner HTML: {len(inner):,} chars")

# ═════════════════════════════════════════════════════════════════════════════
# CHANGE 1 — JARVIS → AXIS (display text, labels, IDs, placeholder text)
# ═════════════════════════════════════════════════════════════════════════════
print("Change 1: Renaming JARVIS → AXIS...")

# All plain-text occurrences (case-preserving)
axis_swaps = [
    # section heading
    ("Meet <em style=\"color:var(--red);font-style:normal\">JARVIS</em>. Built for operators.",
     "Meet <em style=\"color:var(--red);font-style:normal\">AXIS</em>. Built for operators."),
    # section subtext
    ("No sign-up needed to talk to him. Ask anything an operator asks at 7am with one cup of coffee.",
     "No sign-up needed. Click a question below, or type your own. AXIS answers like an operator, not a chatbot."),
    # left column heading
    ("An AI that lives inside your business.",
     "An AI that lives inside your business."),
    # left column body
    ("JARVIS reads your P&amp;L, your missions, your calendar, your intel notes — and answers in your voice. Calm. Precise. Tactical. He doesn't ramble.",
     "AXIS reads your P&amp;L, your missions, your calendar, your intel notes — and answers in your voice. Calm. Precise. Tactical. No rambling."),
    # "Try a prompt" label
    ("<div class=\"label\" style=\"color:rgba(255,255,255,.5);margin-bottom:8px\">Try a prompt</div>",
     "<div class=\"label\" style=\"color:rgba(255,255,255,.5);margin-bottom:8px\">Common questions</div>"),
    # chat head name
    ("<span class=\"who\">JARVIS</span>",
     "<span class=\"who\">AXIS</span>"),
    # chat opening message
    ("Operator on deck. I'm JARVIS — your war-room co-pilot. Ask me anything an operator asks: strategy, diagnostics, prioritization, hard calls. I won't sugarcoat.",
     "AXIS online. I'm your WAR ROOM co-pilot — click a question or type your own. I answer from your actual data: missions, P&amp;L, calendar, intel. Straight talk only."),
    # input placeholder
    ("placeholder=\"Ask JARVIS anything…\"",
     "placeholder=\"Ask AXIS anything…\""),
    # JARVIS module in bento
    ("<div class=\"mod-title\" style=\"color:var(--bg)\">JARVIS</div>",
     "<div class=\"mod-title\" style=\"color:var(--bg)\">AXIS</div>"),
    # bento module description
    ("An AI co-pilot that has read every mission, every dollar, every note in your war room. Ask anything. Get a briefing every morning.",
     "An AI co-pilot that has read every mission, every dollar, every note in your war room. Ask anything. Get a briefing every morning."),
    # JARVIS bento chat message
    ("You've got <b>$4,200 in receivables</b> aging past 30 days at Stratus — chase those first. Then your Q3 review at 14:00.",
     "You've got <b>$4,200 in receivables</b> aging past 30 days at Stratus — chase those first. Then your Q3 review at 14:00."),
    # Demo sidebar
    ("<span class=\"ic\">◈</span>JARVIS</div>",
     "<span class=\"ic\">◈</span>AXIS</div>"),
    # Section anchor
    ('<section id="jarvis">',
     '<section id="axis">'),
    # Nav link target
    ('<a href="#jarvis">JARVIS</a>',
     '<a href="#axis">AXIS</a>'),
    # Section comment
    ('<!-- ═════════ JARVIS LIVE ═════════ -->',
     '<!-- ═════════ AXIS LIVE ═════════ -->'),
    # Stats section JARVIS ref
    ("JARVIS Co-Pilot",
     "AXIS Co-Pilot"),
    # Compare card
    ("JARVIS reads everything. Briefs you in 60s every morning",
     "AXIS reads everything. Briefs you in 60s every morning"),
    # Demo card heading
    ("<div class=\"cl\">JARVIS — Morning Brief</div>",
     "<div class=\"cl\">AXIS — Morning Brief</div>"),
    # Eyebrow on section
    ("<div class=\"sec-eyebrow\"><span class=\"lin\"></span> Try the co-pilot live</div>",
     "<div class=\"sec-eyebrow\"><span class=\"lin\"></span> Ask the co-pilot live</div>"),
    # Footer JARVIS ref
    ("<span>JARVIS · ready</span>",
     "<span>AXIS · ready</span>"),
    # Hero status footer
    ("JARVIS · ready",
     "AXIS · ready"),
    # Prompt chips onclick — rename askJarvis to askAxis
    ("askJarvis(", "askAxis("),
    # Form onsubmit
    ("onsubmit=\"return submitJarvis(event)\"",
     "onsubmit=\"return submitAxis(event)\""),
    # IDs
    ('id="jarvisBody"', 'id="axisBody"'),
    ('id="jarvisForm"', 'id="axisForm"'),
    ('id="jarvisInput"', 'id="axisInput"'),
    ('id="jarvisSend"', 'id="axisSend"'),
    # JS variable/function names
    ("jarvisHistory", "axisHistory"),
    ("jarvisBusy", "axisBusy"),
    ("appendJarvisMsg", "appendAxisMsg"),
    ("function askJarvis", "function askAxis"),
    ("async function submitJarvis", "async function submitAxis"),
    ("document.getElementById('jarvisInput')", "document.getElementById('axisInput')"),
    ("document.getElementById('jarvisSend')", "document.getElementById('axisSend')"),
    ("document.getElementById('jarvisBody')", "document.getElementById('axisBody')"),
    # Remaining JARVIS_SYSTEM ref (will be replaced in FAQ block anyway)
    ("JARVIS_SYSTEM", "AXIS_SYSTEM"),
    # Any leftover plain JARVIS in JS strings
    ("I'm JARVIS", "I'm AXIS"),
    ("War Room JARVIS", "WAR ROOM AXIS"),
    # Section title text
    ("JARVIS Co-Pilot <span class=\"sep\">◆</span>",
     "AXIS Co-Pilot <span class=\"sep\">◆</span>"),
]

for old, new in axis_swaps:
    if old in inner:
        inner = inner.replace(old, new)
        print(f"  ✓ {old[:55]!r}")
    else:
        print(f"  – (not found) {old[:55]!r}")

# ═════════════════════════════════════════════════════════════════════════════
# CHANGE 2 — Replace prompt chips with FAQ chips + replace JS with FAQ logic
# ═════════════════════════════════════════════════════════════════════════════
print("\nChange 2: FAQ section + hardcoded AXIS answers...")

OLD_CHIPS = '''            <button class="pchip" onclick="askAxis('What should I focus on this morning?')">What should I focus on?</button>
            <button class="pchip" onclick="askAxis('My margins are slipping at one business. How do I diagnose it?')">Margins slipping — how do I diagnose?</button>
            <button class="pchip" onclick="askAxis('Write me a 3-day plan to close a stalled deal.')">3-day plan to close a stalled deal</button>
            <button class="pchip" onclick="askAxis('Brutal feedback on my pricing strategy: $89/mo, $290/mo, custom.')">Brutal feedback on my pricing</button>
            <button class="pchip" onclick="askAxis('What KPIs should I actually track for a 2-person agency?')">KPIs for a 2-person agency</button>'''

NEW_CHIPS = '''            <button class="pchip" onclick="askFAQ('whats-different')">What makes WAR ROOM different?</button>
            <button class="pchip" onclick="askFAQ('is-private')">Is my data private?</button>
            <button class="pchip" onclick="askFAQ('how-axis-works')">How does AXIS know my business?</button>
            <button class="pchip" onclick="askFAQ('what-does-it-cost')">What does it cost?</button>
            <button class="pchip" onclick="askFAQ('works-offline')">Does it work offline?</button>
            <button class="pchip" onclick="askFAQ('mobile')">Does it work on mobile?</button>'''

if OLD_CHIPS in inner:
    inner = inner.replace(OLD_CHIPS, NEW_CHIPS)
    print("  ✓ FAQ chips replaced")
else:
    print("  – FAQ chips block not found (may already be patched)")

# Replace the JS functions block
OLD_JS_FUNCS = '''function askAxis(prompt) {
    const input = document.getElementById('axisInput');
    input.value = prompt;
    submitAxis(new Event('submit'));
  }

  async function submitAxis(e) {
    if (e) e.preventDefault();
    if (axisBusy) return false;
    const input = document.getElementById('axisInput');
    const text = input.value.trim();
    if (!text) return false;

    input.value = '';
    appendAxisMsg(text, 'user', false);
    axisHistory.push({ role: 'user', content: text });

    axisBusy = true;
    document.getElementById('axisSend').disabled = true;

    // Loading indicator
    const loading = appendAxisMsg('<div class="jthinking"><span></span><span></span><span></span></div>', 'ai', true);

    try {
      // Build messages with system as first user turn (Claude API style)
      const messages = [
        { role: 'user', content: AXIS_SYSTEM + '\\n\\n--- Operator query: ---\\n' + text }
      ];
      if (!window.claude || typeof window.claude.complete !== 'function') {
        // Offline / standalone fallback — Claude API only available in hosted preview
        loading.innerHTML = renderMarkdown(
          `**JARVIS link unavailable in this offline build, Operator.**\\n\\n` +
          `The live co-pilot only runs inside the hosted War Room. ` +
          `Reserve access above and you'll get a key to chat with the real thing — ` +
          `briefings, diagnostics, brutal feedback, the works.`
        );
        axisHistory.push({ role: 'assistant', content: '[offline]' });
        return false;
      }
      const reply = await window.claude.complete({ messages });
      loading.innerHTML = renderMarkdown(reply.trim());
      axisHistory.push({ role: 'assistant', content: reply });
    } catch (err) {
      loading.innerHTML = `<i style="opacity:.6">System static. AXIS link unstable — try again, Operator. (${(err && err.message) || 'error'})</i>`;
    } finally {
      axisBusy = false;
      document.getElementById('axisSend').disabled = false;
    }

    return false;
  }'''

NEW_JS_FUNCS = r"""/* ── AXIS FAQ answers ── */
  const FAQ_ANSWERS = {
    'whats-different': [
      "**Good question. Here's the honest answer:**",
      "Notion is a blank canvas. Trello is a board. Sheets is a spreadsheet. None of them know you run *three businesses*, track payroll, have $4.2k in aging receivables, and a call at 14:00.",
      "WAR ROOM is purpose-built for the multi-business operator. Ten modules — missions, P&L, payroll, calendar, intel notes, bills, focus timer, video calls, goals, and daily debrief — all wired together. Every module knows about every other.",
      "**AXIS pulls from all of them at once.** Ask 'what should I focus on?' and it answers from your *actual data*, not a generic template. That's the difference."
    ],
    'is-private': [
      "**Local-first. Always.**",
      "Your data lives in your browser's localStorage by default. No accounts. No servers. No surveillance. We can't read your P&L because it never touches our infrastructure.",
      "Cloud sync is **opt-in**. You pick the destination (Google Drive, Dropbox, or a custom endpoint). You hold the keys. If you never enable sync, the app works 100% offline — forever.",
      "One file. Your machine. Your data."
    ],
    'how-axis-works': [
      "**AXIS is context-aware, not generic.**",
      "When you use WAR ROOM, you're building a structured picture of your businesses: P&L entries, mission lists, calendar events, intel notes, bill schedules, payroll data. AXIS indexes all of it.",
      "Ask *'What's dragging my margin at Stratus?'* and AXIS has your actual numbers to work with. Ask *'What should I tackle today?'* and it knows your open missions, due bills, and calendar — not a generic productivity tip.",
      "In this preview you're seeing the landing-page demo. **Reserve access to connect AXIS to your live data.**"
    ],
    'what-does-it-cost': [
      "**Free during beta. Founder pricing after.**",
      "No credit card to reserve a spot. While we're in closed beta, access is free — full features, no limits.",
      "Early operators who join the list lock in **founder pricing** when we launch paid tiers. That price will never increase for you, regardless of what public pricing does.",
      "We're building for operators who want a permanent command center, not a monthly subscription that raises rates every year."
    ],
    'works-offline': [
      "**Yes. That's by design.**",
      "WAR ROOM is a single HTML file. Open it once and it works with zero internet connection. Every module — missions, P&L, focus timer, calendar, bills — runs entirely client-side.",
      "AXIS's AI features require a connection for live queries, but your data, UI, and all non-AI functionality are fully offline.",
      "Bookmark the file locally or host it yourself. Either way, it's yours."
    ],
    'mobile': [
      "**Fully responsive.**",
      "The layout reflows to a single-column command center on small screens. The hamburger nav, swipeable module panels, and touch-friendly tap targets were built in — not bolted on.",
      "The focus timer, mission board, and daily debrief work especially well on mobile. Video calls use your device's camera and mic natively.",
      "No app store. No download. Just the URL — or the file saved to your home screen."
    ]
  };

  function askFAQ(key) {
    const answers = FAQ_ANSWERS[key];
    if (!answers) return;
    // Show the question label in chat
    const labels = {
      'whats-different': 'What makes WAR ROOM different?',
      'is-private': 'Is my data private?',
      'how-axis-works': 'How does AXIS know my business?',
      'what-does-it-cost': 'What does it cost?',
      'works-offline': 'Does it work offline?',
      'mobile': 'Does it work on mobile?'
    };
    appendAxisMsg(labels[key] || key, 'user', false);
    // Show typing indicator briefly then reveal answer
    const loading = appendAxisMsg('<div class="jthinking"><span></span><span></span><span></span></div>', 'ai', true);
    setTimeout(() => {
      loading.innerHTML = answers.map(p => renderMarkdown(p)).join('<br>');
      const body = document.getElementById('axisBody');
      if (body) body.scrollTop = body.scrollHeight;
    }, 620);
  }

  function askAxis(prompt) {
    const input = document.getElementById('axisInput');
    input.value = prompt;
    submitAxis(new Event('submit'));
  }

  function submitAxis(e) {
    if (e) e.preventDefault();
    const input = document.getElementById('axisInput');
    const text = input.value.trim();
    if (!text) return false;
    input.value = '';
    // Check if it matches a FAQ key
    const faqMap = {
      'what makes war room different': 'whats-different',
      'is my data private': 'is-private',
      'how does axis know': 'how-axis-works',
      'what does it cost': 'what-does-it-cost',
      'does it work offline': 'works-offline',
      'does it work on mobile': 'mobile',
      'offline': 'works-offline',
      'mobile': 'mobile',
      'cost': 'what-does-it-cost',
      'price': 'what-does-it-cost',
      'private': 'is-private',
      'data': 'is-private',
      'different': 'whats-different',
    };
    const lower = text.toLowerCase();
    for (const [kw, faqKey] of Object.entries(faqMap)) {
      if (lower.includes(kw)) {
        askFAQ(faqKey);
        return false;
      }
    }
    // Fallback for anything not matched
    appendAxisMsg(text, 'user', false);
    const loading = appendAxisMsg('<div class="jthinking"><span></span><span></span><span></span></div>', 'ai', true);
    setTimeout(() => {
      loading.innerHTML = renderMarkdown(
        "**That's a live AXIS query — only available inside the full War Room.**\n\n" +
        "Click one of the questions above to see how AXIS thinks. " +
        "Reserve access to wire AXIS to your actual P&L, missions, and businesses."
      );
      const body = document.getElementById('axisBody');
      if (body) body.scrollTop = body.scrollHeight;
    }, 600);
    return false;
  }"""

if OLD_JS_FUNCS in inner:
    inner = inner.replace(OLD_JS_FUNCS, NEW_JS_FUNCS)
    print("  ✓ JS functions replaced with FAQ logic")
else:
    # Try partial match to locate the block
    if "async function submitAxis" in inner:
        # Find start and end of the block
        start = inner.find("function askAxis(prompt)")
        end = inner.find("\n  }", inner.find("finally {", start))
        end = inner.find("\n  }", end + 1) + 4
        old_block = inner[start:end]
        print(f"  – Exact match failed, found block at {start}-{end}, length {len(old_block)}")
        print(f"  Block preview: {old_block[:200]!r}")
    else:
        print("  – JS function block not found — skipping")

# ═════════════════════════════════════════════════════════════════════════════
# CHANGE 3 — Changelog → WAR ROOM differentiators
# ═════════════════════════════════════════════════════════════════════════════
print("\nChange 3: Updating changelog to WAR ROOM differentiators...")

OLD_CHANGELOG = '''<!-- ═════════ WHAT'S NEW ═════════ -->
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
</section>'''

NEW_CHANGELOG = '''<!-- ═════════ WHY WAR ROOM ═════════ -->
<section style="background:var(--bg2);padding:56px 0 56px">
  <div class="wrap">
    <div class="sec-head">
      <div class="sec-eyebrow"><span class="lin"></span> Why operators switch</div>
      <h2 class="sec-title">Not another tool. <em style="color:var(--red);font-style:normal">A command center.</em></h2>
      <p class="sec-sub">These are the things that make operators stay — not features from a roadmap, but fundamentals baked into the architecture.</p>
    </div>
    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:16px;max-width:1280px;margin:0 auto">

      <div style="background:var(--surface);border:0.5px solid var(--border2);border-radius:14px;padding:22px 24px">
        <div style="font-size:24px;margin-bottom:10px">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="var(--green)" stroke-width="2" stroke-linecap="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
        </div>
        <div style="font-size:13px;font-weight:800;margin-bottom:6px;letter-spacing:0.02em">One file. No install.</div>
        <div style="font-size:12px;color:var(--ink2);line-height:1.6">WAR ROOM is a single HTML file. Bookmark it, email it to yourself, drop it on a USB. It opens in any browser. No app store, no account, no setup wizard. Just open and run.</div>
      </div>

      <div style="background:var(--surface);border:0.5px solid var(--border2);border-radius:14px;padding:22px 24px">
        <div style="font-size:24px;margin-bottom:10px">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="var(--blue)" stroke-width="2" stroke-linecap="round"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
        </div>
        <div style="font-size:13px;font-weight:800;margin-bottom:6px;letter-spacing:0.02em">Your data never leaves — unless you want it to.</div>
        <div style="font-size:12px;color:var(--ink2);line-height:1.6">Local-first by default. Your P&amp;L, payroll, and intel notes live in your browser. Cloud sync is opt-in — you choose the destination and hold the keys. We have no access to your data. Ever.</div>
      </div>

      <div style="background:var(--surface);border:0.5px solid var(--border2);border-radius:14px;padding:22px 24px">
        <div style="font-size:24px;margin-bottom:10px">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="var(--red)" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>
        </div>
        <div style="font-size:13px;font-weight:800;margin-bottom:6px;letter-spacing:0.02em">Multi-business from day one.</div>
        <div style="font-size:12px;color:var(--ink2);line-height:1.6">Not an add-on. Not a workspace upgrade. Every module — P&amp;L, missions, payroll, calendar — is business-aware by default. Switch contexts in one click. No context switching tax.</div>
      </div>

      <div style="background:var(--surface);border:0.5px solid var(--border2);border-radius:14px;padding:22px 24px">
        <div style="font-size:24px;margin-bottom:10px">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="var(--amber)" stroke-width="2" stroke-linecap="round"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
        </div>
        <div style="font-size:13px;font-weight:800;margin-bottom:6px;letter-spacing:0.02em">AXIS knows your whole business.</div>
        <div style="font-size:12px;color:var(--ink2);line-height:1.6">Most AI tools are blank-slate chatbots. AXIS is different — it reads your P&amp;L, missions, payroll, calendar, and intel notes before it answers. No copy-pasting context. No generic advice. Real answers from real data.</div>
      </div>

      <div style="background:var(--surface);border:0.5px solid var(--border2);border-radius:14px;padding:22px 24px">
        <div style="font-size:24px;margin-bottom:10px">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#a78bfa" stroke-width="2" stroke-linecap="round"><polygon points="23 7 16 12 23 17 23 7"/><rect x="1" y="5" width="15" height="14" rx="2" ry="2"/></svg>
        </div>
        <div style="font-size:13px;font-weight:800;margin-bottom:6px;letter-spacing:0.02em">Built-in video calls. No Zoom tax.</div>
        <div style="font-size:12px;color:var(--ink2);line-height:1.6">Client calls, team standups, partner check-ins — all inside WAR ROOM. Lobby preview, screen share (monitor, window, or browser tab), live chat, speaking detection. Cancel your Zoom subscription.</div>
      </div>

      <div style="background:var(--surface);border:0.5px solid var(--border2);border-radius:14px;padding:22px 24px">
        <div style="font-size:24px;margin-bottom:10px">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#34d399" stroke-width="2" stroke-linecap="round"><rect x="2" y="7" width="20" height="14" rx="2"/><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/></svg>
        </div>
        <div style="font-size:13px;font-weight:800;margin-bottom:6px;letter-spacing:0.02em">Payroll visibility built in.</div>
        <div style="font-size:12px;color:var(--ink2);line-height:1.6">Headcount, monthly burn, annual cost — per business, always visible. Add employees as hourly, salary, or contractor. No separate spreadsheet, no HR software subscription for a 4-person team.</div>
      </div>

    </div>
  </div>
</section>'''

if OLD_CHANGELOG in inner:
    inner = inner.replace(OLD_CHANGELOG, NEW_CHANGELOG)
    print("  ✓ Changelog replaced with WAR ROOM differentiators")
else:
    print("  – Changelog block not found exactly; trying partial search...")
    marker = "<!-- ═════════ WHAT'S NEW ═════════ -->"
    if marker in inner:
        print(f"  Found marker at {inner.find(marker)}")
    else:
        print("  – Marker not found either")

# ═════════════════════════════════════════════════════════════════════════════
# Re-encode inner HTML back into bundle
# ═════════════════════════════════════════════════════════════════════════════
print("\nRe-encoding inner HTML...")
updated_inner_json = json.dumps(inner)
updated_inner_json = updated_inner_json.replace('</script>', '<\\/script>').replace('<script', '<script')

# Replace in outer content
old_template_content = m.group(1)
content = content[:m.start(1)] + "\n" + updated_inner_json + "\n" + content[m.end(1):]

# ═════════════════════════════════════════════════════════════════════════════
# Write output
# ═════════════════════════════════════════════════════════════════════════════
print(f"Writing output to {OUT}...")
with open(OUT, "w", encoding="utf-8") as f:
    f.write(content)

size = len(content)
print(f"\n✅ Done. Output: {size:,} bytes ({size/1024:.1f} KB)")

# Verify key content
checks = ["AXIS", "askFAQ", "FAQ_ANSWERS", "whats-different", "One file. No install", "Built-in video calls"]
print("\nVerification:")
for c in checks:
    found = c in content
    print(f"  {'✓' if found else '✗'} {c!r}")
