#!/usr/bin/env python3
import json
import re
import sys

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


def extract_template(file_content):
    """Extract the raw JSON string from between script tags."""
    pattern = r'(<script type="__bundler/template">)(.*?)(</script>)'
    match = re.search(pattern, file_content, re.DOTALL)
    if not match:
        raise ValueError("Could not find <script type=\"__bundler/template\"> tag")
    return match.group(1), match.group(2), match.group(3)


def replace_in_html(html, old, new, label):
    if old in html:
        html = html.replace(old, new)
        print(f"  [OK] {label}")
    else:
        print(f"  [WARNING] Not found: {label}")
    return html


def process_file(filepath, changes_fn):
    print(f"\nProcessing: {filepath}")
    with open(filepath, 'r', encoding='utf-8') as f:
        file_content = f.read()

    open_tag, raw_json_str, close_tag = extract_template(file_content)

    # JSON.parse the template
    decoded_html = json.loads(raw_json_str.strip())
    print(f"  Template decoded successfully ({len(decoded_html)} chars)")

    # Apply changes
    decoded_html = changes_fn(decoded_html)

    # Re-encode
    new_json_str = json.dumps(decoded_html)

    # Verify it can be parsed back
    test = json.loads(new_json_str)
    assert test == decoded_html, "Round-trip verification failed!"
    print(f"  Round-trip verification passed")

    # Reconstruct file with original whitespace pattern: \n + json_string + \n
    new_script_content = '\n' + new_json_str + '\n  '
    new_file_content = file_content.replace(
        open_tag + raw_json_str + close_tag,
        open_tag + new_script_content + close_tag
    )

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_file_content)
    print(f"  File written successfully")

    # Final verification
    with open(filepath, 'r', encoding='utf-8') as f:
        verify_content = f.read()
    _, verify_raw, _ = extract_template(verify_content)
    verify_decoded = json.loads(verify_raw.strip())
    assert verify_decoded == decoded_html, "Final verification failed!"
    print(f"  Final verification passed")


def changes_both(html):
    """Changes A - applied to both files."""
    # Change A: Add _hashPwd async helper before esc function
    html = replace_in_html(
        html,
        ESC_FUNC,
        HASH_PWD_FUNC + ESC_FUNC,
        "Change A: Add _hashPwd helper"
    )
    return html


def changes_index(html):
    """Changes B, C, D, E - applied to index.html only."""
    html = changes_both(html)

    # Change B: Replace handleGoogleSignIn
    old_google = """  function handleGoogleSignIn() {
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

    new_google = """  async function handleGoogleSignIn() {
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

    html = replace_in_html(html, old_google, new_google, "Change B: Replace handleGoogleSignIn")

    # Change C: Replace handleAuth in index.html
    old_handle_auth = """  function handleAuth() {
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

    new_handle_auth = """  async function handleAuth() {
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

    html = replace_in_html(html, old_handle_auth, new_handle_auth, "Change C: Replace handleAuth (async+PBKDF2)")

    # Change D: Update handleAuthSubmit
    old_auth_submit = """  function handleAuthSubmit() {
    if (_authMode === 'forgot') { handleForgotPassword(); return; }
    if (_authMode === 'reset') { handleResetPassword(); return; }
    handleAuth();
  }"""

    new_auth_submit = """  async function handleAuthSubmit() {
    if (_authMode === 'forgot') { handleForgotPassword(); return; }
    if (_authMode === 'reset') { await handleResetPassword(); return; }
    await handleAuth();
  }"""

    html = replace_in_html(html, old_auth_submit, new_auth_submit, "Change D: Update handleAuthSubmit")

    # Change E: Update handleResetPassword signature
    html = replace_in_html(
        html,
        "  function handleResetPassword() {",
        "  async function handleResetPassword() {",
        "Change E: Update handleResetPassword signature"
    )

    # Change E: Update handleResetPassword body
    old_reset_body = """    accounts[email].hash = btoa(unescape(encodeURIComponent(email + ':' + newPass)));
    try { localStorage.setItem('wr_accounts', JSON.stringify(accounts)); } catch(e) {}
    sessionStorage.removeItem('wr_reset_email');
    if (sucEl) sucEl.textContent = '✓ Password updated. Sign in with your new password.';
    setTimeout(() => setAuthMode('signin'), 1600);
  }"""

    new_reset_body = """    accounts[email].hash = await _hashPwd(email, newPass);
    try { localStorage.setItem('wr_accounts', JSON.stringify(accounts)); } catch(e) {}
    sessionStorage.removeItem('wr_reset_email');
    if (sucEl) sucEl.textContent = '✓ Password updated. Sign in with your new password.';
    setTimeout(() => setAuthMode('signin'), 1600);
  }"""

    html = replace_in_html(html, old_reset_body, new_reset_body, "Change E: Update handleResetPassword body")

    return html


def changes_app(html):
    """Changes F, G, H - applied to app.html only."""
    html = changes_both(html)

    # Change F: Replace handleAuth in app.html
    old_handle_auth = """function handleAuth(){
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

    new_handle_auth = """async function handleAuth(){
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

    html = replace_in_html(html, old_handle_auth, new_handle_auth, "Change F: Replace handleAuth (async+PBKDF2)")

    # Change G: Update handleAuthSubmit in app.html
    old_auth_submit = """async function handleAuthSubmit(){
  if(authMode==='forgot'){handleForgotPassword();return;}
  if(authMode==='reset'){handleResetPassword();return;}
  handleAuth();
}"""

    new_auth_submit = """async function handleAuthSubmit(){
  if(authMode==='forgot'){handleForgotPassword();return;}
  if(authMode==='reset'){await handleResetPassword();return;}
  await handleAuth();
}"""

    html = replace_in_html(html, old_auth_submit, new_auth_submit, "Change G: Update handleAuthSubmit")

    # Change H: Update handleResetPassword signature in app.html
    html = replace_in_html(
        html,
        "function handleResetPassword(){",
        "async function handleResetPassword(){",
        "Change H: Update handleResetPassword signature"
    )

    # Change H: Update handleResetPassword body in app.html
    old_reset_body = """  accounts[email].hash=btoa(unescape(encodeURIComponent(email+':'+newPass)));
  try{localStorage.setItem('wr_accounts',JSON.stringify(accounts));}catch(e){}
  sessionStorage.removeItem('wr_reset_email');
  if(sucEl)sucEl.textContent='✓ Password updated. Sign in with your new password.';
  setTimeout(()=>setAuthMode('signin'),1600);
}"""

    new_reset_body = """  accounts[email].hash=await _hashPwd(email,newPass);
  try{localStorage.setItem('wr_accounts',JSON.stringify(accounts));}catch(e){}
  sessionStorage.removeItem('wr_reset_email');
  if(sucEl)sucEl.textContent='✓ Password updated. Sign in with your new password.';
  setTimeout(()=>setAuthMode('signin'),1600);
}"""

    html = replace_in_html(html, old_reset_body, new_reset_body, "Change H: Update handleResetPassword body")

    return html


# Process both files
process_file('/home/user/html-starter/index.html', changes_index)
process_file('/home/user/html-starter/app.html', changes_app)

print("\nAll done!")
