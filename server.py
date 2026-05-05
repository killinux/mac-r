"""
Windows 端 - 命令控制服务器
用法: python server.py [端口]
默认端口 8900
"""
import http.server
import json
import sys
import threading
import os

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8900

pending_cmd = {"cmd": ""}
results = []
lock = threading.Lock()


class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/cmd":
            with lock:
                cmd = pending_cmd["cmd"]
                pending_cmd["cmd"] = ""
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"cmd": cmd}).encode())

        elif self.path == "/results":
            with lock:
                data = list(results)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(data).encode())

        elif self.path == "/":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(PAGE.encode())
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == "/cmd":
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length))
            with lock:
                pending_cmd["cmd"] = body.get("cmd", "")
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"ok")

        elif self.path == "/result":
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length))
            with lock:
                results.append(body)
                if len(results) > 200:
                    results.pop(0)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"ok")
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, fmt, *args):
        pass


PAGE = r"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Mac Remote</title>
<style>
* { margin:0; padding:0; box-sizing:border-box; }
body { font-family: Consolas, monospace; background:#1e1e1e; color:#d4d4d4; height:100vh; display:flex; flex-direction:column; }
#output { flex:1; overflow-y:auto; padding:12px; white-space:pre-wrap; word-break:break-all; font-size:14px; }
.cmd-line { color:#569cd6; margin-top:8px; }
.out-line { color:#d4d4d4; }
.err-line { color:#f44747; }
.time-line { color:#6a9955; font-size:12px; }
#bar { display:flex; padding:8px; background:#252526; border-top:1px solid #333; }
#input { flex:1; background:#3c3c3c; color:#d4d4d4; border:1px solid #555; padding:8px 12px; font-family:inherit; font-size:14px; outline:none; }
#input:focus { border-color:#569cd6; }
#send { background:#0e639c; color:#fff; border:none; padding:8px 20px; cursor:pointer; font-family:inherit; font-size:14px; margin-left:6px; }
#status { padding:4px 12px; background:#007acc; color:#fff; font-size:12px; }
</style></head><body>
<div id="status">waiting for mac...</div>
<div id="output"></div>
<div id="bar">
  <input id="input" placeholder="输入命令..." autofocus />
  <button id="send">Run</button>
</div>
<script>
let seen = 0;
const out = document.getElementById('output');
const inp = document.getElementById('input');
const sts = document.getElementById('status');

function send() {
  const cmd = inp.value.trim();
  if (!cmd) return;
  fetch('/cmd', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({cmd})});
  inp.value = '';
}
document.getElementById('send').onclick = send;
inp.onkeydown = e => { if(e.key==='Enter') send(); };

function poll() {
  fetch('/results').then(r=>r.json()).then(data => {
    if (data.length > seen) {
      for (let i = seen; i < data.length; i++) {
        const r = data[i];
        out.innerHTML += `<div class="cmd-line">$ ${esc(r.cmd)}</div>`;
        if (r.stdout) out.innerHTML += `<div class="out-line">${esc(r.stdout)}</div>`;
        if (r.stderr) out.innerHTML += `<div class="err-line">${esc(r.stderr)}</div>`;
        out.innerHTML += `<div class="time-line">[exit ${r.code}]</div>`;
      }
      seen = data.length;
      out.scrollTop = out.scrollHeight;
      sts.textContent = 'mac online - last: ' + new Date().toLocaleTimeString();
    }
  }).catch(()=>{});
}
setInterval(poll, 1500);
</script></body></html>"""

if __name__ == "__main__":
    print(f"Server running on 0.0.0.0:{PORT}")
    print(f"Open http://localhost:{PORT} in browser")
    server = http.server.HTTPServer(("0.0.0.0", PORT), Handler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
