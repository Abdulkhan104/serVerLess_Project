"""
FRONTEND LAMBDA
===============
This Lambda serves HTML directly — no S3 needed.
Connect it to API Gateway with routes:
  GET  /         → index page (dashboard)
  GET  /success  → success confirmation page

API Gateway setup for this Lambda:
  - Method: GET
  - Integration: Lambda Proxy
  - Resource paths: / and /success
"""

import json
import urllib.parse

# ═══════════════════════════════════════════════
#  CONFIGURATION  ← set your Backend API URL here
# ═══════════════════════════════════════════════
BACKEND_API_URL = 'https://YOUR_API_ID.execute-api.us-east-1.amazonaws.com/prod'
# ↑ Replace with your actual Backend API Gateway Invoke URL


# ═══════════════════════════════════════════════
#  MAIN HANDLER
# ═══════════════════════════════════════════════
def lambda_handler(event, context):
    path   = event.get('path', '/')
    method = event.get('httpMethod', 'GET')
    qsp    = event.get('queryStringParameters') or {}

    if method == 'OPTIONS':
        return cors_resp()

    if path == '/' or path == '/index':
        return html_resp(render_index())

    if path == '/success':
        return html_resp(render_success(qsp))

    return html_resp(render_404(), 404)


def cors_resp():
    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Origin':  '*',
            'Access-Control-Allow-Methods': 'GET,OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type',
        },
        'body': ''
    }

def html_resp(html, status=200):
    return {
        'statusCode': status,
        'headers': {
            'Content-Type':                 'text/html; charset=utf-8',
            'Access-Control-Allow-Origin':  '*',
            'X-Content-Type-Options':       'nosniff',
        },
        'body': html
    }


# ═══════════════════════════════════════════════
#  PAGE: INDEX  (Dashboard)
# ═══════════════════════════════════════════════
def render_index():
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>NexusDB — User Management</title>
<link rel="preconnect" href="https://fonts.googleapis.com"/>
<link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Outfit:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet"/>
<style>
/* ── TOKENS ─────────────────────────────────── */
:root{{
  --ink:     #0d0d14;
  --paper:   #f5f4f0;
  --cream:   #ede9e0;
  --amber:   #e8a020;
  --amber2:  #f5c842;
  --rust:    #c94a2c;
  --teal:    #1a7a6e;
  --teal2:   #24a896;
  --slate:   #3a3a4a;
  --muted:   #8a8a9a;
  --line:    #d8d4cc;
  --card:    #ffffff;
  --shadow:  0 2px 20px rgba(13,13,20,0.08);
  --shadow2: 0 8px 40px rgba(13,13,20,0.14);
  --r:       10px;
  --font-display: 'Bebas Neue', sans-serif;
  --font-body:    'Outfit', sans-serif;
  --font-mono:    'JetBrains Mono', monospace;
}}
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
html{{scroll-behavior:smooth}}
body{{
  background:var(--paper);
  color:var(--ink);
  font-family:var(--font-body);
  font-size:15px;
  line-height:1.6;
  min-height:100vh;
}}

/* ── NOISE TEXTURE ──────────────────────────── */
body::after{{
  content:'';position:fixed;inset:0;
  background-image:url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.03'/%3E%3C/svg%3E");
  pointer-events:none;z-index:9999;opacity:0.6;
}}

/* ── HEADER ─────────────────────────────────── */
header{{
  background:var(--ink);
  color:var(--paper);
  padding:0 40px;
  display:flex;align-items:center;justify-content:space-between;
  height:64px;
  position:sticky;top:0;z-index:100;
}}
.logo{{
  font-family:var(--font-display);
  font-size:2rem;letter-spacing:2px;
  color:var(--amber);
  line-height:1;
}}
.logo em{{color:var(--paper);font-style:normal}}
.header-right{{
  display:flex;align-items:center;gap:20px;
  font-family:var(--font-mono);font-size:0.72rem;
  color:rgba(245,244,240,0.5);
}}
.live-dot{{
  width:7px;height:7px;border-radius:50%;
  background:var(--teal2);
  box-shadow:0 0 8px var(--teal2);
  animation:blink 2s infinite;
}}
@keyframes blink{{0%,100%{{opacity:1}}50%{{opacity:0.3}}}}

/* ── SIDEBAR + CONTENT LAYOUT ───────────────── */
.shell{{display:flex;min-height:calc(100vh - 64px)}}
aside{{
  width:240px;flex-shrink:0;
  background:var(--ink);
  padding:32px 0;
  position:sticky;top:64px;height:calc(100vh - 64px);overflow-y:auto;
}}
.nav-label{{
  font-family:var(--font-mono);
  font-size:0.6rem;letter-spacing:3px;text-transform:uppercase;
  color:rgba(245,244,240,0.3);
  padding:0 24px;margin-bottom:10px;margin-top:28px;
}}
.nav-label:first-child{{margin-top:0}}
.nav-item{{
  display:flex;align-items:center;gap:12px;
  padding:11px 24px;
  color:rgba(245,244,240,0.55);
  font-size:0.875rem;font-weight:500;
  cursor:pointer;
  border-left:3px solid transparent;
  transition:all 0.18s;
  user-select:none;
}}
.nav-item:hover{{color:var(--paper);background:rgba(245,244,240,0.05)}}
.nav-item.active{{
  color:var(--amber);
  border-left-color:var(--amber);
  background:rgba(232,160,32,0.08);
}}
.nav-icon{{font-size:1rem;width:20px;text-align:center}}
.method-tag{{
  margin-left:auto;
  font-family:var(--font-mono);font-size:0.6rem;
  padding:2px 6px;border-radius:4px;
  font-weight:500;
}}
.tag-get   {{background:rgba(26,122,110,0.3);color:var(--teal2)}}
.tag-post  {{background:rgba(232,160,32,0.25);color:var(--amber2)}}
.tag-put   {{background:rgba(90,90,180,0.25);color:#a0a0ff}}
.tag-delete{{background:rgba(201,74,44,0.25);color:#ff8070}}

/* ── MAIN CONTENT ───────────────────────────── */
main{{flex:1;padding:36px 40px;max-width:900px}}

/* ── PAGE TITLE ─────────────────────────────── */
.page-title{{
  font-family:var(--font-display);
  font-size:3.2rem;letter-spacing:1px;
  color:var(--ink);line-height:1;
  margin-bottom:6px;
}}
.page-sub{{
  font-size:0.85rem;color:var(--muted);
  margin-bottom:36px;
  font-family:var(--font-mono);
}}

/* ── CARDS ──────────────────────────────────── */
.card{{
  background:var(--card);
  border:1px solid var(--line);
  border-radius:var(--r);
  padding:28px 32px;
  margin-bottom:24px;
  box-shadow:var(--shadow);
  display:none;
  animation:fadeUp 0.3s ease forwards;
}}
.card.visible{{display:block}}
@keyframes fadeUp{{
  from{{opacity:0;transform:translateY(12px)}}
  to  {{opacity:1;transform:translateY(0)}}
}}
.card-header{{
  display:flex;align-items:center;gap:14px;
  margin-bottom:24px;
  padding-bottom:16px;
  border-bottom:1px solid var(--line);
}}
.method-pill{{
  font-family:var(--font-mono);
  font-size:0.72rem;font-weight:500;
  padding:4px 12px;border-radius:6px;
  text-transform:uppercase;letter-spacing:1px;
}}
.pill-get   {{background:#dcfff5;color:var(--teal)}}
.pill-post  {{background:#fff4d6;color:#a06000}}
.pill-put   {{background:#ebebff;color:#4040c0}}
.pill-delete{{background:#ffe8e4;color:var(--rust)}}
.card-title{{
  font-family:var(--font-display);
  font-size:1.5rem;letter-spacing:1px;
  color:var(--ink);
}}
.endpoint-badge{{
  margin-left:auto;
  font-family:var(--font-mono);
  font-size:0.72rem;color:var(--muted);
  background:var(--cream);
  padding:4px 12px;border-radius:20px;
  border:1px solid var(--line);
}}

/* ── FORM ───────────────────────────────────── */
.form-grid{{
  display:grid;grid-template-columns:1fr 1fr;gap:14px;
  margin-bottom:20px;
}}
.fg{{display:flex;flex-direction:column;gap:5px}}
.fg.span2{{grid-column:1/-1}}
.fg label{{
  font-size:0.68rem;font-weight:600;
  letter-spacing:1.5px;text-transform:uppercase;
  color:var(--slate);
}}
.fg input,.fg select{{
  background:var(--paper);
  border:1.5px solid var(--line);
  color:var(--ink);
  font-family:var(--font-body);
  font-size:0.9rem;
  padding:9px 13px;
  border-radius:7px;
  transition:border-color 0.2s,box-shadow 0.2s;
  outline:none;
}}
.fg input:focus,.fg select:focus{{
  border-color:var(--amber);
  box-shadow:0 0 0 3px rgba(232,160,32,0.15);
}}
.fg select option{{background:white}}

/* ── BUTTONS ────────────────────────────────── */
.btn-row{{display:flex;gap:10px;flex-wrap:wrap}}
.btn{{
  font-family:var(--font-body);
  font-size:0.85rem;font-weight:600;
  padding:10px 22px;
  border-radius:7px;
  border:none;cursor:pointer;
  display:inline-flex;align-items:center;gap:8px;
  transition:all 0.18s;
  letter-spacing:0.3px;
}}
.btn:active{{transform:scale(0.97)}}
.btn:disabled{{opacity:0.45;cursor:not-allowed}}
.btn-amber{{
  background:var(--amber);color:var(--ink);
  box-shadow:0 3px 12px rgba(232,160,32,0.35);
}}
.btn-amber:hover{{background:var(--amber2);box-shadow:0 5px 20px rgba(232,160,32,0.5)}}
.btn-teal{{
  background:var(--teal);color:white;
  box-shadow:0 3px 12px rgba(26,122,110,0.3);
}}
.btn-teal:hover{{background:var(--teal2)}}
.btn-rust{{
  background:transparent;color:var(--rust);
  border:1.5px solid var(--rust);
}}
.btn-rust:hover{{background:rgba(201,74,44,0.08)}}
.btn-ghost{{
  background:transparent;color:var(--muted);
  border:1.5px solid var(--line);
}}
.btn-ghost:hover{{color:var(--ink);border-color:var(--muted)}}
.btn-purple{{
  background:transparent;color:#5050c0;
  border:1.5px solid #c0c0ff;
}}
.btn-purple:hover{{background:rgba(80,80,192,0.07)}}

/* ── ID BAR ─────────────────────────────────── */
.id-bar{{
  display:flex;gap:10px;align-items:center;
  margin-bottom:18px;
}}
.id-bar input{{
  flex:1;
  background:var(--paper);border:1.5px solid var(--line);
  color:var(--ink);font-family:var(--font-mono);
  font-size:0.82rem;padding:9px 13px;border-radius:7px;
  outline:none;transition:border-color 0.2s;
}}
.id-bar input:focus{{border-color:var(--amber)}}

/* ── RESPONSE ───────────────────────────────── */
.resp-box{{
  background:var(--ink);color:#a0ffd8;
  font-family:var(--font-mono);font-size:0.76rem;
  border-radius:8px;padding:16px 20px;
  margin-top:16px;max-height:200px;overflow-y:auto;
  white-space:pre-wrap;word-break:break-all;
  display:none;line-height:1.6;
}}
.resp-box.on{{display:block}}

/* ── TABLE ──────────────────────────────────── */
.tbl-wrap{{overflow-x:auto;border-radius:8px;border:1px solid var(--line)}}
table{{width:100%;border-collapse:collapse;font-size:0.83rem}}
thead th{{
  background:var(--cream);color:var(--slate);
  font-size:0.65rem;letter-spacing:2px;text-transform:uppercase;
  padding:11px 14px;text-align:left;font-weight:600;
  border-bottom:1px solid var(--line);
}}
tbody tr{{border-bottom:1px solid rgba(216,212,204,0.5);transition:background 0.12s}}
tbody tr:hover{{background:rgba(232,160,32,0.04)}}
tbody td{{padding:11px 14px;vertical-align:middle}}
.id-short{{
  font-family:var(--font-mono);font-size:0.68rem;
  color:var(--muted);max-width:100px;
  overflow:hidden;text-overflow:ellipsis;white-space:nowrap;
}}
.role-tag{{
  display:inline-block;padding:2px 9px;border-radius:20px;
  font-size:0.68rem;letter-spacing:0.5px;font-weight:600;
}}
.role-admin  {{background:#fff0d0;color:#a06000}}
.role-user   {{background:#dcfff5;color:var(--teal)}}
.role-manager{{background:#ebebff;color:#4040c0}}
.status-active  {{color:var(--teal);font-size:0.8rem}}
.status-inactive{{color:var(--rust);font-size:0.8rem}}

/* ── EMPTY STATE ────────────────────────────── */
.empty{{text-align:center;padding:48px 20px;color:var(--muted);font-size:0.85rem}}
.empty-icon{{font-size:2.5rem;margin-bottom:12px}}

/* ── TOAST ──────────────────────────────────── */
#toast{{
  position:fixed;bottom:28px;right:28px;
  padding:12px 20px;border-radius:8px;
  font-family:var(--font-body);font-size:0.85rem;font-weight:500;
  z-index:9998;
  transform:translateY(16px);opacity:0;
  transition:all 0.3s cubic-bezier(.175,.885,.32,1.275);
  pointer-events:none;max-width:320px;
  box-shadow:var(--shadow2);
}}
#toast.on{{transform:translateY(0);opacity:1}}
#toast.ok {{background:var(--teal);color:white}}
#toast.err{{background:var(--rust);color:white}}
#toast.inf{{background:var(--ink);color:var(--amber)}}

/* ── SPINNER ────────────────────────────────── */
.spin{{
  width:14px;height:14px;border-radius:50%;
  border:2px solid rgba(255,255,255,0.3);
  border-top-color:white;
  animation:rot 0.6s linear infinite;display:inline-block;
}}
@keyframes rot{{to{{transform:rotate(360deg)}}}}
</style>
</head>
<body>

<header>
  <div class="logo"><em>Nexus</em>DB</div>
  <div class="header-right">
    <div class="live-dot"></div>
    <span>SERVERLESS · LAMBDA · DYNAMODB</span>
  </div>
</header>

<div class="shell">

  <!-- SIDEBAR -->
  <aside>
    <div class="nav-label">Dashboard</div>
    <div class="nav-item active" onclick="show('create')" id="nav-create">
      <span class="nav-icon">＋</span> Create User
      <span class="method-tag tag-post">POST</span>
    </div>
    <div class="nav-item" onclick="show('getall')" id="nav-getall">
      <span class="nav-icon">◈</span> All Users
      <span class="method-tag tag-get">GET</span>
    </div>
    <div class="nav-item" onclick="show('getone')" id="nav-getone">
      <span class="nav-icon">◎</span> Find User
      <span class="method-tag tag-get">GET</span>
    </div>
    <div class="nav-item" onclick="show('update')" id="nav-update">
      <span class="nav-icon">✎</span> Update User
      <span class="method-tag tag-put">PUT</span>
    </div>
    <div class="nav-item" onclick="show('remove')" id="nav-remove">
      <span class="nav-icon">✕</span> Delete User
      <span class="method-tag tag-delete">DEL</span>
    </div>
  </aside>

  <!-- MAIN -->
  <main>
    <div class="page-title">USER MANAGEMENT</div>
    <div class="page-sub">// Serverless REST API · AWS Lambda + DynamoDB</div>

    <!-- ① CREATE -->
    <div class="card visible" id="card-create">
      <div class="card-header">
        <span class="method-pill pill-post">POST</span>
        <span class="card-title">CREATE USER</span>
        <span class="endpoint-badge">/users</span>
      </div>
      <div class="form-grid">
        <div class="fg"><label>Full Name *</label>
          <input id="c-name" placeholder="e.g. Aryan Mehta"/></div>
        <div class="fg"><label>Email *</label>
          <input id="c-email" type="email" placeholder="aryan@company.com"/></div>
        <div class="fg"><label>Phone</label>
          <input id="c-phone" placeholder="+91 9000000000"/></div>
        <div class="fg"><label>Department</label>
          <input id="c-dept" placeholder="Engineering"/></div>
        <div class="fg"><label>Role</label>
          <select id="c-role">
            <option value="user">User</option>
            <option value="admin">Admin</option>
            <option value="manager">Manager</option>
          </select></div>
        <div class="fg"><label>Status</label>
          <select id="c-status">
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
          </select></div>
      </div>
      <div class="btn-row">
        <button class="btn btn-amber" onclick="createUser()">＋ Create User</button>
        <button class="btn btn-ghost" onclick="clearCard('c')">Clear</button>
      </div>
      <div class="resp-box" id="c-resp"></div>
    </div>

    <!-- ② GET ALL -->
    <div class="card" id="card-getall">
      <div class="card-header">
        <span class="method-pill pill-get">GET</span>
        <span class="card-title">ALL USERS</span>
        <span class="endpoint-badge">/users</span>
      </div>
      <div class="btn-row" style="margin-bottom:20px">
        <button class="btn btn-teal" onclick="getAllUsers()">↓ Load All Users</button>
      </div>
      <div class="tbl-wrap">
        <table><thead><tr>
          <th>ID</th><th>Name</th><th>Email</th>
          <th>Dept</th><th>Role</th><th>Status</th><th>Actions</th>
        </tr></thead>
        <tbody id="tbl-body">
          <tr><td colspan="7"><div class="empty">
            <div class="empty-icon">📋</div>Click Load to fetch records
          </div></td></tr>
        </tbody></table>
      </div>
    </div>

    <!-- ③ GET ONE -->
    <div class="card" id="card-getone">
      <div class="card-header">
        <span class="method-pill pill-get">GET</span>
        <span class="card-title">FIND USER</span>
        <span class="endpoint-badge">/users/{{id}}</span>
      </div>
      <div class="id-bar">
        <input id="g-id" placeholder="Paste user UUID here…"/>
        <button class="btn btn-teal" onclick="getOne()">Search</button>
      </div>
      <div class="resp-box" id="g-resp"></div>
    </div>

    <!-- ④ UPDATE -->
    <div class="card" id="card-update">
      <div class="card-header">
        <span class="method-pill pill-put">PUT</span>
        <span class="card-title">UPDATE USER</span>
        <span class="endpoint-badge">/users/{{id}}</span>
      </div>
      <div class="id-bar">
        <input id="u-id" placeholder="User UUID to update…"/>
      </div>
      <div class="form-grid">
        <div class="fg"><label>Name</label>
          <input id="u-name" placeholder="New name"/></div>
        <div class="fg"><label>Email</label>
          <input id="u-email" placeholder="New email"/></div>
        <div class="fg"><label>Phone</label>
          <input id="u-phone" placeholder="New phone"/></div>
        <div class="fg"><label>Department</label>
          <input id="u-dept" placeholder="New department"/></div>
        <div class="fg"><label>Role</label>
          <select id="u-role">
            <option value="">— unchanged —</option>
            <option value="user">User</option>
            <option value="admin">Admin</option>
            <option value="manager">Manager</option>
          </select></div>
        <div class="fg"><label>Status</label>
          <select id="u-status">
            <option value="">— unchanged —</option>
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
          </select></div>
      </div>
      <div class="btn-row">
        <button class="btn btn-purple" onclick="updateUser()">✎ Update User</button>
        <button class="btn btn-ghost" onclick="clearCard('u')">Clear</button>
      </div>
      <div class="resp-box" id="u-resp"></div>
    </div>

    <!-- ⑤ DELETE -->
    <div class="card" id="card-remove">
      <div class="card-header">
        <span class="method-pill pill-delete">DELETE</span>
        <span class="card-title">DELETE USER</span>
        <span class="endpoint-badge">/users/{{id}}</span>
      </div>
      <div class="id-bar">
        <input id="d-id" placeholder="User UUID to delete…"/>
        <button class="btn btn-rust" onclick="deleteUser()">✕ Delete</button>
      </div>
      <div class="resp-box" id="d-resp"></div>
    </div>

  </main>
</div>

<div id="toast"></div>

<script>
const API = '{BACKEND_API_URL}';

/* ── NAV ─────────────────────────────────────── */
const sections = ['create','getall','getone','update','remove'];
function show(key) {{
  sections.forEach(s => {{
    document.getElementById('card-'+s).classList.toggle('visible', s===key);
    document.getElementById('nav-'+s).classList.toggle('active',  s===key);
  }});
}}

/* ── TOAST ──────────────────────────────────── */
function toast(msg, type='inf') {{
  const t = document.getElementById('toast');
  t.textContent = msg; t.className = 'on '+type;
  clearTimeout(t._t);
  t._t = setTimeout(()=>t.className='', 3200);
}}

/* ── API CALL ───────────────────────────────── */
async function call(method, path, body=null) {{
  const opts = {{ method, headers: {{'Content-Type':'application/json'}} }};
  if (body) opts.body = JSON.stringify(body);
  try {{
    const r = await fetch(API+path, opts);
    const d = await r.json();
    return {{ status:r.status, data:d }};
  }} catch(e) {{
    toast('Network error: '+e.message, 'err'); return null;
  }}
}}

function showResp(id, data) {{
  const el = document.getElementById(id);
  el.textContent = JSON.stringify(data,null,2);
  el.classList.add('on');
}}

function clearCard(p) {{
  ['name','email','phone','dept','role','status'].forEach(f=>{{
    const el=document.getElementById(p+'-'+f);
    if(el) el.value = el.tagName==='SELECT' ? el.options[0].value : '';
  }});
  const r=document.getElementById(p+'-resp');
  if(r){{ r.textContent=''; r.classList.remove('on'); }}
}}

/* ── CREATE ─────────────────────────────────── */
async function createUser() {{
  const name=document.getElementById('c-name').value.trim();
  const email=document.getElementById('c-email').value.trim();
  if(!name||!email){{ toast('Name & Email required','err'); return; }}
  const btn=event.target; btn.disabled=true;
  btn.innerHTML='<span class="spin"></span> Creating…';
  const r = await call('POST','/users',{{
    name,email,
    phone: document.getElementById('c-phone').value.trim(),
    department: document.getElementById('c-dept').value.trim(),
    role: document.getElementById('c-role').value,
    status: document.getElementById('c-status').value
  }});
  btn.disabled=false; btn.innerHTML='＋ Create User';
  if(!r) return;
  showResp('c-resp', r.data);
  if(r.status===201){{
    toast('User created! ✓','ok');
    const u=r.data.user;
    setTimeout(()=>{{
      window.location.href='/success?action=created&id='+u.id+'&name='+encodeURIComponent(u.name)+'&email='+encodeURIComponent(u.email)+'&role='+u.role;
    }},700);
  }} else toast(r.data.error||'Error','err');
}}

/* ── GET ALL ────────────────────────────────── */
async function getAllUsers() {{
  const btn=event.target; btn.disabled=true;
  btn.innerHTML='<span class="spin"></span> Loading…';
  const r = await call('GET','/users');
  btn.disabled=false; btn.innerHTML='↓ Load All Users';
  if(!r) return;
  const tbody=document.getElementById('tbl-body');
  const users=r.data.users||[];
  if(!users.length){{
    tbody.innerHTML='<tr><td colspan="7"><div class="empty"><div class="empty-icon">📭</div>No users found</div></td></tr>';
    return;
  }}
  tbody.innerHTML=users.map(u=>`
    <tr>
      <td><span class="id-short" title="${{u.id}}">${{u.id}}</span></td>
      <td>${{u.name||'—'}}</td>
      <td>${{u.email||'—'}}</td>
      <td>${{u.department||'—'}}</td>
      <td><span class="role-tag role-${{u.role||'user'}}">${{u.role||'user'}}</span></td>
      <td><span class="status-${{u.status||'active'}}">● ${{u.status||'active'}}</span></td>
      <td>
        <div style="display:flex;gap:6px">
          <button class="btn btn-ghost" style="padding:5px 10px;font-size:0.72rem"
            onclick="fillUpdate('${{u.id}}','${{u.name}}','${{u.email}}','${{u.phone||''}}','${{u.department||''}}','${{u.role||''}}','${{u.status||''}}')">Edit</button>
          <button class="btn btn-rust" style="padding:5px 10px;font-size:0.72rem"
            onclick="fillDelete('${{u.id}}')">Del</button>
        </div>
      </td>
    </tr>
  `).join('');
  toast(`${{users.length}} user(s) loaded`,'ok');
}}

/* ── GET ONE ────────────────────────────────── */
async function getOne() {{
  const id=document.getElementById('g-id').value.trim();
  if(!id){{ toast('Enter a user ID','err'); return; }}
  const r=await call('GET','/users/'+id);
  if(r){{ showResp('g-resp',r.data); if(r.status!==200) toast(r.data.error,'err'); else toast('User found','ok'); }}
}}

/* ── UPDATE ─────────────────────────────────── */
async function updateUser() {{
  const id=document.getElementById('u-id').value.trim();
  if(!id){{ toast('Enter a user ID','err'); return; }}
  const body={{}};
  [['name','u-name'],['email','u-email'],['phone','u-phone'],
   ['department','u-dept'],['role','u-role'],['status','u-status']].forEach(([k,el])=>{{
    const v=document.getElementById(el).value.trim();
    if(v && v!=='— unchanged —') body[k]=v;
  }});
  if(!Object.keys(body).length){{ toast('No fields to update','err'); return; }}
  const btn=event.target; btn.disabled=true;
  btn.innerHTML='<span class="spin"></span> Updating…';
  const r=await call('PUT','/users/'+id,body);
  btn.disabled=false; btn.innerHTML='✎ Update User';
  if(!r) return;
  showResp('u-resp',r.data);
  if(r.status===200){{
    toast('User updated! ✓','ok');
    const u=r.data.user||{{}};
    setTimeout(()=>{{
      window.location.href='/success?action=updated&id='+id+'&name='+encodeURIComponent(u.name||'')+'&email='+encodeURIComponent(u.email||'')+'&role='+(u.role||'');
    }},700);
  }} else toast(r.data.error||'Update failed','err');
}}

/* ── DELETE ─────────────────────────────────── */
async function deleteUser() {{
  const id=document.getElementById('d-id').value.trim();
  if(!id){{ toast('Enter a user ID','err'); return; }}
  if(!confirm('Delete this user? This cannot be undone.')) return;
  const r=await call('DELETE','/users/'+id);
  if(!r) return;
  showResp('d-resp',r.data);
  if(r.status===200){{
    toast('User deleted','ok');
    setTimeout(()=>{{ window.location.href='/success?action=deleted&id='+id; }},700);
  }} else toast(r.data.error||'Delete failed','err');
}}

/* ── FILL HELPERS ───────────────────────────── */
function fillUpdate(id,name,email,phone,dept,role,status){{
  document.getElementById('u-id').value=id;
  document.getElementById('u-name').value=name;
  document.getElementById('u-email').value=email;
  document.getElementById('u-phone').value=phone;
  document.getElementById('u-dept').value=dept;
  document.getElementById('u-role').value=role;
  document.getElementById('u-status').value=status;
  show('update');
}}
function fillDelete(id){{
  document.getElementById('d-id').value=id;
  show('remove');
}}
</script>
</body>
</html>
""".replace('{BACKEND_API_URL}', BACKEND_API_URL)


# ═══════════════════════════════════════════════
#  PAGE: SUCCESS
# ═══════════════════════════════════════════════
def render_success(qsp):
    action = qsp.get('action', 'updated')
    uid    = qsp.get('id',     '—')
    name   = qsp.get('name',   '—')
    email  = qsp.get('email',  '—')
    role   = qsp.get('role',   '—')

    icons    = {'created': '✦', 'updated': '✔', 'deleted': '✕'}
    labels   = {'created': 'RECORD CREATED',  'updated': 'RECORD UPDATED',  'deleted': 'RECORD REMOVED'}
    headlines= {'created': 'User <em>Created</em>', 'updated': 'User <em>Updated</em>', 'deleted': 'User <em>Deleted</em>'}
    accents  = {'created': '#1a7a6e', 'updated': '#5050c0', 'deleted': '#c94a2c'}

    icon     = icons.get(action, '✔')
    label    = labels.get(action, 'OPERATION COMPLETE')
    headline = headlines.get(action, 'Done')
    accent   = accents.get(action, '#1a7a6e')

    rows = f"""
      <div class="dr"><span class="dk">Action</span><span class="dv act">{action.upper()}</span></div>
      <div class="dr"><span class="dk">User ID</span><span class="dv mono">{uid}</span></div>
    """
    if action != 'deleted':
        rows += f"""
      <div class="dr"><span class="dk">Name</span><span class="dv">{name}</span></div>
      <div class="dr"><span class="dk">Email</span><span class="dv">{email}</span></div>
      <div class="dr"><span class="dk">Role</span><span class="dv">{role}</span></div>
        """

    from datetime import datetime
    ts = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>NexusDB — {label}</title>
<link rel="preconnect" href="https://fonts.googleapis.com"/>
<link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Outfit:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet"/>
<style>
:root{{
  --ink:    #0d0d14;
  --paper:  #f5f4f0;
  --cream:  #ede9e0;
  --line:   #d8d4cc;
  --muted:  #8a8a9a;
  --accent: {accent};
}}
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
body{{
  background:var(--paper);
  color:var(--ink);
  font-family:'Outfit',sans-serif;
  min-height:100vh;
  display:flex;flex-direction:column;align-items:center;justify-content:center;
  padding:40px 20px;
  position:relative;overflow:hidden;
}}
/* diagonal stripe bg */
body::before{{
  content:'';position:fixed;inset:0;
  background:repeating-linear-gradient(
    -45deg,
    transparent,transparent 40px,
    rgba(13,13,20,0.015) 40px,rgba(13,13,20,0.015) 41px
  );
  pointer-events:none;
}}
.card{{
  background:white;
  border:1px solid var(--line);
  border-radius:16px;
  padding:52px 60px;
  max-width:520px;width:100%;
  text-align:center;
  position:relative;z-index:1;
  box-shadow:0 20px 60px rgba(13,13,20,0.1);
  animation:rise 0.5s cubic-bezier(.175,.885,.32,1.275) forwards;
  opacity:0;transform:scale(0.94) translateY(20px);
}}
@keyframes rise{{to{{opacity:1;transform:scale(1) translateY(0)}}}}
/* accent top bar */
.card::before{{
  content:'';position:absolute;top:0;left:0;right:0;
  height:4px;border-radius:16px 16px 0 0;
  background:var(--accent);
}}
.icon-wrap{{
  width:80px;height:80px;border-radius:50%;
  background:color-mix(in srgb, var(--accent) 12%, white);
  border:2px solid color-mix(in srgb, var(--accent) 30%, transparent);
  display:flex;align-items:center;justify-content:center;
  font-size:2rem;color:var(--accent);
  margin:0 auto 24px;
}}
.label{{
  font-family:'JetBrains Mono',monospace;
  font-size:0.65rem;letter-spacing:4px;
  color:var(--accent);margin-bottom:12px;
  text-transform:uppercase;
}}
h1{{
  font-family:'Bebas Neue',sans-serif;
  font-size:3rem;letter-spacing:1px;line-height:1;
  margin-bottom:8px;
}}
h1 em{{color:var(--accent);font-style:normal}}
.sub{{font-size:0.83rem;color:var(--muted);margin-bottom:32px;line-height:1.5}}
.detail-table{{
  background:var(--paper);border:1px solid var(--line);
  border-radius:10px;overflow:hidden;margin-bottom:32px;text-align:left;
}}
.dr{{
  display:flex;padding:10px 18px;
  border-bottom:1px solid var(--line);font-size:0.82rem;
  align-items:center;
}}
.dr:last-child{{border-bottom:none}}
.dk{{
  width:90px;flex-shrink:0;
  font-size:0.67rem;letter-spacing:1.5px;text-transform:uppercase;
  color:var(--muted);font-weight:600;
}}
.dv{{color:var(--ink)}}
.dv.mono{{font-family:'JetBrains Mono',monospace;font-size:0.72rem;color:var(--muted)}}
.dv.act{{font-weight:600;color:var(--accent);text-transform:uppercase;letter-spacing:1px;font-size:0.78rem}}
.ts{{font-family:'JetBrains Mono',monospace;font-size:0.7rem;color:var(--muted);margin-bottom:28px}}
.btn-row{{display:flex;gap:10px;justify-content:center}}
.btn{{
  font-family:'Outfit',sans-serif;
  font-size:0.85rem;font-weight:600;
  padding:11px 26px;border-radius:8px;border:none;cursor:pointer;
  text-decoration:none;display:inline-flex;align-items:center;gap:7px;
  transition:all 0.18s;
}}
.btn-main{{background:var(--accent);color:white;box-shadow:0 4px 16px color-mix(in srgb,var(--accent) 40%,transparent)}}
.btn-main:hover{{opacity:0.88}}
.btn-out{{background:transparent;color:var(--muted);border:1.5px solid var(--line)}}
.btn-out:hover{{color:var(--ink);border-color:var(--muted)}}
/* confetti dots */
.dot{{position:fixed;border-radius:3px;animation:fall linear forwards;opacity:0;pointer-events:none}}
@keyframes fall{{0%{{opacity:1;transform:translateY(-10px) rotate(0)}}100%{{opacity:0;transform:translateY(105vh) rotate(540deg)}}}}
</style>
</head>
<body>
<div id="dots"></div>
<div class="card">
  <div class="icon-wrap">{icon}</div>
  <div class="label">{label}</div>
  <h1>{headline}</h1>
  <p class="sub">Your DynamoDB record has been updated successfully.</p>
  <div class="detail-table">{rows}</div>
  <div class="ts">Processed · {ts} UTC</div>
  <div class="btn-row">
    <a href="/" class="btn btn-main">← Back to Dashboard</a>
    <button class="btn btn-out" onclick="window.print()">⎙ Print</button>
  </div>
</div>
<script>
if('{action}'!=='deleted'){{
  const colors=['#1a7a6e','#e8a020','#c94a2c','#5050c0','#0d0d14'];
  const wrap=document.getElementById('dots');
  for(let i=0;i<50;i++){{
    const d=document.createElement('div');
    d.className='dot';
    d.style.cssText=`left:${{Math.random()*100}}%;top:${{-Math.random()*10}}%;
      background:${{colors[Math.floor(Math.random()*colors.length)]}};
      width:${{4+Math.random()*7}}px;height:${{4+Math.random()*7}}px;
      animation-duration:${{2+Math.random()*3}}s;
      animation-delay:${{Math.random()*1.2}}s`;
    wrap.appendChild(d);
  }}
}}
</script>
</body>
</html>"""


# ═══════════════════════════════════════════════
#  PAGE: 404
# ═══════════════════════════════════════════════
def render_404():
    return """<!DOCTYPE html>
<html><head><meta charset="UTF-8"/>
<title>404 — NexusDB</title>
<link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Outfit:wght@400&display=swap" rel="stylesheet"/>
<style>
body{background:#0d0d14;color:#f5f4f0;font-family:'Outfit',sans-serif;
  display:flex;align-items:center;justify-content:center;height:100vh;flex-direction:column;gap:16px}
h1{font-family:'Bebas Neue',sans-serif;font-size:8rem;color:#e8a020;line-height:1}
p{color:#8a8a9a}a{color:#e8a020}
</style></head>
<body><h1>404</h1><p>Page not found. <a href="/">Go home</a></p></body></html>"""
