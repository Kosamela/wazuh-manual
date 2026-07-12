#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Buduje stronę HTML instrukcji Wazuh (artifact + GitHub Pages) z pliku MD."""
import os, re, unicodedata
import markdown

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "Instrukcja-Wdrozeniowa-WAZUH.md")
OUT_ARTIFACT = os.path.join(ROOT, "site", "wazuh-manual-artifact.html")
OUT_PAGES = os.path.join(ROOT, "docs", "index.html")
os.makedirs(os.path.join(ROOT, "docs"), exist_ok=True)

# ---------------------------------------------------------------- slugify (PL)
def slugify(value, separator):
    value = unicodedata.normalize("NFKD", value)
    value = value.encode("ascii", "ignore").decode("ascii")
    value = re.sub(r"[^\w\s-]", "", value).strip().lower()
    return re.sub(r"[\s_-]+", separator, value)

# ---------------------------------------------------------------- markdown -> html
md_text = open(SRC, encoding="utf-8").read()
md = markdown.Markdown(
    extensions=["tables", "fenced_code", "toc", "sane_lists"],
    extension_configs={"toc": {"slugify": slugify, "separator": "-"}},
)
body = md.convert(md_text)

# --- usuń zduplikowany tytuł: pierwsze h1 + metryczkę (blockquote) + hr -------
body = re.sub(r"^\s*<h1[^>]*>.*?</h1>\s*<blockquote>.*?</blockquote>\s*<hr\s*/?>\s*",
              "", body, count=1, flags=re.S)

# wrap tables for horizontal scroll
body = body.replace("<table>", '<div class="tbl"><table>')
body = body.replace("</table>", "</table></div>")

# --- callouts: paragraphs starting with emoji markers -------------------------
body = re.sub(r"<p>⚠️\s*", '<p class="co co-warn">', body)
body = re.sub(r"<p>💡\s*", '<p class="co co-tip">', body)
body = re.sub(r"<p>✅\s*", '<p class="co co-check">', body)

# --- usuń zdublowane etykiety na początku calloutów (chip ::before je pokazuje)
def callout_lead(m):
    head, extra, etap = m.group(1), m.group(2), m.group(3)
    if extra:                       # "Uwaga (SELinux):" -> "<strong>SELinux:</strong> "
        return head + "<strong>" + extra + ":</strong> "
    if etap:                        # "Punkt kontrolny etapu 1:" -> "<strong>Etap 1:</strong> "
        return head + "<strong>Etap " + re.sub(r"\D", "", etap) + ":</strong> "
    return head
body = re.sub(
    r'(<p class="co co-(?:warn|tip|check)">)'
    r'<strong>(?:Uwaga|Dobra praktyka|Dobre praktyki|Punkt kontrolny)'
    r'(?:\s*\(([^)]+)\))?( etapu \d+)?:</strong>\s*',
    callout_lead, body)

# --- task-list items "- [ ]" --------------------------------------------------
body = body.replace("<li>[ ] ", '<li class="task"><span class="cb" aria-hidden="true"></span>')

# --- replace the three mermaid blocks (in document order) ---------------------
DIAG_ARCH = """
<figure class="diagram" aria-label="Diagram architektury klastrowej Wazuh">
  <div class="dg-tier">
    <div class="dg-label">Końcówki i źródła logów</div>
    <div class="dg-row">
      <div class="dg-node">Agent Windows</div>
      <div class="dg-node">Agent Linux / macOS</div>
      <div class="dg-node">Urządzenia sieciowe<br><small>syslog / agentless</small></div>
    </div>
  </div>
  <div class="dg-arrow"><span>1514 dane · 1515 rejestracja · 514 syslog</span></div>
  <div class="dg-tier dg-slim">
    <div class="dg-row"><div class="dg-node dg-lb">Load balancer (NGINX / HAProxy)<br><small>lub lista serwerów w konfiguracji agenta</small></div></div>
  </div>
  <div class="dg-arrow"><span>1515 zawsze do mastera · 1514 round-robin</span></div>
  <div class="dg-tier">
    <div class="dg-label">Klaster Wazuh Manager <small>— synchronizacja :1516</small></div>
    <div class="dg-row">
      <div class="dg-node dg-master">Manager <b>MASTER</b><br><small>+ Filebeat</small></div>
      <div class="dg-node">Manager worker 1<br><small>+ Filebeat</small></div>
      <div class="dg-node">Manager worker n<br><small>+ Filebeat</small></div>
    </div>
  </div>
  <div class="dg-arrow"><span>Filebeat → TLS :9200</span></div>
  <div class="dg-tier">
    <div class="dg-label">Klaster Wazuh Indexer <small>— OpenSearch, komunikacja :9200 / 9300–9400</small></div>
    <div class="dg-row">
      <div class="dg-node">Indexer node 1</div>
      <div class="dg-node">Indexer node 2</div>
      <div class="dg-node">Indexer node 3</div>
    </div>
  </div>
  <div class="dg-arrow dg-up"><span>Dashboard czyta dane :9200 · API managera :55000</span></div>
  <div class="dg-tier dg-slim">
    <div class="dg-row">
      <div class="dg-node dg-dash">Wazuh Dashboard <small>HTTPS :443</small></div>
      <div class="dg-node dg-user">Administrator / SOC<br><small>dostęp wyłącznie przez VPN</small></div>
    </div>
  </div>
  <figcaption>Wariant klastrowy. W wariancie standalone wszystkie komponenty serwerowe stoją na jednej maszynie.</figcaption>
</figure>
"""

DIAG_DECISION = """
<figure class="diagram" aria-label="Flowchart decyzyjny wyboru architektury">
  <div class="dg-steps">
    <div class="dg-step"><span class="dg-num">1</span>Inwentaryzacja źródeł logów</div>
    <div class="dg-step"><span class="dg-num">2</span>Oszacuj EPS (rozdz. 4.2) i pomnóż <b>×2</b> na zapas</div>
    <div class="dg-step"><span class="dg-num">3</span>Wybierz wariant według progów poniżej</div>
  </div>
  <div class="dg-branch">
    <div class="dg-card ok">
      <div class="dg-cond">EPS ≤ 200 <b>i</b> ≤ ~200 agentów<br><b>i</b> brak planów szybkiego wzrostu</div>
      <div class="dg-res">STANDALONE<br><small>1 maszyna: Manager + Indexer + Dashboard</small></div>
    </div>
    <div class="dg-card mid">
      <div class="dg-cond">EPS 200 – 1000</div>
      <div class="dg-res">KLASTER ŚREDNI<br><small>2 managery (master + worker) · 3 indexery · 1 dashboard</small></div>
    </div>
    <div class="dg-card big">
      <div class="dg-cond">EPS &gt; 1000</div>
      <div class="dg-res">KLASTER DUŻY<br><small>2–3 managery · 3–5 indexerów · 1–2 dashboardy</small></div>
    </div>
  </div>
  <div class="dg-steps">
    <div class="dg-step"><span class="dg-num">4</span>Określ retencję (rozdz. 4.5) i policz dyski: <code>wolumen dzienny × retencja × 1,3</code></div>
    <div class="dg-step"><span class="dg-num">5</span>Zaplanuj snapshoty / backup poza platformą (rozdz. 4.6)</div>
  </div>
  <figcaption>Progi możesz policzyć automatycznie w <a href="#kreator">kreatorze doboru architektury</a>.</figcaption>
</figure>
"""

DIAG_INSTALL = """
<figure class="diagram" aria-label="Kolejność instalacji dystrybuowanej">
  <ol class="dg-chain">
    <li><b>Certyfikaty TLS</b><small>wazuh-certs-tool</small></li>
    <li><b>Wazuh Indexer</b><small>wszystkie węzły</small></li>
    <li><b>Security init</b><small>indexer-security-init.sh</small></li>
    <li><b>Manager + Filebeat</b><small>master, potem workery</small></li>
    <li><b>Dashboard</b><small>opensearch_dashboards.yml</small></li>
    <li><b>Hasła + testy</b><small>wazuh-passwords-tool</small></li>
  </ol>
  <figcaption>Kolejność jest nienegocjowalna — Indexer musi działać, zanim uruchomisz Filebeat i Dashboard.</figcaption>
</figure>
"""

diagrams = [DIAG_ARCH, DIAG_DECISION, DIAG_INSTALL]
def repl_mermaid(m):
    return diagrams.pop(0) if diagrams else ""
body = re.sub(
    r'<pre><code class="language-mermaid">.*?</code></pre>',
    repl_mermaid, body, flags=re.S)
assert not diagrams, "Nie wszystkie diagramy zostały wstawione!"

# ---------------------------------------------------------------- kalkulator
CALC = """
<section class="calc" id="kreator" aria-label="Kreator doboru architektury">
  <div class="calc-head">
    <span class="eyebrow">Narzędzie interaktywne</span>
    <h2 class="calc-title">Kreator doboru architektury</h2>
    <p class="calc-sub">Wpisz liczbę źródeł logów w swojej organizacji — kreator oszacuje EPS,
    dobierze wariant architektury i policzy liczbę maszyn oraz zasoby według metodyki z rozdziału 4.</p>
  </div>
  <div class="calc-grid">
    <form class="calc-form" id="calcForm" autocomplete="off">
      <fieldset>
        <legend>Źródła logów</legend>
        <div class="fld"><label for="winSrv">Serwery Windows</label>
          <input type="number" id="winSrv" min="0" max="100000" value="10" inputmode="numeric"></div>
        <div class="fld"><label for="winWs">Stacje robocze Windows</label>
          <input type="number" id="winWs" min="0" max="1000000" value="100" inputmode="numeric"></div>
        <div class="fld"><label for="linux">Serwery / stacje Linux</label>
          <input type="number" id="linux" min="0" max="100000" value="10" inputmode="numeric"></div>
        <div class="fld"><label for="utm">Firewalle / UTM</label>
          <input type="number" id="utm" min="0" max="10000" value="1" inputmode="numeric"></div>
        <div class="fld"><label for="extraEps">Inne źródła <small>(dodatkowy EPS)</small></label>
          <input type="number" id="extraEps" min="0" max="1000000" value="0" inputmode="numeric"></div>
      </fieldset>
      <fieldset>
        <legend>Parametry</legend>
        <div class="fld"><label for="retention">Retencja online <small>(dni)</small></label>
          <input type="number" id="retention" min="7" max="1095" value="90" inputmode="numeric"></div>
        <div class="fld fld-check">
          <input type="checkbox" id="headroom" checked>
          <label for="headroom">Zapas ×2 <small>(wzrost, NIS2 — zalecane)</small></label></div>
      </fieldset>
      <fieldset>
        <legend>Liczba maszyn (klaster)</legend>
        <div class="fld fld-check">
          <input type="radio" name="topo" id="topoRef" value="ref" checked>
          <label for="topoRef">Referencyjna <small>(pełna separacja — zalecana)</small></label></div>
        <div class="fld fld-check">
          <input type="radio" name="topo" id="topoCompact" value="compact">
          <label for="topoCompact">Skonsolidowana <small>(mniej maszyn, role łączone)</small></label></div>
      </fieldset>
      <details class="calc-adv">
        <summary>Zaawansowane: EPS na urządzenie</summary>
        <div class="fld"><label for="epsWinSrv">Serwer Windows <small>(typowo 5–20)</small></label>
          <input type="number" id="epsWinSrv" min="1" max="100" value="15"></div>
        <div class="fld"><label for="epsWinWs">Stacja Windows <small>(5–10)</small></label>
          <input type="number" id="epsWinWs" min="1" max="50" value="8"></div>
        <div class="fld"><label for="epsLinux">Linux <small>(1–5)</small></label>
          <input type="number" id="epsLinux" min="1" max="50" value="3"></div>
        <div class="fld"><label for="epsUtm">Firewall / UTM <small>(50–300)</small></label>
          <input type="number" id="epsUtm" min="10" max="1000" value="150"></div>
      </details>
    </form>

    <div class="calc-out" id="calcOut" aria-live="polite">
      <div class="rec" id="recCard">
        <span class="rec-eyebrow">Rekomendowana architektura</span>
        <div class="rec-name" id="recName">—</div>
        <p class="rec-why" id="recWhy"></p>
      </div>
      <div class="tiles">
        <div class="tile"><span class="tile-label">EPS projektowy</span><span class="tile-val" id="tEps">—</span><span class="tile-sub" id="tEpsSub"></span></div>
        <div class="tile"><span class="tile-label">Agenci</span><span class="tile-val" id="tAgents">—</span><span class="tile-sub">końcówki z agentem</span></div>
        <div class="tile"><span class="tile-label">Wolumen dzienny</span><span class="tile-val" id="tDaily">—</span><span class="tile-sub">GB / dzień (zakres)</span></div>
        <div class="tile"><span class="tile-label">Dysk łącznie</span><span class="tile-val" id="tDisk">—</span><span class="tile-sub" id="tDiskSub"></span></div>
      </div>
      <div class="tbl calc-tbl">
        <table>
          <thead><tr><th>Maszyna</th><th>Rola</th><th>vCPU</th><th>RAM</th><th>Dysk (SSD)</th></tr></thead>
          <tbody id="machRows"></tbody>
        </table>
      </div>
      <ul class="calc-notes" id="calcNotes"></ul>
      <details class="calc-how">
        <summary>Jak to jest liczone?</summary>
        <ul>
          <li>EPS = Σ (liczba urządzeń × EPS na urządzenie) + inne źródła; opcjonalnie ×2 zapasu.</li>
          <li>Wolumen: 1 EPS ≈ 0,5–1 KB/s → 100 EPS ≈ 4–8 GB/dzień (górna granica użyta do sizingu).</li>
          <li>Dysk = wolumen dzienny × retencja × 1,3 (narzut indeksów) × 1,25 (zapas); w klastrze ×2 (1 replika).</li>
          <li>CPU: ~100 EPS ≈ 1 vCPU (manager), ~1–2 vCPU (indexer). Heap JVM indexera = 50% RAM, maks. 32 GB.</li>
          <li>Progi architektury: ≤200 EPS standalone · 200–1000 klaster średni · &gt;1000 klaster duży (rozdz. 4.1).</li>
        </ul>
      </details>
    </div>
  </div>
</section>
"""

# ---------------------------------------------------------------- CSS
CSS = r"""
:root{
  --bg:#F5F7FB; --surface:#FFFFFF; --surface2:#EBF0F7; --sidebar:#EFF3F9;
  --ink:#17222F; --ink2:#46586B; --muted:#7A8A9B; --line:#D9E1EB;
  --accent:#2563AC; --accent-soft:#E3EDF9; --accent-ink:#1D4E88;
  --warn:#8A5D10; --warn-bg:#FBF3E0; --warn-line:#E5C377;
  --tip:#1E6B52; --tip-bg:#E7F4EE; --tip-line:#9CCCB6;
  --check:#2E6E45; --check-bg:#EAF4EC; --check-line:#A9CFB4;
  --code-bg:#101A28; --code-ink:#D6E2F0; --code-line:#233document144;
  --shadow:0 1px 2px rgba(23,34,47,.06),0 6px 24px -12px rgba(23,34,47,.12);
}
@media (prefers-color-scheme: dark){:root{
  --bg:#0C121C; --surface:#121A28; --surface2:#1A2434; --sidebar:#0F1723;
  --ink:#E4EAF2; --ink2:#AAB8C8; --muted:#75859A; --line:#26344A;
  --accent:#6EA7E8; --accent-soft:#1B2C44; --accent-ink:#9CC4F2;
  --warn:#E2B45C; --warn-bg:#2A2210; --warn-line:#6B5522;
  --tip:#7CC8A8; --tip-bg:#11271E; --tip-line:#2C5A45;
  --check:#84C297; --check-bg:#12261A; --check-line:#2E5A3D;
  --code-bg:#0B131F; --code-ink:#CEDCEC;
  --shadow:0 1px 2px rgba(0,0,0,.4),0 6px 24px -12px rgba(0,0,0,.5);
}}
:root[data-theme="light"]{
  --bg:#F5F7FB; --surface:#FFFFFF; --surface2:#EBF0F7; --sidebar:#EFF3F9;
  --ink:#17222F; --ink2:#46586B; --muted:#7A8A9B; --line:#D9E1EB;
  --accent:#2563AC; --accent-soft:#E3EDF9; --accent-ink:#1D4E88;
  --warn:#8A5D10; --warn-bg:#FBF3E0; --warn-line:#E5C377;
  --tip:#1E6B52; --tip-bg:#E7F4EE; --tip-line:#9CCCB6;
  --check:#2E6E45; --check-bg:#EAF4EC; --check-line:#A9CFB4;
  --code-bg:#101A28; --code-ink:#D6E2F0;
  --shadow:0 1px 2px rgba(23,34,47,.06),0 6px 24px -12px rgba(23,34,47,.12);
}
:root[data-theme="dark"]{
  --bg:#0C121C; --surface:#121A28; --surface2:#1A2434; --sidebar:#0F1723;
  --ink:#E4EAF2; --ink2:#AAB8C8; --muted:#75859A; --line:#26344A;
  --accent:#6EA7E8; --accent-soft:#1B2C44; --accent-ink:#9CC4F2;
  --warn:#E2B45C; --warn-bg:#2A2210; --warn-line:#6B5522;
  --tip:#7CC8A8; --tip-bg:#11271E; --tip-line:#2C5A45;
  --check:#84C297; --check-bg:#12261A; --check-line:#2E5A3D;
  --code-bg:#0B131F; --code-ink:#CEDCEC;
  --shadow:0 1px 2px rgba(0,0,0,.4),0 6px 24px -12px rgba(0,0,0,.5);
}
*{box-sizing:border-box}
html{scroll-behavior:smooth;scroll-padding-top:24px}
@media (prefers-reduced-motion: reduce){html{scroll-behavior:auto}}
body{margin:0;background:var(--bg);color:var(--ink);
  font:16px/1.65 system-ui,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;
  -webkit-font-smoothing:antialiased;text-rendering:optimizeLegibility}
a{color:var(--accent-ink);text-decoration-color:color-mix(in srgb,var(--accent) 45%,transparent)}
a:hover{text-decoration-thickness:2px}
:focus-visible{outline:2px solid var(--accent);outline-offset:2px;border-radius:2px}

/* ---------- layout ---------- */
.app{display:grid;grid-template-columns:280px minmax(0,1fr);min-height:100vh}
.side{background:var(--sidebar);border-right:1px solid var(--line);padding:0}
.side-inner{position:sticky;top:0;max-height:100vh;overflow-y:auto;padding:28px 20px 40px}
.main{min-width:0;padding:0 clamp(20px,5vw,64px) 96px}
.content{max-width:78ch}

/* ---------- sidebar ---------- */
.brand{display:flex;align-items:center;gap:10px;margin-bottom:6px}
.brand-mark{width:34px;height:34px;border-radius:8px;background:var(--accent);color:#fff;
  display:grid;place-items:center;font-weight:800;font-size:15px;letter-spacing:.02em;flex:none}
.brand b{font-size:15px;letter-spacing:.01em}
.brand small{display:block;color:var(--muted);font-size:11.5px;font-weight:400}
.side nav{margin-top:18px}
.toc-h2, .toc-h3{display:block;text-decoration:none;border-left:2px solid transparent}
.toc-h2{color:var(--ink2);font-size:13.5px;font-weight:600;padding:5px 10px;margin-top:2px;border-radius:0 6px 6px 0}
.toc-h3{color:var(--muted);font-size:12.5px;padding:3px 10px 3px 22px}
.toc-h2:hover,.toc-h3:hover{background:var(--surface2);color:var(--ink)}
.toc-h2.on,.toc-h3.on{border-left-color:var(--accent);color:var(--accent-ink);background:var(--accent-soft)}
.side-foot{margin-top:26px;padding-top:14px;border-top:1px solid var(--line)}
.theme-btn{appearance:none;border:1px solid var(--line);background:var(--surface);color:var(--ink2);
  font:12.5px/1 inherit;padding:7px 12px;border-radius:99px;cursor:pointer}
.theme-btn:hover{border-color:var(--accent);color:var(--accent-ink)}
.menu-btn{display:none}

/* ---------- header ---------- */
.hero{padding:52px 0 8px}
.eyebrow{display:inline-block;font-size:11.5px;font-weight:700;letter-spacing:.1em;
  text-transform:uppercase;color:var(--accent-ink);background:var(--accent-soft);
  padding:4px 10px;border-radius:99px}
.hero h1{font-size:clamp(26px,4vw,38px);line-height:1.15;letter-spacing:-.015em;
  margin:14px 0 10px;text-wrap:balance}
.hero .meta{color:var(--muted);font-size:13.5px;display:flex;gap:18px;flex-wrap:wrap;margin:0}

/* ---------- typography ---------- */
.content h2{font-size:25px;letter-spacing:-.012em;line-height:1.25;margin:64px 0 14px;
  padding-top:22px;border-top:1px solid var(--line);text-wrap:balance}
.content h3{font-size:19px;letter-spacing:-.008em;margin:38px 0 10px;text-wrap:balance}
.content h4{font-size:16px;margin:28px 0 8px}
.content p, .content li{color:var(--ink);}
.content hr{border:0;border-top:1px solid var(--line);margin:40px 0}
.content blockquote{margin:18px 0;padding:12px 18px;border-left:3px solid var(--accent);
  background:var(--surface);border-radius:0 10px 10px 0;color:var(--ink2)}
.content blockquote p{margin:6px 0}
.content ul,.content ol{padding-left:26px}
.content li{margin:4px 0}
li.task{list-style:none;margin-left:-22px;display:flex;gap:9px;align-items:baseline}
li.task .cb{flex:none;width:13px;height:13px;border:1.5px solid var(--muted);border-radius:3.5px;
  transform:translateY(1.5px)}

/* ---------- code ---------- */
code{font-family:ui-monospace,"Cascadia Code","JetBrains Mono",Consolas,Menlo,monospace;
  font-size:.875em}
p code, li code, td code, h2 code, h3 code{background:var(--surface2);
  padding:.12em .38em;border-radius:5px;color:var(--ink)}
pre{background:var(--code-bg);color:var(--code-ink);border-radius:12px;
  padding:16px 18px;overflow-x:auto;line-height:1.55;box-shadow:var(--shadow);
  border:1px solid color-mix(in srgb,var(--code-bg) 60%,var(--line))}
pre code{background:none;padding:0;color:inherit;font-size:13px}

/* ---------- tables ---------- */
.tbl{overflow-x:auto;margin:18px 0;border:1px solid var(--line);border-radius:12px;background:var(--surface)}
table{border-collapse:collapse;width:100%;font-size:14px;font-variant-numeric:tabular-nums}
th{font-size:12px;text-transform:uppercase;letter-spacing:.06em;color:var(--muted);
  text-align:left;font-weight:650}
th,td{padding:9px 14px;border-bottom:1px solid var(--line);vertical-align:top}
tbody tr:last-child td{border-bottom:0}
tbody tr:hover{background:var(--surface2)}

/* ---------- callouts ---------- */
.co{border-radius:10px;padding:12px 16px;margin:16px 0;border:1px solid;font-size:15px}
.co::before{font-weight:800;font-size:11px;letter-spacing:.09em;text-transform:uppercase;
  display:block;margin-bottom:3px}
.co-warn{background:var(--warn-bg);border-color:var(--warn-line);color:var(--ink)}
.co-warn::before{content:"⚠ Uwaga";color:var(--warn)}
.co-tip{background:var(--tip-bg);border-color:var(--tip-line)}
.co-tip::before{content:"Dobra praktyka";color:var(--tip)}
.co-check{background:var(--check-bg);border-color:var(--check-line)}
.co-check::before{content:"✓ Punkt kontrolny";color:var(--check)}

/* ---------- diagrams ---------- */
.diagram{margin:26px 0;padding:22px;background:var(--surface);border:1px solid var(--line);
  border-radius:14px;box-shadow:var(--shadow)}
.diagram figcaption{margin-top:14px;color:var(--muted);font-size:12.5px}
.dg-tier{border:1px dashed var(--line);border-radius:10px;padding:12px}
.dg-slim{border-style:none;padding:0}
.dg-label{font-size:11px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;
  color:var(--muted);margin-bottom:8px}
.dg-label small{font-weight:500;text-transform:none;letter-spacing:0}
.dg-row{display:flex;gap:10px;flex-wrap:wrap}
.dg-node{flex:1 1 130px;background:var(--surface2);border:1px solid var(--line);border-radius:9px;
  padding:9px 12px;font-size:13.5px;font-weight:600;text-align:center;line-height:1.35}
.dg-node small{display:block;font-weight:450;color:var(--muted);font-size:11.5px;margin-top:2px}
.dg-master{border-color:var(--accent);background:var(--accent-soft)}
.dg-lb,.dg-dash{background:var(--accent-soft);border-color:var(--accent)}
.dg-user{background:transparent;border-style:dashed}
.dg-arrow{display:flex;align-items:center;gap:10px;margin:8px 4px;color:var(--muted);font-size:12px}
.dg-arrow::before{content:"";width:2px;height:22px;margin-left:26px;
  background:linear-gradient(var(--accent),var(--accent));flex:none}
.dg-arrow span{background:var(--surface2);border-radius:99px;padding:2px 10px}
.dg-steps{display:flex;flex-direction:column;gap:8px;margin:4px 0}
.dg-step{display:flex;gap:10px;align-items:baseline;font-size:14.5px}
.dg-num{flex:none;width:22px;height:22px;border-radius:99px;background:var(--accent);color:#fff;
  font-size:12px;font-weight:700;display:grid;place-items:center;transform:translateY(3px)}
.dg-branch{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:12px;margin:16px 0}
.dg-card{border:1px solid var(--line);border-radius:11px;overflow:hidden;background:var(--surface2)}
.dg-cond{padding:10px 14px;font-size:13px;color:var(--ink2);border-bottom:1px solid var(--line);min-height:64px}
.dg-res{padding:12px 14px;font-weight:750;font-size:14px;letter-spacing:.02em}
.dg-res small{display:block;font-weight:450;color:var(--ink2);letter-spacing:0;margin-top:3px}
.dg-card.ok .dg-res{color:var(--check)} .dg-card.mid .dg-res{color:var(--accent-ink)} .dg-card.big .dg-res{color:var(--warn)}
.dg-chain{display:flex;flex-wrap:wrap;gap:8px;list-style:none;padding:0;margin:0;counter-reset:chain}
.dg-chain li{counter-increment:chain;flex:1 1 130px;background:var(--surface2);border:1px solid var(--line);
  border-radius:10px;padding:10px 12px 10px 12px;font-size:13px;position:relative}
.dg-chain li::before{content:counter(chain);display:inline-grid;place-items:center;width:20px;height:20px;
  border-radius:99px;background:var(--accent);color:#fff;font-size:11px;font-weight:700;margin-bottom:6px}
.dg-chain li b{display:block;font-size:13.5px}
.dg-chain li small{color:var(--muted)}

/* ---------- kalkulator ---------- */
.calc{margin:36px 0 8px;border:1px solid var(--line);border-radius:16px;overflow:hidden;
  background:var(--surface);box-shadow:var(--shadow)}
.calc-head{padding:26px 28px 6px;background:
  linear-gradient(180deg,var(--accent-soft),transparent 130%)}
.calc-title{margin:12px 0 6px;font-size:24px;letter-spacing:-.012em}
.calc-sub{color:var(--ink2);max-width:64ch;margin:0 0 12px;font-size:14.5px}
.calc-grid{display:grid;grid-template-columns:320px minmax(0,1fr);gap:0}
.calc-form{padding:18px 24px 26px;border-right:1px solid var(--line);display:flex;
  flex-direction:column;gap:16px}
.calc-form fieldset{border:0;padding:0;margin:0}
.calc-form legend{font-size:11.5px;font-weight:750;letter-spacing:.09em;text-transform:uppercase;
  color:var(--muted);margin-bottom:8px;padding:0}
.fld{display:flex;align-items:center;justify-content:space-between;gap:12px;margin:7px 0}
.fld label{font-size:14px;color:var(--ink)}
.fld label small{color:var(--muted)}
.fld input[type=number]{width:92px;padding:7px 10px;border:1px solid var(--line);border-radius:8px;
  background:var(--bg);color:var(--ink);font:14px inherit;font-variant-numeric:tabular-nums;text-align:right}
.fld input[type=number]:focus{border-color:var(--accent)}
.fld-check{justify-content:flex-start}
.fld-check input{width:16px;height:16px;accent-color:var(--accent)}
.calc-adv summary{cursor:pointer;font-size:13px;color:var(--accent-ink);font-weight:600}
.calc-adv[open] summary{margin-bottom:6px}
.calc-out{padding:22px 26px 26px;min-width:0}
.rec{border:1px solid var(--accent);background:var(--accent-soft);border-radius:12px;
  padding:16px 20px;margin-bottom:16px}
.rec-eyebrow{font-size:11px;font-weight:750;letter-spacing:.1em;text-transform:uppercase;color:var(--accent-ink)}
.rec-name{font-size:26px;font-weight:800;letter-spacing:-.01em;margin:4px 0 2px}
.rec-why{margin:4px 0 0;color:var(--ink2);font-size:14px}
.tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:10px;margin-bottom:16px}
.tile{background:var(--surface2);border:1px solid var(--line);border-radius:11px;padding:12px 14px}
.tile-label{display:block;font-size:11px;font-weight:700;letter-spacing:.08em;
  text-transform:uppercase;color:var(--muted)}
.tile-val{display:block;font-size:24px;font-weight:750;font-variant-numeric:tabular-nums;
  letter-spacing:-.01em;margin-top:3px}
.tile-sub{display:block;font-size:11.5px;color:var(--muted);margin-top:1px}
.calc-tbl{margin:0 0 14px}
.calc-notes{margin:0 0 14px;padding-left:22px;font-size:13.5px;color:var(--ink2)}
.calc-notes li{margin:4px 0}
.calc-how summary{cursor:pointer;font-size:13px;color:var(--accent-ink);font-weight:600}
.calc-how ul{font-size:13px;color:var(--ink2);margin:8px 0 0}

/* ---------- responsive ---------- */
@media (max-width: 1020px){
  .app{grid-template-columns:1fr}
  .side{position:fixed;inset:0 28% 0 0;z-index:40;transform:translateX(-102%);
    transition:transform .25s ease;box-shadow:0 0 40px rgba(0,0,0,.35)}
  @media (prefers-reduced-motion: reduce){.side{transition:none}}
  .side.open{transform:none}
  .menu-btn{display:inline-flex;align-items:center;gap:8px;position:fixed;top:14px;left:14px;z-index:50;
    appearance:none;border:1px solid var(--line);background:var(--surface);color:var(--ink);
    font:13px/1 inherit;font-weight:650;padding:9px 14px;border-radius:99px;cursor:pointer;box-shadow:var(--shadow)}
  .hero{padding-top:70px}
  .calc-grid{grid-template-columns:1fr}
  .calc-form{border-right:0;border-bottom:1px solid var(--line)}
}
@media print{
  .side,.menu-btn,.theme-btn{display:none}
  .app{display:block}
  pre{white-space:pre-wrap}
}
"""
CSS = CSS.replace("--code-line:#233document144;", "")  # usuń artefakt

# ---------------------------------------------------------------- JS
JS = r"""
(function(){
  "use strict";
  /* ---------- motyw ---------- */
  var tbtn = document.getElementById('themeBtn');
  function themeLabel(){
    var t = document.documentElement.getAttribute('data-theme');
    tbtn.textContent = t === 'dark' ? 'Motyw: ciemny' : t === 'light' ? 'Motyw: jasny' : 'Motyw: systemowy';
  }
  tbtn.addEventListener('click', function(){
    var cur = document.documentElement.getAttribute('data-theme');
    var next = cur === 'dark' ? 'light' : cur === 'light' ? null : 'dark';
    if(next){ document.documentElement.setAttribute('data-theme', next); }
    else { document.documentElement.removeAttribute('data-theme'); }
    themeLabel();
  });
  themeLabel();

  /* ---------- menu mobilne ---------- */
  var side = document.getElementById('side');
  var mbtn = document.getElementById('menuBtn');
  mbtn.addEventListener('click', function(){ side.classList.toggle('open'); });
  side.addEventListener('click', function(e){
    if(e.target.closest('a')) side.classList.remove('open');
  });

  /* ---------- spis treści ---------- */
  var nav = document.getElementById('toc');
  var heads = document.querySelectorAll('#content h2[id], #content h3[id]');
  heads.forEach(function(h){
    var a = document.createElement('a');
    a.href = '#' + h.id;
    a.className = h.tagName === 'H2' ? 'toc-h2' : 'toc-h3';
    a.textContent = h.textContent.replace(/^ETAP (\d) — /, '$1 · ');
    nav.appendChild(a);
  });
  var links = nav.querySelectorAll('a');
  var map = {};
  links.forEach(function(a){ map[a.getAttribute('href').slice(1)] = a; });
  var current = null;
  var io = new IntersectionObserver(function(entries){
    entries.forEach(function(en){
      if(en.isIntersecting){
        if(current) current.classList.remove('on');
        current = map[en.target.id];
        if(current){ current.classList.add('on'); }
      }
    });
  }, {rootMargin: '-10% 0px -80% 0px'});
  heads.forEach(function(h){ io.observe(h); });

  /* ---------- kalkulator ---------- */
  var $ = function(id){ return document.getElementById(id); };
  var inputs = ['winSrv','winWs','linux','utm','extraEps','retention',
                'epsWinSrv','epsWinWs','epsLinux','epsUtm'];
  var fmt = new Intl.NumberFormat('pl-PL', {maximumFractionDigits:0});
  var fmt1 = new Intl.NumberFormat('pl-PL', {maximumFractionDigits:1});
  function num(id){ var v = parseFloat($(id).value); return isFinite(v) && v >= 0 ? v : 0; }

  function calc(){
    var winSrv = num('winSrv'), winWs = num('winWs'), linux = num('linux'), utm = num('utm');
    var agents = winSrv + winWs + linux;
    var raw = winSrv*num('epsWinSrv') + winWs*num('epsWinWs') + linux*num('epsLinux')
            + utm*num('epsUtm') + num('extraEps');
    var head = $('headroom').checked;
    var eps = Math.ceil(raw * (head ? 2 : 1));
    var ret = Math.max(7, num('retention'));

    /* wolumen: 1 EPS = 0,5–1 KB/s -> GB/dzień */
    var dayLo = eps * 0.0432, dayHi = eps * 0.0864;
    /* dysk: górna granica x retencja x 1,3 narzut x 1,25 zapas */
    var diskGB = dayHi * ret * 1.3 * 1.25;

    var arch, why, machines = [], notes = [];
    var replicas = 0;

    if(raw === 0){
      $('recName').textContent = '—';
      $('recWhy').textContent = 'Wprowadź liczbę źródeł logów po lewej stronie.';
      $('tEps').textContent = $('tAgents').textContent = $('tDaily').textContent = $('tDisk').textContent = '—';
      $('tEpsSub').textContent = $('tDiskSub').textContent = '';
      $('machRows').innerHTML = ''; $('calcNotes').innerHTML = '';
      return;
    }

    function mgrSize(count){
      var v = Math.min(16, Math.max(4, Math.ceil(eps/100/count)));
      return {v:v, r:Math.min(32, Math.max(8, v*2))};
    }
    function idxSize(count){
      var v = Math.min(16, Math.max(8, Math.ceil(eps*1.5/100/count)));
      var r = Math.min(64, Math.max(16, v*4));
      return {v:v, r:r};
    }

    if(eps <= 200 && agents <= 200){
      arch = 'STANDALONE';
      why = 'EPS projektowy ' + fmt.format(eps) + ' i ' + fmt.format(agents) +
            ' agentów mieszczą się w limicie pojedynczego serwera (≤ 200 EPS, ≤ ~200 agentów).';
      var v = eps <= 100 ? 4 : 8, r = eps <= 100 ? 8 : 16;
      machines.push(['wazuh-aio','Manager + Indexer + Dashboard', v, r, diskGB]);
      notes.push('Planujesz wzrost powyżej ~200 agentów? Zaprojektuj od razu klaster — konwersja standalone → klaster wymaga regeneracji certyfikatów i przestoju (rozdz. 4.1).');
      notes.push('Na pojedynczym węźle ustaw number_of_replicas: 0 (replika bez drugiego węzła daje status yellow).');
    } else {
      replicas = 1;
      diskGB *= 2; /* 1 replika */
      var mgrN, idxN, dashN = 1;
      if(eps <= 1000){
        arch = 'KLASTER ŚREDNI';
        mgrN = 2; idxN = 3;
        why = 'EPS projektowy ' + fmt.format(eps) + ' (przedział 200–1000) wymaga klastra: 2 managery, 3 indexery (kworum), 1 dashboard.';
      } else {
        arch = 'KLASTER DUŻY';
        mgrN = eps > 3000 ? 3 : 2;
        idxN = Math.min(5, Math.max(3, Math.ceil(eps/1000) + 1));
        dashN = eps > 5000 ? 2 : 1;
        why = 'EPS projektowy ' + fmt.format(eps) + ' (> 1000) to środowisko duże: ' + mgrN +
              ' managery, ' + idxN + ' indexerów, ' + dashN + ' dashboard' + (dashN > 1 ? 'y' : '') + '.';
      }
      var ms = mgrSize(mgrN), is = idxSize(idxN);
      var idxDisk = diskGB / idxN;
      var compact = document.getElementById('topoCompact').checked;
      if(compact){
        arch += ' · SKONSOLIDOWANY';
        why += ' Wariant skonsolidowany: role łączone na ' + idxN + ' maszynach — węzły Indexera pozostają na osobnych hostach (kworum i HA zachowane), zasoby zsumowane.';
        for(var c=1;c<=idxN;c++){
          var roles = ['Indexer'], v = is.v, r = is.r, d = idxDisk;
          if(c === 1){ roles.unshift('Manager (master) + Filebeat'); v += ms.v; r += ms.r; d += 100; }
          else if(c <= mgrN){ roles.unshift('Manager (worker) + Filebeat'); v += ms.v; r += ms.r; d += 100; }
          if(c === 1 && dashN >= 1){ roles.push('Dashboard'); v += 2; r += 4; d += 50; }
          machines.push(['wazuh-node-'+c, roles.join(' + '), v, r, d]);
        }
        if(dashN > 1) machines.push(['wazuh-dashboard-2','Dashboard (druga instancja)', 2, 4, 50]);
        notes.push('Konsolidacja: NIGDY dwa węzły Indexera na jednym hoście (fikcja HA) i nigdy master z workerem na jednym hoście. Zasoby maszyn poniżej są już zsumowane.');
        notes.push('Na wspólnym hoście pilnuj osobnych katalogów certyfikatów (/etc/wazuh-indexer/certs, /etc/filebeat/certs, /etc/wazuh-dashboard/certs) — rozdz. 4.3.');
        if(eps > 1000) notes.push('Przy > 1000 EPS konsolidacja to ryzykowny kompromis — Indexer będzie konkurował z Managerem o RAM/dyski. Zalecana architektura referencyjna (rozdz. 4.3).');
      } else {
        machines.push(['wazuh-master-1','Manager (master) + Filebeat', ms.v, ms.r, 100]);
        for(var i=1;i<mgrN;i++) machines.push(['wazuh-worker-'+i,'Manager (worker) + Filebeat', ms.v, ms.r, 100]);
        for(var j=1;j<=idxN;j++) machines.push(['wazuh-indexer-'+j,'Wazuh Indexer', is.v, is.r, idxDisk]);
        for(var k=1;k<=dashN;k++) machines.push(['wazuh-dashboard'+(dashN>1?'-'+k:''),'Dashboard', 2, 4, 50]);
        notes.push('Klienta odstrasza liczba serwerów? Przełącz na wariant „Skonsolidowany" — klaster średni mieści się na 3 maszynach z zachowaniem HA i kworum (rozdz. 4.3).');
      }
      notes.push('Minimum 3 indexery = kworum klastra (ochrona przed split-brain, rozdz. 4.1).');
      notes.push('Ustaw 1 replikę indeksów — domyślne 0 replik oznacza brak HA (klaster RED po awarii węzła, rozdz. 7.1). Dysk poniżej uwzględnia już replikę (×2).');
      notes.push('Rejestracja agentów (port 1515) zawsze przez mastera — skonfiguruj to w load balancerze (rozdz. 7.3).');
      if(is.r >= 64) notes.push('Heap JVM indexera ustaw na maks. 31–32 GB niezależnie od RAM maszyny (rozdz. 4.4).');
    }
    notes.push('Dyski indexerów wyłącznie SSD/NVMe (ew. SAS 10–15k). HDD = gwarantowany problem wydajnościowy.');
    if(ret > 180) notes.push('Retencja ' + fmt.format(ret) + ' dni na dyskach online jest kosztowna — rozważ tiering hot/warm/cold i politykę ISM (rozdz. 4.5, 8.7).');

    $('recName').textContent = arch;
    $('recWhy').textContent = why;
    $('tEps').textContent = fmt.format(eps);
    $('tEpsSub').textContent = head ? (fmt.format(Math.ceil(raw)) + ' surowy × 2 zapasu') : 'bez zapasu (niezalecane)';
    $('tAgents').textContent = fmt.format(agents);
    $('tDaily').textContent = fmt.format(Math.round(dayLo)) + '–' + fmt.format(Math.round(dayHi));
    var diskTB = diskGB / 1000;
    $('tDisk').textContent = diskTB >= 1 ? fmt1.format(diskTB) + ' TB' : fmt.format(Math.round(diskGB)) + ' GB';
    $('tDiskSub').textContent = 'retencja ' + fmt.format(ret) + ' dni' + (replicas ? ' · 1 replika' : '') + ' · narzut ×1,3 · zapas ×1,25';

    $('machRows').innerHTML = machines.map(function(m){
      var d = m[4] >= 1000 ? fmt1.format(m[4]/1000) + ' TB' : fmt.format(Math.round(m[4])) + ' GB';
      return '<tr><td><code>' + m[0] + '</code></td><td>' + m[1] + '</td><td>' + m[2] +
             '</td><td>' + m[3] + ' GB</td><td>' + d + '</td></tr>';
    }).join('');
    $('calcNotes').innerHTML = notes.map(function(n){ return '<li>' + n + '</li>'; }).join('');
  }
  inputs.forEach(function(id){ $(id).addEventListener('input', calc); });
  $('headroom').addEventListener('change', calc);
  $('topoRef').addEventListener('change', calc);
  $('topoCompact').addEventListener('change', calc);
  calc();
})();
"""

# ---------------------------------------------------------------- kompozycja
INNER = (
    '<title>Instrukcja wdrożeniowa WAZUH</title>\n'
    '<style>' + CSS + '</style>\n'
    '<button class="menu-btn" id="menuBtn" aria-label="Pokaż spis treści">☰ Spis treści</button>\n'
    '<div class="app">\n'
    '<aside class="side" id="side"><div class="side-inner">\n'
    '  <div class="brand"><span class="brand-mark">W</span>'
    '<span><b>Wazuh — wdrożenie</b><small>instrukcja dla administratorów</small></span></div>\n'
    '  <nav id="toc" aria-label="Spis treści"><a class="toc-h2" href="#kreator">✦ Kreator doboru architektury</a></nav>\n'
    '  <div class="side-foot"><button class="theme-btn" id="themeBtn" type="button">Motyw</button></div>\n'
    '</div></aside>\n'
    '<main class="main">\n'
    '<header class="hero">\n'
    '  <span class="eyebrow">Manual wdrożeniowy · SIEM / XDR</span>\n'
    '  <h1>Instrukcja wdrożeniowa platformy WAZUH</h1>\n'
    '  <p class="meta"><span>Wersja 1.0 · 2026-07-12</span><span>Wazuh 4.x (4.9–4.14)</span>'
    '<span>projekt → infrastruktura → instalacja → klaster/HA → bezpieczeństwo</span></p>\n'
    '</header>\n'
    + CALC +
    '\n<article class="content" id="content">\n' + body + '\n</article>\n'
    '</main></div>\n'
    '<script>' + JS + '</script>\n'
)

# artifact (fragment — host claude.ai dokleja doctype/head/body)
open(OUT_ARTIFACT, "w", encoding="utf-8").write(INNER)

# GitHub Pages (pełny dokument)
PAGES = (
    "<!doctype html>\n<html lang=\"pl\">\n<head>\n<meta charset=\"utf-8\">\n"
    "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
    "<meta name=\"description\" content=\"Kompleksowa instrukcja wdrożeniowa platformy Wazuh: "
    "architektura, sizing, instalacja, klaster HA, bezpieczeństwo. Z interaktywnym kreatorem doboru architektury.\">\n"
    "</head>\n<body>\n" + INNER + "\n</body>\n</html>\n"
)
open(OUT_PAGES, "w", encoding="utf-8").write(PAGES)

print("OK artifact:", OUT_ARTIFACT)
print("OK pages   :", OUT_PAGES)
