#!/usr/bin/env python3
import json
import re

def extract_template(content):
    """Extract raw JSON string between script tags."""
    match = re.search(r'<script type="__bundler/template">(.*?)</script>', content, re.DOTALL)
    if not match:
        raise ValueError("No __bundler/template script tag found")
    return match.group(1), match.start(1), match.end(1)

def apply_replacement(html, old, new, label):
    if old in html:
        html = html.replace(old, new, 1)
        print(f"  [OK] {label}")
    else:
        print(f"  [WARNING] NOT FOUND: {label}")
    return html

# ============================================================
# CHANGE A - _hashPwd helper (both files)
# ============================================================
HASH_PWD_FUNC = """async function _hashPwd(email, pass) {
  const enc = new TextEncoder();
  const key = await crypto.subtle.importKey('raw', enc.encode(pass), 'PBKDF2', false, ['deriveBits']);
  const bits = await crypto.subtle.deriveBits(
    { name: 'PBKDF2', salt: enc.encode('wr:' + email.toLowerCase()), iterations: 150000, hash: 'SHA-256' },
    key, 256
  );
  return btoa(String.fromCharCode(...new Uint8Array(bits)));
}
"""

ESC_FUNC = "function esc(s){return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/\"/g,'&quot;').replace(/'/g,'&#39;');}"

# ============================================================
# Process index.html
# ============================================================
print("\n=== Processing index.html ===")
with open('/home/user/html-starter/index.html', 'r', encoding='utf-8') as f:
    index_content = f.read()

raw_json, start, end = extract_template(index_content)
print(f"Template JSON length: {len(raw_json)}")

decoded_html = json.loads(raw_json.strip())
print(f"Decoded HTML length: {len(decoded_html)}")

# Change A: Add _hashPwd before esc()
decoded_html = apply_replacement(
    decoded_html,
    ESC_FUNC,
    HASH_PWD_FUNC + ESC_FUNC,
    "Change A: Add _hashPwd helper"
)

# Change B: Replace handleGoogleSignIn
OLD_GOOGLE = """  function handleGoogleSignIn() {
    const btn = document.getElementById('googleSignInBtn');
    if (btn) { btn.disabled = true; btn.textContent = 'Connecting...'; }
    setTimeout(() => {
      localStorage.setItem('wr_access', '1');
      localStorage.setItem('wr_user_google', '1');
      const sucEl = document.getElementById('authSuccess');
      if (sucEl) sucEl.textContent = '✓ Google sign-in successful. Launching War Room...';
      setTimeout(() => closeAuthOverlay(), 900);
    }, 800);
  }"""

NEW_GOOGLE = """  async function handleGoogleSignIn() {
    const btn = document.getElementById('googleSignInBtn');
    const sucEl = document.getElementById('authSuccess');
    const errEl = document.getElementById('authError');
    if (btn) { btn.disabled = true; btn.textContent = 'Connecting...'; }
    if (errEl) errEl.textContent = '';
    try {
      if (!window._fbAuthApp) {
        await new Promise((res, rej) => {
          const s1 = document.createElement('script');
          s1.src = 'https://www.gstatic.com/firebasejs/10.12.0/firebase-app-compat.js';
          s1.onload = () => {
            const s2 = document.createElement('script');
            s2.src = 'https://www.gstatic.com/firebasejs/10.12.0/firebase-auth-compat.js';
            s2.onload = res; s2.onerror = rej;
            document.head.appendChild(s2);
          };
          s1.onerror = rej;
          document.head.appendChild(s1);
        });
        window._fbAuthApp = firebase.apps.length
          ? firebase.apps[0]
          : firebase.initializeApp({ apiKey: 'AIzaSyBcdKlkPBlLxs6barPZDAgoPlB9iU82Zkg', authDomain: 'createwarrom.firebaseapp.com', projectId: 'createwarrom' });
      }
      const auth = firebase.auth();
      const result = await auth.signInWithPopup(new firebase.auth.GoogleAuthProvider());
      const user = result.user;
      localStorage.setItem('wr_access', '1');
      localStorage.setItem('wr_user_google', '1');
      localStorage.setItem('wr_google_name', user.displayName || '');
      localStorage.setItem('wr_google_email', user.email || '');
      localStorage.setItem('wr_google_picture', user.photoURL || '');
      if (sucEl) sucEl.textContent = '✓ Signed in as ' + (user.email || 'Google User') + '. Launching War Room...';
      setTimeout(() => closeAuthOverlay(), 900);
    } catch (e) {
      if (btn) { btn.disabled = false; btn.textContent = 'Continue with Google'; }
      if (errEl) errEl.textContent = e.code === 'auth/popup-closed-by-user' ? 'Sign-in cancelled.' : 'Google sign-in failed. Please try again.';
    }
  }"""

decoded_html = apply_replacement(decoded_html, OLD_GOOGLE, NEW_GOOGLE, "Change B: Replace handleGoogleSignIn")

# Change C: Replace handleAuth in index.html
OLD_HANDLE_AUTH = """  function handleAuth() {
    const emailVal = (document.getElementById('authEmail').value || '').trim().toLowerCase();
    const passVal  = document.getElementById('authPassword').value || '';
    const errEl    = document.getElementById('authError');
    const sucEl    = document.getElementById('authSuccess');
    if (errEl) errEl.textContent = '';
    if (sucEl) sucEl.textContent = '';
    if (!emailVal || !passVal) { if (errEl) errEl.textContent = 'Email and password required.'; return; }
    if (!/^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/.test(emailVal)) { if (errEl) errEl.textContent = 'Enter a valid email address.'; return; }
    const ACCOUNTS_KEY = 'wr_accounts';
    const TOKEN_KEY = 'wr_access';
    let accounts = {};
    try { accounts = JSON.parse(localStorage.getItem(ACCOUNTS_KEY) || '{}'); } catch(e) {}
    if (_authMode === 'signup') {
      const confirmEl = document.getElementById('authConfirmPassword');
      const confirmVal = confirmEl ? confirmEl.value : '';
      if (passVal !== confirmVal) { if (errEl) errEl.textContent = 'Passwords do not match.'; return; }
      if (passVal.length < 6) { if (errEl) errEl.textContent = 'Password must be at least 6 characters.'; return; }
      if (accounts[emailVal]) { if (errEl) errEl.textContent = 'An account with this email already exists. Sign in instead.'; return; }
      accounts[emailVal] = { hash: btoa(unescape(encodeURIComponent(emailVal + ':' + passVal))), created: Date.now() };
      try { localStorage.setItem(ACCOUNTS_KEY, JSON.stringify(accounts)); } catch(e) {}
      localStorage.setItem(TOKEN_KEY, '1');
      localStorage.setItem('wr_user_email', emailVal);
      if (sucEl) sucEl.textContent = '✓ Account created. Welcome to War Room, Operator.';
      setTimeout(() => closeAuthOverlay(), 900);
    } else {
      const acct = accounts[emailVal];
      if (!acct) { if (errEl) errEl.textContent = 'No account found. Use "Create Account" to sign up.'; return; }
      const hash = btoa(unescape(encodeURIComponent(emailVal + ':' + passVal)));
      if (hash !== acct.hash) { if (errEl) errEl.textContent = 'Incorrect password. Please try again.'; return; }
      localStorage.setItem(TOKEN_KEY, '1');
      localStorage.setItem('wr_user_email', emailVal);
      if (sucEl) sucEl.textContent = '✓ Access granted. Welcome back, Operator.';
      setTimeout(() => closeAuthOverlay(), 900);
    }
  }"""

NEW_HANDLE_AUTH = """  async function handleAuth() {
    const emailVal = (document.getElementById('authEmail').value || '').trim().toLowerCase();
    const passVal  = document.getElementById('authPassword').value || '';
    const errEl    = document.getElementById('authError');
    const sucEl    = document.getElementById('authSuccess');
    if (errEl) errEl.textContent = '';
    if (sucEl) sucEl.textContent = '';
    if (!emailVal || !passVal) { if (errEl) errEl.textContent = 'Email and password required.'; return; }
    if (!/^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/.test(emailVal)) { if (errEl) errEl.textContent = 'Enter a valid email address.'; return; }
    const ACCOUNTS_KEY = 'wr_accounts';
    const TOKEN_KEY = 'wr_access';
    let accounts = {};
    try { accounts = JSON.parse(localStorage.getItem(ACCOUNTS_KEY) || '{}'); } catch(e) {}
    if (_authMode === 'signup') {
      const confirmEl = document.getElementById('authConfirmPassword');
      const confirmVal = confirmEl ? confirmEl.value : '';
      if (passVal !== confirmVal) { if (errEl) errEl.textContent = 'Passwords do not match.'; return; }
      if (passVal.length < 6) { if (errEl) errEl.textContent = 'Password must be at least 6 characters.'; return; }
      if (accounts[emailVal]) { if (errEl) errEl.textContent = 'An account with this email already exists. Sign in instead.'; return; }
      const hash = await _hashPwd(emailVal, passVal);
      accounts[emailVal] = { hash, created: Date.now() };
      try { localStorage.setItem(ACCOUNTS_KEY, JSON.stringify(accounts)); } catch(e) {}
      localStorage.setItem(TOKEN_KEY, '1');
      localStorage.setItem('wr_user_email', emailVal);
      if (sucEl) sucEl.textContent = '✓ Account created. Welcome to War Room, Operator.';
      setTimeout(() => closeAuthOverlay(), 900);
    } else {
      const acct = accounts[emailVal];
      if (!acct) { if (errEl) errEl.textContent = 'No account found. Use "Create Account" to sign up.'; return; }
      const hash = await _hashPwd(emailVal, passVal);
      if (hash !== acct.hash) { if (errEl) errEl.textContent = 'Incorrect password. Please try again.'; return; }
      localStorage.setItem(TOKEN_KEY, '1');
      localStorage.setItem('wr_user_email', emailVal);
      if (sucEl) sucEl.textContent = '✓ Access granted. Welcome back, Operator.';
      setTimeout(() => closeAuthOverlay(), 900);
    }
  }"""

decoded_html = apply_replacement(decoded_html, OLD_HANDLE_AUTH, NEW_HANDLE_AUTH, "Change C: Replace handleAuth (async + PBKDF2)")

# Change D: Update handleAuthSubmit
OLD_SUBMIT = """  function handleAuthSubmit() {
    if (_authMode === 'forgot') { handleForgotPassword(); return; }
    if (_authMode === 'reset') { handleResetPassword(); return; }
    handleAuth();
  }"""

NEW_SUBMIT = """  async function handleAuthSubmit() {
    if (_authMode === 'forgot') { handleForgotPassword(); return; }
    if (_authMode === 'reset') { await handleResetPassword(); return; }
    await handleAuth();
  }"""

decoded_html = apply_replacement(decoded_html, OLD_SUBMIT, NEW_SUBMIT, "Change D: Update handleAuthSubmit to await")

# Change E: Update handleResetPassword - function signature
decoded_html = apply_replacement(
    decoded_html,
    "  function handleResetPassword() {",
    "  async function handleResetPassword() {",
    "Change E1: Make handleResetPassword async"
)

# Change E: Update handleResetPassword - hash line
OLD_RESET_HASH = """    accounts[email].hash = btoa(unescape(encodeURIComponent(email + ':' + newPass)));
    try { localStorage.setItem('wr_accounts', JSON.stringify(accounts)); } catch(e) {}
    sessionStorage.removeItem('wr_reset_email');
    if (sucEl) sucEl.textContent = '✓ Password updated. Sign in with your new password.';
    setTimeout(() => setAuthMode('signin'), 1600);
  }"""

NEW_RESET_HASH = """    accounts[email].hash = await _hashPwd(email, newPass);
    try { localStorage.setItem('wr_accounts', JSON.stringify(accounts)); } catch(e) {}
    sessionStorage.removeItem('wr_reset_email');
    if (sucEl) sucEl.textContent = '✓ Password updated. Sign in with your new password.';
    setTimeout(() => setAuthMode('signin'), 1600);
  }"""

decoded_html = apply_replacement(decoded_html, OLD_RESET_HASH, NEW_RESET_HASH, "Change E2: Update handleResetPassword hash to PBKDF2")

# Re-encode and write
new_json = json.dumps(decoded_html)
new_template_block = "\n" + new_json + "\n  "

new_index_content = index_content[:start] + new_template_block + index_content[end:]

# Verify
raw_json2, _, _ = extract_template(new_index_content)
json.loads(raw_json2.strip())
print("  [OK] Verification: template JSON parses cleanly")

with open('/home/user/html-starter/index.html', 'w', encoding='utf-8') as f:
    f.write(new_index_content)
print("  [OK] index.html written")

# ============================================================
# Process app.html
# ============================================================
print("\n=== Processing app.html ===")
with open('/home/user/html-starter/app.html', 'r', encoding='utf-8') as f:
    app_content = f.read()

raw_json, start, end = extract_template(app_content)
print(f"Template JSON length: {len(raw_json)}")

decoded_html = json.loads(raw_json.strip())
print(f"Decoded HTML length: {len(decoded_html)}")

# Change A: Add _hashPwd before esc()
decoded_html = apply_replacement(
    decoded_html,
    ESC_FUNC,
    HASH_PWD_FUNC + ESC_FUNC,
    "Change A: Add _hashPwd helper"
)

# Change F: Update handleAuth in app.html
OLD_APP_HANDLE_AUTH = """function handleAuth(){
  const emailVal=(document.getElementById('authEmail').value||'').trim().toLowerCase();
  const passVal=document.getElementById('authPassword').value||'';
  const errEl=document.getElementById('authError');
  const sucEl=document.getElementById('authSuccess');
  if(errEl)errEl.textContent='';
  if(sucEl)sucEl.textContent='';
  if(!emailVal||!passVal){if(errEl)errEl.textContent='Email and password required.';return;}
  if(!/^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/.test(emailVal)){if(errEl)errEl.textContent='Enter a valid email address.';return;}
  const ACCOUNTS_KEY='wr_accounts';
  const TOKEN_KEY='wr_access';
  let accounts={};
  try{accounts=JSON.parse(localStorage.getItem(ACCOUNTS_KEY)||'{}');}catch(e){}
  if(authMode==='signup'){
    const confirmEl=document.getElementById('authConfirmPassword');
    const confirmVal=confirmEl?confirmEl.value:'';
    if(passVal!==confirmVal){if(errEl)errEl.textContent='Passwords do not match.';return;}
    if(passVal.length<6){if(errEl)errEl.textContent='Password must be at least 6 characters.';return;}
    if(accounts[emailVal]){if(errEl)errEl.textContent='An account with this email already exists. Sign in instead.';return;}
    accounts[emailVal]={hash:btoa(unescape(encodeURIComponent(emailVal+':'+passVal))),created:Date.now()};
    try{localStorage.setItem(ACCOUNTS_KEY,JSON.stringify(accounts));}catch(e){}
    localStorage.setItem(TOKEN_KEY,'1');
    localStorage.setItem('wr_user_email',emailVal);
    if(sucEl)sucEl.textContent='✓ Account created. Welcome to War Room, Operator.';
    setTimeout(()=>closeAppAuthOverlay(),900);
  } else {
    const acct=accounts[emailVal];
    if(!acct){if(errEl)errEl.textContent='No account found. Use "Create Account" to sign up.';return;}
    const hash=btoa(unescape(encodeURIComponent(emailVal+':'+passVal)));
    if(hash!==acct.hash){if(errEl)errEl.textContent='Incorrect password. Please try again.';return;}
    localStorage.setItem(TOKEN_KEY,'1');
    localStorage.setItem('wr_user_email',emailVal);
    if(sucEl)sucEl.textContent='✓ Access granted. Welcome back, Operator.';
    setTimeout(()=>closeAppAuthOverlay(),900);
  }
}"""

NEW_APP_HANDLE_AUTH = """async function handleAuth(){
  const emailVal=(document.getElementById('authEmail').value||'').trim().toLowerCase();
  const passVal=document.getElementById('authPassword').value||'';
  const errEl=document.getElementById('authError');
  const sucEl=document.getElementById('authSuccess');
  if(errEl)errEl.textContent='';
  if(sucEl)sucEl.textContent='';
  if(!emailVal||!passVal){if(errEl)errEl.textContent='Email and password required.';return;}
  if(!/^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/.test(emailVal)){if(errEl)errEl.textContent='Enter a valid email address.';return;}
  const ACCOUNTS_KEY='wr_accounts';
  const TOKEN_KEY='wr_access';
  let accounts={};
  try{accounts=JSON.parse(localStorage.getItem(ACCOUNTS_KEY)||'{}');}catch(e){}
  if(authMode==='signup'){
    const confirmEl=document.getElementById('authConfirmPassword');
    const confirmVal=confirmEl?confirmEl.value:'';
    if(passVal!==confirmVal){if(errEl)errEl.textContent='Passwords do not match.';return;}
    if(passVal.length<6){if(errEl)errEl.textContent='Password must be at least 6 characters.';return;}
    if(accounts[emailVal]){if(errEl)errEl.textContent='An account with this email already exists. Sign in instead.';return;}
    const hash=await _hashPwd(emailVal,passVal);
    accounts[emailVal]={hash,created:Date.now()};
    try{localStorage.setItem(ACCOUNTS_KEY,JSON.stringify(accounts));}catch(e){}
    localStorage.setItem(TOKEN_KEY,'1');
    localStorage.setItem('wr_user_email',emailVal);
    if(sucEl)sucEl.textContent='✓ Account created. Welcome to War Room, Operator.';
    setTimeout(()=>closeAppAuthOverlay(),900);
  } else {
    const acct=accounts[emailVal];
    if(!acct){if(errEl)errEl.textContent='No account found. Use "Create Account" to sign up.';return;}
    const hash=await _hashPwd(emailVal,passVal);
    if(hash!==acct.hash){if(errEl)errEl.textContent='Incorrect password. Please try again.';return;}
    localStorage.setItem(TOKEN_KEY,'1');
    localStorage.setItem('wr_user_email',emailVal);
    if(sucEl)sucEl.textContent='✓ Access granted. Welcome back, Operator.';
    setTimeout(()=>closeAppAuthOverlay(),900);
  }
}"""

decoded_html = apply_replacement(decoded_html, OLD_APP_HANDLE_AUTH, NEW_APP_HANDLE_AUTH, "Change F: Replace handleAuth (async + PBKDF2)")

# Change G: Update handleAuthSubmit in app.html
OLD_APP_SUBMIT = """async function handleAuthSubmit(){
  if(authMode==='forgot'){handleForgotPassword();return;}
  if(authMode==='reset'){handleResetPassword();return;}
  handleAuth();
}"""

NEW_APP_SUBMIT = """async function handleAuthSubmit(){
  if(authMode==='forgot'){handleForgotPassword();return;}
  if(authMode==='reset'){await handleResetPassword();return;}
  await handleAuth();
}"""

decoded_html = apply_replacement(decoded_html, OLD_APP_SUBMIT, NEW_APP_SUBMIT, "Change G: Update handleAuthSubmit to await")

# Change H: Update handleResetPassword in app.html - signature
decoded_html = apply_replacement(
    decoded_html,
    "function handleResetPassword(){",
    "async function handleResetPassword(){",
    "Change H1: Make handleResetPassword async"
)

# Change H: Update handleResetPassword in app.html - hash line
OLD_APP_RESET_HASH = """  accounts[email].hash=btoa(unescape(encodeURIComponent(email+':'+newPass)));
  try{localStorage.setItem('wr_accounts',JSON.stringify(accounts));}catch(e){}
  sessionStorage.removeItem('wr_reset_email');
  if(sucEl)sucEl.textContent='✓ Password updated. Sign in with your new password.';
  setTimeout(()=>setAuthMode('signin'),1600);
}"""

NEW_APP_RESET_HASH = """  accounts[email].hash=await _hashPwd(email,newPass);
  try{localStorage.setItem('wr_accounts',JSON.stringify(accounts));}catch(e){}
  sessionStorage.removeItem('wr_reset_email');
  if(sucEl)sucEl.textContent='✓ Password updated. Sign in with your new password.';
  setTimeout(()=>setAuthMode('signin'),1600);
}"""

decoded_html = apply_replacement(decoded_html, OLD_APP_RESET_HASH, NEW_APP_RESET_HASH, "Change H2: Update handleResetPassword hash to PBKDF2")

# Re-encode and write
new_json = json.dumps(decoded_html)
new_template_block = "\n" + new_json + "\n  "

new_app_content = app_content[:start] + new_template_block + app_content[end:]

# Verify
raw_json2, _, _ = extract_template(new_app_content)
json.loads(raw_json2.strip())
print("  [OK] Verification: template JSON parses cleanly")

with open('/home/user/html-starter/app.html', 'w', encoding='utf-8') as f:
    f.write(new_app_content)
print("  [OK] app.html written")

print("\n=== All done ===")
