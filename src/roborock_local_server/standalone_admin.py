"""Standalone admin/dashboard adapter routes."""

from __future__ import annotations

import json
from textwrap import dedent
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse

from .security import verify_password


_SHARED_STYLES = """\
:root {
  --bg: #101214;
  --panel: #171a1d;
  --panel-2: #1c2024;
  --border: #2b3138;
  --border-2: #3a424c;
  --text: #e3e7eb;
  --muted: #9aa3ad;
  --faint: #77818c;
  --blue: #6ea8fe;
  --green: #7dd3a0;
  --yellow: #d8b15a;
  --red: #e07a7a;
  --rule-line: rgba(255,255,255,0.03);
  --primary-bg: #1c2733;
  --primary-border: #355277;
  --primary-text: #cfe2ff;
  --primary-hover: #4d709d;
  --danger-bg: #241b1b;
  --danger-border: #5f3a3a;
  --danger-text: #f0b3b3;
}
html[data-theme="light"] {
  --bg: #f4f5f6;
  --panel: #ffffff;
  --panel-2: #f1f2f4;
  --border: #d7dbdf;
  --border-2: #bfc4ca;
  --text: #1a1e22;
  --muted: #5b636b;
  --faint: #8a919a;
  --blue: #1f5cc2;
  --green: #2f7a54;
  --yellow: #8a6a1a;
  --red: #b03a3a;
  --rule-line: rgba(0,0,0,0.05);
  --primary-bg: #e5edf8;
  --primary-border: #1f5cc2;
  --primary-text: #0f3e86;
  --primary-hover: #0f3e86;
  --danger-bg: #f8e4e4;
  --danger-border: #b03a3a;
  --danger-text: #7a2222;
}
* { box-sizing: border-box; }
html, body {
  margin: 0;
  padding: 0;
  background: var(--bg);
  color: var(--text);
  font: 14px/1.45 system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  -webkit-font-smoothing: antialiased;
}
a { color: var(--blue); text-decoration: none; }
a:hover { color: var(--text); }

.wrap {
  max-width: 1120px;
  margin: 0 auto;
  padding: 18px 18px 28px;
}

header.topbar {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 14px;
}
header.topbar h1 {
  margin: 0 0 4px;
  font-size: 20px;
  font-weight: 600;
}
header.topbar .sub {
  color: var(--muted);
  font-size: 13px;
}
header.topbar .actions {
  display: flex;
  gap: 8px;
  align-items: center;
  flex-shrink: 0;
}

.panel {
  background: var(--panel);
  border: 1px solid var(--border);
  margin-bottom: 14px;
}
.panel-body { padding: 14px; }
.panel h2 {
  margin: 0 0 12px;
  font-size: 15px;
  font-weight: 600;
}
.note {
  color: var(--muted);
  font-size: 13px;
  margin: -4px 0 12px;
}

.layout {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
  align-items: stretch;
  margin-bottom: 14px;
}
.layout > main,
.layout > aside {
  display: flex;
  flex-direction: column;
}
.layout > main > .panel,
.layout > aside > .panel {
  flex: 1;
  margin-bottom: 0;
  display: flex;
  flex-direction: column;
}
.layout > main > .panel > .panel-body,
.layout > aside > .panel > .panel-body {
  flex: 1;
}
.row2 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.field { margin-bottom: 12px; }
.field label {
  display: block;
  margin-bottom: 5px;
  font-size: 12px;
  color: var(--muted);
  font-weight: 600;
}
.field input,
.field select {
  width: 100%;
  background: var(--panel-2);
  color: var(--text);
  border: 1px solid var(--border-2);
  border-radius: 0;
  padding: 9px 10px;
  font: inherit;
  outline: none;
}
.field input:focus,
.field select:focus { border-color: var(--blue); }

.actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-top: 14px;
}

.btn {
  appearance: none;
  border: 1px solid var(--border-2);
  background: var(--panel-2);
  color: var(--text);
  padding: 9px 12px;
  font: inherit;
  font-weight: 600;
  cursor: pointer;
  border-radius: 0;
}
.btn:hover { border-color: #56606c; }
html[data-theme="light"] .btn:hover { border-color: #8a919a; }
.btn.primary {
  background: var(--primary-bg);
  border-color: var(--primary-border);
  color: var(--primary-text);
}
.btn.primary:hover { border-color: var(--primary-hover); }
.btn.danger {
  background: var(--danger-bg);
  border-color: var(--danger-border);
  color: var(--danger-text);
}
.btn.icon {
  width: 36px;
  height: 36px;
  padding: 0;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}
.btn.icon svg { width: 16px; height: 16px; }
html[data-theme="light"] .btn.icon .sun { display: block; }
html[data-theme="light"] .btn.icon .moon { display: none; }
.btn.icon .sun { display: none; }
.btn.icon .moon { display: block; }
.btn:disabled { opacity: 0.55; cursor: not-allowed; }

.callout {
  border: 1px solid var(--border-2);
  background: var(--panel-2);
  padding: 12px;
  margin-bottom: 12px;
}
.callout strong { display: block; margin-bottom: 4px; font-size: 14px; }
.callout .sub { color: var(--muted); font-size: 13px; }
.callout.ok { border-left: 3px solid var(--green); }
.callout.err { border-left: 3px solid var(--red); }
.callout.info { border-left: 3px solid var(--blue); }
.callout.warn { border-left: 3px solid var(--yellow); }

.tag {
  display: inline-block;
  padding: 2px 6px;
  border: 1px solid var(--border-2);
  background: var(--panel-2);
  font-size: 12px;
  color: var(--muted);
}
.tag.ok { color: var(--green); border-color: #355746; }
html[data-theme="light"] .tag.ok { border-color: #7ba593; }
.tag.no { color: var(--red); border-color: #5f3a3a; }
html[data-theme="light"] .tag.no { border-color: #b88585; }
.tag.mono { font: 12px/1.4 ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }

.device-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 10px;
}
.device {
  background: var(--panel-2);
  border: 1px solid var(--border);
  color: var(--text);
  padding: 14px;
  border-radius: 0;
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.device .head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 8px;
}
.device .name {
  font-weight: 600;
  font-size: 14px;
  word-break: break-word;
}
.device .ident {
  font: 11px/1.4 ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  color: var(--faint);
  margin-top: 2px;
}
.device .rows {
  display: flex;
  flex-direction: column;
  gap: 6px;
  font-size: 13px;
}
.device .rows .row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
}
.device .rows .k { color: var(--muted); }
.device .rows .v {
  font: 12px/1.4 ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
}

.stats {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.stat {
  min-width: 140px;
  border: 1px solid var(--border);
  background: var(--panel-2);
  padding: 9px 10px;
}
.stat .k {
  display: block;
  color: var(--faint);
  font-size: 11px;
  margin-bottom: 2px;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}
.stat .v { font-weight: 600; }

.log {
  background: #0d0f11;
  border: 1px solid var(--border);
  padding: 10px;
  max-height: 560px;
  overflow-y: auto;
}
html[data-theme="light"] .log { background: #fafbfc; }
.log pre {
  margin: 0;
  font: 12px/1.45 ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  white-space: pre-wrap;
  color: var(--text);
}

.support-links {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.support-links a {
  display: inline-block;
  padding: 7px 12px;
  border: 1px solid var(--border-2);
  background: var(--panel-2);
  color: var(--text);
  font-weight: 600;
  font-size: 13px;
}
.support-links a:hover { border-color: var(--blue); color: var(--blue); }

footer.footer {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  margin-top: 12px;
  color: var(--faint);
  font-size: 12px;
}

@media (max-width: 900px) {
  .layout { grid-template-columns: 1fr; }
  .row2 { grid-template-columns: 1fr; }
}
"""


_THEME_INIT_SCRIPT = """\
(function () {
  var saved = null;
  try { saved = localStorage.getItem("rr-theme"); } catch (e) {}
  var theme = saved || "dark";
  document.documentElement.setAttribute("data-theme", theme);
})();
"""


_THEME_TOGGLE_SCRIPT = """\
function toggleTheme() {
  var current = document.documentElement.getAttribute("data-theme");
  var next = current === "dark" ? "light" : "dark";
  document.documentElement.setAttribute("data-theme", next);
  try { localStorage.setItem("rr-theme", next); } catch (e) {}
}
"""


_THEME_TOGGLE_BUTTON = """\
<button class="btn icon" onclick="toggleTheme()" aria-label="Toggle theme" title="Toggle theme" type="button">
  <svg class="moon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>
  <svg class="sun" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41"/></svg>
</button>
"""


def _admin_login_html() -> str:
    return dedent(
        f"""\
        <!doctype html>
        <html lang="en">
        <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width,initial-scale=1" />
        <title>Sign in · Roborock Local Server</title>
        <script>{_THEME_INIT_SCRIPT}</script>
        <style>
        {_SHARED_STYLES}
        .login-wrap {{
          min-height: 100vh;
          display: grid;
          place-items: center;
          padding: 24px;
        }}
        .login-panel {{
          width: 100%;
          max-width: 380px;
        }}
        .login-corner {{
          position: fixed;
          top: 18px;
          right: 18px;
        }}
        </style>
        </head>
        <body>
          <div class="login-corner">{_THEME_TOGGLE_BUTTON}</div>
          <div class="login-wrap">
            <form class="panel login-panel" onsubmit="return false">
              <div class="panel-body">
                <h2>Roborock Local Server</h2>
                <div class="note">Sign in to manage the stack.</div>
                <div class="field">
                  <label for="password">Admin password</label>
                  <input id="password" type="password" autocomplete="current-password" autofocus />
                </div>
                <div id="result" class="callout err" style="display:none"></div>
                <div class="actions">
                  <button id="login" class="btn primary" type="submit">Sign In</button>
                </div>
              </div>
            </form>
          </div>
        <script>
        {_THEME_TOGGLE_SCRIPT}
        var loginBtn = document.getElementById("login");
        var passwordInput = document.getElementById("password");
        var resultEl = document.getElementById("result");
        function escapeHtml(s) {{
          return String(s).replace(/[&<>"']/g, function (c) {{
            return {{"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}}[c];
          }});
        }}
        async function doLogin() {{
          resultEl.style.display = "none";
          resultEl.innerHTML = "";
          try {{
            var response = await fetch("/admin/api/login", {{
              method: "POST",
              headers: {{"Content-Type":"application/json"}},
              body: JSON.stringify({{password: passwordInput.value}})
            }});
            var payload = await response.json().catch(function () {{ return {{error: "Invalid response"}}; }});
            if (!response.ok) {{
              resultEl.innerHTML = '<strong>Sign-in failed</strong><div class="sub">' + escapeHtml(payload.error || "Invalid password") + '</div>';
              resultEl.style.display = "block";
              return;
            }}
            window.location.reload();
          }} catch (err) {{
            resultEl.innerHTML = '<strong>Sign-in failed</strong><div class="sub">' + escapeHtml(err.message || "Network error") + '</div>';
            resultEl.style.display = "block";
          }}
        }}
        loginBtn.addEventListener("click", doLogin);
        passwordInput.addEventListener("keydown", function (e) {{
          if (e.key === "Enter") doLogin();
        }});
        </script>
        </body></html>
        """
    )


def _admin_dashboard_html(project_support: dict[str, Any]) -> str:
    support_payload = json.dumps(project_support)
    return dedent(
        f"""\
        <!doctype html>
        <html lang="en">
        <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width,initial-scale=1" />
        <title>Roborock Local Server</title>
        <script>{_THEME_INIT_SCRIPT}</script>
        <style>
        {_SHARED_STYLES}
        </style>
        </head>
        <body>
        <div class="wrap">

          <header class="topbar">
            <div>
              <h1>Roborock Local Server</h1>
              <div class="sub">Admin dashboard. Refreshes automatically.</div>
            </div>
            <div class="actions" style="margin-top:0">
              <span id="overall" class="tag">loading</span>
              {_THEME_TOGGLE_BUTTON}
              <button id="logout" class="btn" type="button">Sign Out</button>
            </div>
          </header>

          <section class="panel">
            <div class="panel-body">
              <h2>Vacuums</h2>
              <div class="note">Devices known to this server.</div>
              <div id="device-list" class="device-list">
                <div class="callout info"><strong>Loading vacuums...</strong></div>
              </div>
            </div>
          </section>

          <div class="layout">
            <main>
              <section class="panel">
                <div class="panel-body">
                  <h2>Cloud Import</h2>
                  <div class="note">Pull device inventory from your Roborock account.</div>
                  <div class="field">
                    <label for="email">Account email</label>
                    <div style="display:flex;gap:8px;align-items:stretch">
                      <input id="email" type="email" placeholder="email@example.com" autocomplete="email" style="flex:1" />
                      <button id="sendCode" class="btn" type="button" style="flex-shrink:0">Send Code</button>
                    </div>
                  </div>
                  <div class="field" style="margin-bottom:0">
                    <label for="code">Email code</label>
                    <div style="display:flex;gap:8px;align-items:stretch">
                      <input id="code" type="text" placeholder="from Roborock email" autocomplete="one-time-code" style="flex:1" />
                      <button id="fetchData" class="btn primary" type="button" style="flex-shrink:0">Fetch Data</button>
                    </div>
                  </div>
                  <div id="cloudCallout" class="callout" style="margin-top:12px;display:none"></div>
                </div>
              </section>
            </main>

            <aside>
              <section class="panel">
                <div class="panel-body">
                  <h2 id="supportTitle">Support</h2>
                  <div id="supportText" class="note"></div>
                  <div id="supportLinks" class="support-links"></div>
                </div>
              </section>
            </aside>
          </div>

          <section class="panel">
            <div class="panel-body">
              <h2>Diagnostics</h2>
              <div class="note">Raw snapshots.</div>
              <div class="actions" style="margin-top:0;margin-bottom:10px">
                <button id="tab-health" class="btn primary" type="button">Health</button>
                <button id="tab-vacuums" class="btn" type="button">Vacuums</button>
              </div>
              <div id="diag" class="log"><pre id="diag-content">loading...</pre></div>
            </div>
          </section>

          <footer class="footer">
            <span>Admin interface</span>
            <span id="last-update">—</span>
          </footer>

        </div>

        <script>
        {_THEME_TOGGLE_SCRIPT}
        const support = {support_payload};
        let cloudSessionId = "";
        let diagTab = "health";
        let lastStatus = null;
        let lastVacuums = null;

        const $ = (id) => document.getElementById(id);

        function escapeHtml(s) {{
          return String(s).replace(/[&<>"']/g, (c) => ({{
            "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
          }})[c]);
        }}

        // Support section
        $("supportTitle").textContent = support.title || "Support This Project";
        $("supportText").textContent = support.text || "";
        const supportLinksEl = $("supportLinks");
        for (const link of (support.links || [])) {{
          const a = document.createElement("a");
          a.href = link.url;
          a.target = "_blank";
          a.rel = "noreferrer";
          a.textContent = link.label || link.url;
          supportLinksEl.appendChild(a);
        }}

        async function fetchJson(url, options) {{
          const response = await fetch(url, options);
          const raw = await response.text();
          const payload = raw ? JSON.parse(raw) : {{}};
          if (!response.ok) throw new Error(payload.error || `HTTP ${{response.status}}`);
          return payload;
        }}

        function setOverall(state, label) {{
          const el = $("overall");
          el.className = "tag " + state;
          el.textContent = label;
        }}

        function tag(state, label) {{
          return '<span class="tag ' + state + '">' + escapeHtml(label) + '</span>';
        }}

        function renderDevices(vacuums) {{
          const list = $("device-list");
          const items = Array.isArray(vacuums) ? vacuums : [];
          if (!items.length) {{
            list.innerHTML = '<div class="callout info"><strong>No vacuums yet</strong><div class="sub">Run a cloud import to populate inventory.</div></div>';
            return;
          }}
          list.innerHTML = items.map((v) => {{
            const onboarding = v.onboarding || {{}};
            const keyState = onboarding.key_state || {{}};
            const name = v.name || v.did || v.duid || "Unknown device";
            const samples = Number(keyState.query_samples || 0);
            const hasKey = Boolean(onboarding.has_public_key);
            const connected = Boolean(v.connected);
            const duid = v.duid || v.did || "";
            return '<div class="device">' +
              '<div class="head">' +
                '<div>' +
                  '<div class="name">' + escapeHtml(name) + '</div>' +
                  (duid ? '<div class="ident">' + escapeHtml(duid) + '</div>' : '') +
                '</div>' +
              '</div>' +
              '<div class="rows">' +
                '<div class="row"><span class="k">mqtt</span>' + tag(connected ? "ok" : "no", connected ? "connected" : "disconnected") + '</div>' +
                '<div class="row"><span class="k">query samples</span><span class="v">' + samples + '</span></div>' +
                '<div class="row"><span class="k">public key</span>' + tag(hasKey ? "ok" : "no", hasKey ? "ready" : "pending") + '</div>' +
              '</div>' +
            '</div>';
          }}).join("");
        }}

        function renderDiag() {{
          const el = $("diag-content");
          if (diagTab === "health") {{
            el.textContent = lastStatus && lastStatus.health ? JSON.stringify(lastStatus.health, null, 2) : "loading...";
          }} else {{
            el.textContent = lastVacuums ? JSON.stringify(lastVacuums, null, 2) : "loading...";
          }}
          $("tab-health").className = "btn" + (diagTab === "health" ? " primary" : "");
          $("tab-vacuums").className = "btn" + (diagTab === "vacuums" ? " primary" : "");
        }}

        async function refresh() {{
          try {{
            const status = await fetchJson("/admin/api/status");
            lastStatus = status;
            const ok = status.health && status.health.overall_ok;
            setOverall(ok ? "ok" : "no", ok ? "healthy" : "needs attention");

            const vacuums = await fetchJson("/admin/api/vacuums");
            lastVacuums = vacuums.vacuums;
            renderDevices(vacuums.vacuums);

            $("last-update").textContent = "updated " + new Date().toLocaleTimeString([], {{hour12: false}});
            renderDiag();
          }} catch (err) {{
            setOverall("no", err.message || "error");
          }}
        }}

        function setCloud(kind, title, detail) {{
          const el = $("cloudCallout");
          el.className = "callout " + kind;
          el.innerHTML = '<strong>' + escapeHtml(title) + '</strong>' +
            (detail ? '<div class="sub"><pre style="margin:0;white-space:pre-wrap;font:12px/1.45 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace">' + escapeHtml(detail) + '</pre></div>' : "");
          el.style.display = "block";
        }}

        $("sendCode").addEventListener("click", async () => {{
          try {{
            const payload = await fetchJson("/admin/api/cloud/request-code", {{
              method: "POST",
              headers: {{"Content-Type":"application/json"}},
              body: JSON.stringify({{email: $("email").value}})
            }});
            cloudSessionId = payload.session_id || "";
            setCloud(payload.success ? "ok" : "err",
              payload.success ? "Code sent" : "Could not send code",
              JSON.stringify(payload, null, 2));
          }} catch (error) {{
            setCloud("err", "Could not send code", error.message);
          }}
        }});

        $("fetchData").addEventListener("click", async () => {{
          try {{
            const payload = await fetchJson("/admin/api/cloud/submit-code", {{
              method: "POST",
              headers: {{"Content-Type":"application/json"}},
              body: JSON.stringify({{session_id: cloudSessionId, code: $("code").value}})
            }});
            cloudSessionId = "";
            setCloud(payload.success ? "ok" : "err",
              payload.success ? "Data fetched" : "Could not fetch data",
              JSON.stringify(payload, null, 2));
            await refresh();
          }} catch (error) {{
            setCloud("err", "Could not fetch data", error.message);
          }}
        }});

        $("logout").addEventListener("click", async () => {{
          await fetch("/admin/api/logout", {{method:"POST"}});
          window.location.reload();
        }});

        $("tab-health").addEventListener("click", () => {{ diagTab = "health"; renderDiag(); }});
        $("tab-vacuums").addEventListener("click", () => {{ diagTab = "vacuums"; renderDiag(); }});

        refresh();
        setInterval(() => {{ refresh(); }}, 2000);
        </script>
        </body></html>
        """
    )


def register_standalone_admin_routes(
        *,
        app: FastAPI,
        supervisor: Any,
        project_support: dict[str, Any],
) -> None:
    @app.get("/admin", response_class=HTMLResponse)
    async def admin_page(request: Request) -> HTMLResponse:
        if not supervisor._authenticated(request):
            return HTMLResponse(_admin_login_html())
        return HTMLResponse(_admin_dashboard_html(project_support))

    @app.post("/admin/api/login")
    async def admin_login(request: Request) -> JSONResponse:
        try:
            body = await request.json()
        except json.JSONDecodeError:
            body = {}
        password = str((body or {}).get("password") or "")
        if not verify_password(password, supervisor.config.admin.password_hash):
            return JSONResponse({"error": "Invalid password"}, status_code=401)
        response = JSONResponse({"ok": True})
        response.set_cookie(
            supervisor.session_manager.cookie_name,
            supervisor.session_manager.issue(),
            httponly=True,
            secure=request.url.scheme == "https",
            samesite="lax",
            max_age=supervisor.config.admin.session_ttl_seconds,
            path="/",
        )
        return response

    @app.post("/admin/api/logout")
    async def admin_logout() -> JSONResponse:
        response = JSONResponse({"ok": True})
        response.delete_cookie(supervisor.session_manager.cookie_name, path="/")
        return response

    @app.get("/admin/api/status")
    async def admin_status(request: Request) -> JSONResponse:
        supervisor._require_admin(request)
        return JSONResponse(supervisor._status_payload())

    @app.get("/admin/api/vacuums")
    async def admin_vacuums(request: Request) -> JSONResponse:
        supervisor._require_admin(request)
        return JSONResponse(supervisor._vacuums_payload())

    @app.get("/admin/api/onboarding/devices")
    async def admin_onboarding_devices(request: Request) -> JSONResponse:
        supervisor._require_admin(request)
        return JSONResponse(supervisor._onboarding_devices_payload())

    @app.post("/admin/api/onboarding/sessions")
    async def admin_onboarding_start(request: Request) -> JSONResponse:
        supervisor._require_admin(request)
        try:
            body = await request.json()
        except json.JSONDecodeError:
            body = {}
        duid = str((body or {}).get("duid") or "").strip()
        try:
            payload = supervisor.start_onboarding_session(duid=duid)
        except ValueError as exc:
            return JSONResponse({"error": str(exc)}, status_code=400)
        except KeyError:
            return JSONResponse({"error": "Unknown onboarding device"}, status_code=404)
        return JSONResponse(payload)

    @app.get("/admin/api/onboarding/sessions/{session_id}")
    async def admin_onboarding_status(session_id: str, request: Request) -> JSONResponse:
        supervisor._require_admin(request)
        try:
            payload = supervisor.onboarding_session_snapshot(session_id=session_id)
        except KeyError:
            return JSONResponse({"error": "Onboarding session not found"}, status_code=404)
        return JSONResponse(payload)

    @app.delete("/admin/api/onboarding/sessions/{session_id}")
    async def admin_onboarding_delete(session_id: str, request: Request) -> JSONResponse:
        supervisor._require_admin(request)
        try:
            payload = supervisor.clear_onboarding_session(session_id=session_id)
        except KeyError:
            return JSONResponse({"error": "Onboarding session not found"}, status_code=404)
        return JSONResponse(payload)


    @app.post("/admin/api/cloud/request-code")
    async def admin_cloud_request_code(request: Request) -> JSONResponse:
        supervisor._require_admin(request)
        try:
            body = await request.json()
        except json.JSONDecodeError:
            body = {}
        try:
            result = await supervisor.cloud_manager.request_code(
                email=str((body or {}).get("email") or ""),
                base_url=str((body or {}).get("base_url") or ""),
            )
        except Exception as exc:  # noqa: BLE001
            result = {"success": False, "step": "code_request_failed", "error": str(exc)}
        supervisor.runtime_state.record_cloud_request(result)
        return JSONResponse(result, status_code=200 if result.get("success") else 400)

    @app.post("/admin/api/cloud/submit-code")
    async def admin_cloud_submit_code(request: Request) -> JSONResponse:
        supervisor._require_admin(request)
        try:
            body = await request.json()
        except json.JSONDecodeError:
            body = {}
        try:
            result = await supervisor.cloud_manager.submit_code(
                session_id=str((body or {}).get("session_id") or ""),
                code=str((body or {}).get("code") or ""),
            )
            supervisor.refresh_inventory_state()
        except Exception as exc:  # noqa: BLE001
            result = {"success": False, "step": "code_submit_failed", "error": str(exc)}
        supervisor.runtime_state.record_cloud_request(result)
        return JSONResponse(result, status_code=200 if result.get("success") else 400)