from __future__ import annotations

import argparse
from http.server import BaseHTTPRequestHandler, HTTPServer
import json

from family_care_review_ui.app import FamilyCareReviewSession


HTML = r'''<!doctype html><html lang="de"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Guardian Family Care Review</title><style>
:root{color-scheme:light;--bg:#f4f3ef;--card:#fff;--ink:#22302d;--muted:#65706d;--line:#d9ddd8;--accent:#386a5b;--warn:#8a5a24}*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.5 system-ui,sans-serif}header{padding:24px 32px;background:#203d35;color:white}header p{margin:4px 0 0;color:#d5e3dd}.wrap{max-width:1280px;margin:auto;padding:24px}.toolbar{display:flex;gap:12px;align-items:center;margin-bottom:18px}.badge{padding:5px 9px;border-radius:999px;background:#e5eee9;color:#295347;font-weight:700}.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px}.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:18px}.wide{grid-column:1/-1}h2{font-size:17px;margin:0 0 12px}h3{font-size:14px;margin:14px 0 4px;color:var(--muted)}ul{margin:4px 0;padding-left:20px}.question{border-left:4px solid var(--accent);padding:12px;background:#edf5f1;font-size:18px}.warning{border-left-color:var(--warn);background:#faf1e7}button{border:0;border-radius:7px;padding:10px 15px;background:var(--accent);color:white;font-weight:700;cursor:pointer}button.secondary{background:#65706d}button:disabled{opacity:.45}.chain{display:grid;grid-template-columns:repeat(3,1fr);gap:8px}.chain div{background:#f5f7f5;padding:9px;border-radius:6px}.label{display:block;color:var(--muted);font-size:12px}details{margin-top:16px}code{word-break:break-all}@media(max-width:800px){.grid{grid-template-columns:1fr}.chain{grid-template-columns:1fr}.wide{grid-column:auto}}</style></head><body><header><h1>Guardian Family Care Review UI</h1><p>Internes, lokales Prüfwerkzeug · keine Produktionsoberfläche</p></header><main class="wrap"><div class="toolbar"><span id="notice" class="badge"></span><span id="progress"></span><button id="next">Vorbereiteten Schritt anwenden</button><button id="reset" class="secondary">Zurücksetzen</button></div><div id="app"></div></main><script>
const esc=v=>String(v??'nicht vorhanden').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));const display=x=>typeof x==='object'?Object.values(x).flat().join(' · '):x;const list=a=>a&&a.length?`<ul>${a.map(x=>`<li>${esc(display(x))}</li>`).join('')}</ul>`:'<p>nicht vorhanden</p>';async function load(){const s=await fetch('/api/state').then(r=>r.json());document.querySelector('#notice').textContent=s.case.notice;document.querySelector('#progress').textContent=`Schritt ${s.case.step} von ${s.case.total_steps}`;document.querySelector('#next').disabled=!s.conversation.can_advance;const c=s.source_chain;document.querySelector('#app').innerHTML=`<div class="grid"><section class="card wide"><h2>${esc(s.journey.heading)}</h2><p>${esc(s.journey.description)}</p>${s.conversation.current_question?`<div class="question"><span class="label">Aktive Lücke</span>${esc(s.conversation.current_gap)}<hr><span class="label">Genau eine kontrollierte Frage</span>${esc(s.conversation.current_question)}<h3>Vorbereitete typisierte Antwort</h3>${esc(s.conversation.prepared_answer)}</div>`:'<div class="question">Keine aktuelle Guardian-Frage.</div>'}</section><section class="card"><h2>Understanding</h2><h3>Facts</h3>${list(s.understanding.facts)}<h3>Hypotheses</h3>${list(s.understanding.hypotheses)}<h3>Unknowns</h3>${list(s.understanding.unknowns)}<h3>Contradictions</h3>${list(s.understanding.contradictions)}<h3>Goals</h3>${list(s.understanding.goals)}</section><section class="card"><h2>Cross-Domain</h2><h3>Contributions</h3>${list(s.cross_domain.contributions)}<h3>Dependencies</h3>${list(s.cross_domain.dependencies)}<h3>Personen und Rollen</h3>${list(s.cross_domain.people)}<h3>Dokumentreferenzen</h3>${list(s.cross_domain.documents)}</section><section class="card"><h2>Journey und Review</h2><h3>Status</h3><p>${esc(s.journey.status)}</p><h3>Beantwortet</h3>${list(s.cross_domain.answered_points)}<h3>Offen oder zurückgestellt</h3>${list([...s.cross_domain.open_points,...s.cross_domain.deferred_points])}<h3>Professional Reviews</h3>${list(s.cross_domain.reviews)}<h3>Organisatorische Schritte</h3>${list(s.cross_domain.steps)}</section><section class="card"><h2>Fachliche Grenzen</h2>${list(s.journey.boundaries)}<h3>Zulässige Aktionen</h3>${list(s.journey.allowed_actions)}</section><section class="card wide"><h2>Quellenkette des letzten Schritts</h2><div class="chain">${Object.entries(c).map(([k,v])=>`<div><span class="label">${esc(k)}</span>${esc(Array.isArray(v)?v.join(', '):v)}</div>`).join('')}</div><details><summary>Technische Referenzen</summary><pre>${esc(JSON.stringify(s.debug,null,2))}</pre></details></section></div>`}async function post(path){await fetch(path,{method:'POST'});await load()}document.querySelector('#next').onclick=()=>post('/api/advance');document.querySelector('#reset').onclick=()=>post('/api/reset');load();</script></body></html>'''


class ReviewHandler(BaseHTTPRequestHandler):
    session = FamilyCareReviewSession()

    def do_GET(self):
        if self.path == "/": return self._send(HTML, "text/html; charset=utf-8")
        if self.path == "/api/state": return self._json(self.session.view())
        self.send_error(404)

    def do_POST(self):
        if self.path == "/api/advance": return self._json(self.session.advance())
        if self.path == "/api/reset": return self._json(self.session.reset())
        self.send_error(404)

    def log_message(self, format, *args):
        return

    def _json(self, value):
        self._send(json.dumps(value, ensure_ascii=False, separators=(",", ":")), "application/json; charset=utf-8")

    def _send(self, value, content_type):
        data = value.encode("utf-8"); self.send_response(200); self.send_header("Content-Type", content_type); self.send_header("Cache-Control", "no-store"); self.send_header("Content-Length", str(len(data))); self.end_headers(); self.wfile.write(data)


def main():
    parser = argparse.ArgumentParser(description="Start the local Family Care review UI.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    print("Family Care Review UI: http://{}:{} (Ctrl-C beendet)".format(args.host, args.port))
    server = HTTPServer((args.host, args.port), ReviewHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
