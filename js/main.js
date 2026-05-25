// ============================================================
// MOMENT STUDIO — main.js
// ============================================================

// --- Announcement bar dismiss ---
function initAnnouncementBar() {
  if (sessionStorage.getItem('annDismissed')) {
    const bar = document.getElementById('announcementBar');
    if (bar) bar.style.display = 'none';
  }
}
function dismissAnnouncement() {
  const bar = document.getElementById('announcementBar');
  if (bar) { bar.style.display = 'none'; sessionStorage.setItem('annDismissed', '1'); }
}

// --- Scroll-triggered fade-in ---
function initScrollFade() {
  const observer = new IntersectionObserver(entries => {
    entries.forEach(e => { if (e.isIntersecting) e.target.classList.add('visible'); });
  }, { threshold: 0.1, rootMargin: '0px 0px -48px 0px' });
  document.querySelectorAll('.scroll-fade').forEach(el => observer.observe(el));
}

// --- Animated counters ---
function animateCounter(el) {
  const target = parseInt(el.dataset.count, 10);
  const suffix = el.hasAttribute('data-suffix') ? el.dataset.suffix : '+';
  const dur = 1800;
  const step = target / (dur / 16);
  let cur = 0;
  const tick = setInterval(() => {
    cur += step;
    if (cur >= target) { cur = target; clearInterval(tick); }
    el.textContent = Math.floor(cur) + suffix;
  }, 16);
}
function initCounters() {
  const observer = new IntersectionObserver(entries => {
    entries.forEach(e => {
      if (e.isIntersecting) { animateCounter(e.target); observer.unobserve(e.target); }
    });
  }, { threshold: 0.6 });
  document.querySelectorAll('[data-count]').forEach(el => observer.observe(el));
}

// --- Mobile nav ---
function initMobileNav() {
  const toggle = document.getElementById('navToggle');
  const mobileNav = document.getElementById('mobileNav');
  if (!toggle || !mobileNav) return;
  toggle.addEventListener('click', () => {
    const open = toggle.classList.toggle('open');
    mobileNav.classList.toggle('open', open);
    document.body.style.overflow = open ? 'hidden' : '';
  });
  mobileNav.querySelectorAll('a').forEach(link => {
    link.addEventListener('click', () => {
      toggle.classList.remove('open');
      mobileNav.classList.remove('open');
      document.body.style.overflow = '';
    });
  });
}

// --- Floating CTA + back-to-top ---
function initScrollUI() {
  const cta = document.getElementById('floatingCta');
  const top = document.getElementById('backToTop');
  const onScroll = () => {
    const show = window.scrollY > 440;
    if (cta) cta.classList.toggle('visible', show);
    if (top) top.classList.toggle('visible', show);
  };
  window.addEventListener('scroll', onScroll, { passive: true });
  if (top) top.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));
}

// --- FAQ accordion ---
function initFaq() {
  document.querySelectorAll('.faq-item').forEach(item => {
    const btn = item.querySelector('.faq-q-btn');
    const body = item.querySelector('.faq-body');
    if (!btn || !body) return;
    btn.addEventListener('click', () => {
      const isOpen = item.classList.contains('open');
      document.querySelectorAll('.faq-item.open').forEach(o => {
        o.classList.remove('open');
        o.querySelector('.faq-body').style.maxHeight = '0';
      });
      if (!isOpen) {
        item.classList.add('open');
        body.style.maxHeight = body.scrollHeight + 'px';
      }
    });
  });
}

// --- Package tab switching (home + packages preview) ---
function switchTab(tab, el) {
  document.querySelectorAll('.pkg-tab').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.pkg-panel').forEach(p => p.classList.remove('active'));
  el.classList.add('active');
  document.getElementById('tab-' + tab).classList.add('active');
}

// --- Inquiry modal ---
function openInquiry(pkgName) {
  const modal = document.getElementById('inquiryModal');
  const label = document.getElementById('modalPkgLabel');
  if (!modal) return;
  if (label) label.textContent = 'Package: ' + pkgName;
  modal.classList.add('open');
  document.body.style.overflow = 'hidden';
}
function closeInquiry() {
  const modal = document.getElementById('inquiryModal');
  if (!modal) return;
  modal.classList.remove('open');
  document.body.style.overflow = '';
}
function overlayClose(e) {
  if (e.target === document.getElementById('inquiryModal')) closeInquiry();
}

// --- Modal form submit ---
function submitModal(e) {
  e.preventDefault();
  const form = document.getElementById('modalForm');
  const success = document.getElementById('modalSuccess');
  if (form) form.style.display = 'none';
  if (success) success.style.display = 'block';
}

// --- Contact form ---
function handleSubmit(e) {
  e.preventDefault();
  e.target.style.display = 'none';
  const msg = document.getElementById('formSuccess');
  if (msg) { msg.style.display = 'block'; msg.scrollIntoView({ behavior: 'smooth', block: 'center' }); }
}

// --- Init ---
document.addEventListener('DOMContentLoaded', () => {
  initAnnouncementBar();
  initScrollFade();
  initCounters();
  initMobileNav();
  initScrollUI();
  initFaq();
});
