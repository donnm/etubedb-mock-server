import os, ssl, json, sys, http.client, socket, argparse, atexit, threading, time, signal
import urllib.request, urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer

try:
    import termios, tty, select
    _POSIX = True
except ImportError:
    _POSIX = False

# ---- embedded TLS identity for etubedb.shimanoweb.com ----
CERT_PEM = """-----BEGIN CERTIFICATE-----
MIIDIzCCAgugAwIBAgIUDKPoN5qnpzsrdihWg2avNBIjgc8wDQYJKoZIhvcNAQEL
BQAwITEfMB0GA1UEAwwWZXR1YmVkYi5zaGltYW5vd2ViLmNvbTAeFw0yNjA5MDgw
OTQ4MjBaFw0yNzA5MDgwOTQ4MjBaMCExHzAdBgNVBAMMFmV0dWJlZGIuc2hpbWFu
b3dlYi5jb20wggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQDbfUZcNbQ7
xQTDJV80zlUOibiFID6W+xUo9hpdUE6/pUds5rSd9nIes+93SqK/hXMtbvBKhb62
hfIs/Vw7qSYtXh6wAjLT0zqL7miwg683cfabnMZ7lswiRtwA8vPo0uG4qBqvwLma
eq2eAVgxGcrAsdDcU1wFxc712NNte430+xaUsburT0r4aO31xS7Tbnz8WlmLfvRZ
8BCOFyZnc6k31JoJBW4sSo7NoC4p0uOIKpOxwRCZ1QjGk1pwDQ489gJW44SO7q7X
yI/I12bi9e8stdjdIMChzTTZlziCZinIH4k8koY0rVIQAgsuoBR7jF36VoIEGIbq
zZoUg2oN8eVrAgMBAAGjUzBRMB0GA1UdDgQWBBThiqchJ4xbHWaZLvPpoeqkN5QZ
kjAfBgNVHSMEGDAWgBThiqchJ4xbHWaZLvPpoeqkN5QZkjAPBgNVHRMBAf8EBTAD
AQH/MA0GCSqGSIb3DQEBCwUAA4IBAQCrSpQ1xKi0o+lmCx+aN01wpUK3E2OvCO5M
tM7gSpw3f91HCv5X+zw0r4CSxqWiwN0eQVxhUmOJoPt96u8sunvC7COEWvQL3qIq
vGoSz8k5pGQ5Qv6e+dYspIARRzq9JsqVFqg7HbShsI8Gel2oHnT/ALyUc+tjpOMJ
ZqEWeSJWivyrC/S5PX6E8S3iFDA5mP6syri3n7k1L5exgAUfMfKFlpr2cyfmTJyl
uVsrPwwfA2OwhxAb6AVjiNi/FzG5M2XULbTqi04eITM9KvsfKRXPMbV7GZaqSi6M
NEI/zuVVdzMuqw3WuCEKStXoqVTpAzfFwfb9EwARj2bR8LGV0DDS
-----END CERTIFICATE-----"""

KEY_PEM = """-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDbfUZcNbQ7xQTD
JV80zlUOibiFID6W+xUo9hpdUE6/pUds5rSd9nIes+93SqK/hXMtbvBKhb62hfIs
/Vw7qSYtXh6wAjLT0zqL7miwg683cfabnMZ7lswiRtwA8vPo0uG4qBqvwLmaeq2e
AVgxGcrAsdDcU1wFxc712NNte430+xaUsburT0r4aO31xS7Tbnz8WlmLfvRZ8BCO
FyZnc6k31JoJBW4sSo7NoC4p0uOIKpOxwRCZ1QjGk1pwDQ489gJW44SO7q7XyI/I
12bi9e8stdjdIMChzTTZlziCZinIH4k8koY0rVIQAgsuoBR7jF36VoIEGIbqzZoU
g2oN8eVrAgMBAAECggEAR3Wk57aQZHlDkKllMtMOfDo4ehdCaXN7sydU9BaGXPzZ
oUoHefpXs0lP6J3DGOnA0wTwdMLQkapQa3ddhQsQI+slwJYmqDJ4OEC5kuZ8sGeJ
K6bCNFCnS22YiTKQWLf3x1/ruFbd1r6kMfIsHWhRS6VY47K8HiEFvaMHSvjUAfL2
99emDC/IriPN1NqG2NMp7Q0ygcMjr2euRVAhmMsil8WLJ8b9bQXgbNZ/lMJAeIme
GiqjhUBWpW4bab0DS1Lv/boyeyIzxsllvYOxv58S7eM+lPOWLnL6fc2rJI8mBcgX
EUcl7Pahd6rzuRMzdmaLa9rouYmn3i5ceIBpLzKGcQKBgQD9bn05UmmYVV0+WFkT
lrpbm42faejlmxwg6+6ukn4PjKwRt5OR4PEqIIHerGj5c2jRhHwOdG4Z7PvuaiFy
BezmiO+OxkRXC6hEVv49P50L1dXaEMMoC0u/XGmnDaqSDdN6Fu6pxFbp6o7hkKgL
shP5DPvq5Ns5EXB4sf0B5+mlgwKBgQDdtrmRT4dlRm2BajwbMmjGOio1U5X33u4S
S6j9t79jki1O/Pct3j+RffGEZdDXiOhofq29/LTuzgQ1itckLv6CuhHz0v/adH26
c2D55P11B+Djt3OAsAX9JvufFTnHry+HpmAYI6PZLN8dhdeJlvJnRiJ4EOW57a+A
HDfxr4Uj+QKBgBNUxTqFHcbf5A/oX0sOOULZl7DsPDafYULlnDw2smTvPwTO8vOy
q9KhziY1EoDMm9c3etsDaI6TtBfYgpqW9x4SnetPFlFpczlbRWNYodsQQZKzqp84
VVvQacKzWSpw4Yuzihrq/hIzsRhll1vlBn79zY16TXqJ6QFb2ke17+2PAoGAOO7c
FgljDkmYgxwBlUZLi2OSRSFSqFTxs3cETSqrFemKgvcIjhm9HyJFK6dtintYmsS0
3s2OtKfogstFVcBPkMgxJfhvxOwXARLxuxnnT+8W+8K3ATuyPgCNqpsrvDArN10s
3eYBBBq2rIEbCPTfCFAFN+m25Bi58V7Nqt1UhhkCgYEAvxAzgCUAOm5uenwFGxfK
D5zAaF7wkJBleXumNHxquZL1I6LxBSPZYssoTes863Uat0gphbUZmnvn3yP1SRoM
x2u8VJrYmMiaOrQLTvzy/PbfAp4/CcM6Oij8lP0tVu1rN7sM6D5M0JeIFa/x1gRR
WLYFYMXv5AzlkEXoS8iMNLE=
-----END PRIVATE KEY-----"""

HOST = "etubedb.shimanoweb.com"
LOGIN = {"userID": "shimano", "uid": "shimano", "userType": "1",
         "tempPassAuthFlg": "0", "passwordExpiredFlg": "0",
         "accessKey": "mock-access-key"}
AUTO = {"userID": "shimano", "userType": "1", "passwordExpiredFlg": "0"}
EMPTY = {}

MODES = ("mock", "passthru", "passthru-no-login")
MODE = "passthru-no-login"
PASSTHRU_ALL = False
PASSTHRU_NO_LOGIN = True
REAL_IP = None
HOSTS_ADDED = False
_orig_term = None


# ---- tiny terminal helpers (raw ANSI codes, no curses) ----
TTY = sys.stdout.isatty()


def _term_size():
    try:
        c = os.get_terminal_size()
        return max(c.lines, 2), c.columns
    except Exception:
        return 25, 80


def _fit(msg, cols):
    if not cols or cols <= 1:
        return msg
    lines = []
    for piece in msg.split("\n"):
        while len(piece) > cols:
            lines.append(piece[:cols])
            piece = piece[cols:]
        lines.append(piece)
    return "\n".join(lines)


def _bar():
    labels = {"mock": "MOCK (all mocked)", "passthru": "PASSTHRU (all real API)",
              "passthru-no-login": "PASSTHRU-NO-LOGIN (login mocked, rest real)"}
    return ("  mode: %s   [m]/[Tab] next   [1] mock   [2] passthru   "
            "[3] passthru-no-login   [q] quit  " % labels[MODE])


def enable_vt():
    if sys.platform == "win32":
        try:
            import ctypes
            k = ctypes.windll.kernel32
            h = k.GetStdHandle(-11)
            m = ctypes.c_uint32()
            k.GetConsoleMode(h, ctypes.byref(m))
            k.SetConsoleMode(h, m.value | 0x0004)  # ENABLE_VIRTUAL_TERMINAL_PROCESSING
        except Exception:
            pass


def apply_region():
    rows, _ = _term_size()
    sys.stdout.write("\x1b[1;%dr" % max(1, rows - 1))   # DECSTBM: logs scroll above the bar
    sys.stdout.flush()


def paint_status():
    if not TTY:
        return
    rows, cols = _term_size()
    bar = _bar()
    if cols:
        bar = bar[:max(1, cols - 1)]                    # never wrap onto/under the log area
    apply_region()
    sys.stdout.write("\x1b[%d;1H\x1b[2K%s" % (rows, bar))
    sys.stdout.write("\x1b[%d;1H" % max(1, rows - 1))   # park cursor at region bottom
    sys.stdout.flush()


def setup_scroll_region():
    if not TTY:
        return
    sys.stdout.write("\x1b[1;1H\x1b[J")                 # clear whole viewport once
    apply_region()
    paint_status()


def say(*a):
    msg = " ".join(str(x) for x in a)
    if TTY:
        _, cols = _term_size()
        msg = _fit(msg, cols)
    sys.stdout.write(msg + "\n")
    sys.stdout.flush()
    if TTY:
        rows, _ = _term_size()
        sys.stdout.write("\x1b[%d;1H" % max(1, rows - 1))
        sys.stdout.flush()
        paint_status()


def set_mode(n):
    global MODE, PASSTHRU_ALL, PASSTHRU_NO_LOGIN
    MODE = MODES[n - 1]
    PASSTHRU_ALL = MODE == "passthru"
    PASSTHRU_NO_LOGIN = MODE == "passthru-no-login"
    paint_status()


def cycle_mode():
    set_mode((MODES.index(MODE) + 1) % len(MODES) + 1)


# ---- self-elevation (Windows UAC) ----
def ensure_admin():
    if sys.platform != "win32":
        return
    try:
        import ctypes
        if ctypes.windll.shell32.IsUserAnAdmin():
            return
    except Exception:
        return
    say("[*] not running as Administrator - requesting elevation...")
    import subprocess
    python = sys.executable
    script = os.path.abspath(__file__)
    args = subprocess.list2cmdline(sys.argv[1:])
    cmd = '"%s" "%s"%s' % (python, script, args and " " + args)
    ps = "Start-Process -Verb RunAs -FilePath '%s' -ArgumentList '%s'" % (
        python, '"%s"%s' % (script, args and " " + args))
    try:
        subprocess.run(["powershell", "-NoProfile", "-Command", ps], timeout=10,
                       capture_output=True)
    except Exception:
        pass
    sys.exit(0)


# ---- hosts entry lifecycle ----
def hosts_path():
    if sys.platform == "win32":
        return os.path.join(os.environ.get("SystemRoot", r"C:\Windows"),
                            "System32", "drivers", "etc", "hosts")
    return "/etc/hosts"


def flush_dns():
    if sys.platform == "win32":
        os.system("ipconfig /flushdns")


def bootstrap_hosts():
    global HOSTS_ADDED
    path = hosts_path()
    if not os.access(path, os.W_OK):
        say("[!] no write access to %s - add manually:" % path)
        say("    127.0.0.1  %s" % HOST)
        return
    with open(path, "r", errors="replace") as f:
        text = f.read()
    if HOST in text:
        say("[*] %s already present in %s" % (HOST, path))
        return
    with open(path, "a") as f:
        f.write("\n127.0.0.1  %s\n" % HOST)
    HOSTS_ADDED = True
    say("[+] added 127.0.0.1 %s -> %s" % (HOST, path))
    flush_dns()


def remove_hosts_entry():
    global HOSTS_ADDED
    if not HOSTS_ADDED:
        return
    path = hosts_path()
    try:
        with open(path, "r", errors="replace") as f:
            lines = f.readlines()
        keep = [l for l in lines if HOST not in l]
        if len(keep) != len(lines):
            with open(path, "w") as f:
                f.writelines(keep)
            HOSTS_ADDED = False
            say("[+] removed %s from %s" % (HOST, path))
            flush_dns()
        else:
            HOSTS_ADDED = False
    except Exception as e:
        say("[!] could not remove hosts entry: %s" % e)


atexit.register(remove_hosts_entry)


# ---- cert bootstrap ----
def write_identity():
    cert, key = "cert.pem", "key.pem"
    for path, pem in ((cert, CERT_PEM), (key, KEY_PEM)):
        if not os.path.exists(path):
            with open(path, "w") as f:
                f.write(pem)
    return cert, key


def bootstrap_cert(certfile):
    if sys.platform != "win32":
        return
    import subprocess
    certutil = os.path.join(os.environ.get("SystemRoot", r"C:\Windows"),
                            "System32", "certutil.exe")
    r = subprocess.run([certutil, "-addstore", "-f", "Root", os.path.abspath(certfile)],
                       capture_output=True, text=True)
    if r.returncode == 0:
        say("[+] imported cert into Trusted Root Certification Authorities")
    else:
        say("[!] cert import failed:")
        say("    %s -addstore -f Root cert.pem" % certutil)
        say(r.stderr.strip()[:400])


def remove_pems():
    removed = []
    for p in ("cert.pem", "key.pem"):
        if os.path.exists(p):
            try:
                os.remove(p)
                removed.append(p)
            except Exception:
                pass
    if removed:
        say("[+] cleaned up %s" % ", ".join(removed))


# ---- passthru backend ----
def resolve_real_ip():
    global REAL_IP
    if REAL_IP:
        return REAL_IP
    ips = []
    for doh in ("https://1.1.1.1/dns-query", "https://dns.google/resolve"):
        try:
            q = doh + "?name=" + urllib.parse.quote(HOST) + "&type=A"
            req = urllib.request.Request(q, headers={"Accept": "application/dns-json"})
            with urllib.request.urlopen(req, timeout=5) as r:
                js = json.load(r)
            ips = [a.get("data") for a in js.get("Answer", []) if a.get("type") == 1]
            if ips:
                break
        except Exception:
            continue
    if not ips:
        try:
            ips = [socket.gethostbyname(HOST)]
        except Exception:
            ips = []
    for ip in ips:
        if ip and not ip.startswith("127.") and ip != "0.0.0.0":
            REAL_IP = ip
            return ip
    return ips[0] if ips else None


def forward_conn():
    ip = resolve_real_ip() or HOST
    ctx = ssl.create_default_context()
    raw = socket.create_connection((ip, 443), timeout=10)
    tls = ctx.wrap_socket(raw, server_hostname=HOST)
    conn = http.client.HTTPConnection(HOST, 443, timeout=15)
    conn.sock = tls
    return conn


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def _body(self):
        n = int(self.headers.get("Content-Length", 0) or 0)
        return self.rfile.read(n) if n else b""

    def _passthru_if_enabled(self):
        mocked = self.path.endswith("/v1/login") or self.path.endswith("/v1/login/auto")
        passthru_this = PASSTHRU_ALL or (PASSTHRU_NO_LOGIN and not mocked)
        if passthru_this:
            self.passthru()
            return True
        return False

    def passthru(self):
        try:
            body = self._body()
            headers = {k: v for (k, v) in self.headers.items()
                       if k.lower() not in ("host", "content-length",
                                            "connection", "transfer-encoding",
                                            "proxy-connection")}
            conn = forward_conn()
            conn.request(self.command, self.path, body=body, headers=headers)
            resp = conn.getresponse()
            data = resp.read()
            say("[passthru] %s %s -> %s" % (self.command, self.path, resp.status))
            try:
                parsed = json.loads(data.decode("utf-8"))
                say("    <- %d %s" % (resp.status, json.dumps(parsed)[:2000]))
            except Exception:
                say("    <- %d %s" % (resp.status, data.decode("utf-8", "replace")[:2000]))
            self.send_response(resp.status, resp.reason)
            for k, v in resp.getheaders():
                if k.lower() in ("connection", "transfer-encoding", "content-length"):
                    continue
                self.send_header(k, v)
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            if data:
                self.wfile.write(data)
            conn.close()
        except Exception as e:
            say("[passthru] ERROR %s %s: %s" % (self.command, self.path, e))
            err = json.dumps({"message": "passthru failed", "code": 502}).encode()
            self.send_response(502)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(err)))
            self.end_headers()
            self.wfile.write(err)

    def _send(self, code, obj):
        say("    <- %d %s" % (code, json.dumps(obj)))
        data = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_POST(self):
        if self._passthru_if_enabled():
            return
        body = self._body()
        say("POST %s\n  %s" % (self.path, body.decode(errors="replace")))
        if self.path.endswith("/v1/login"):
            self._send(200, LOGIN)
        elif self.path.endswith("/v1/login/auto"):
            self._send(200, AUTO)
        elif self.path.endswith("/v1/regulation_agreements") or \
             self.path.endswith("/unit_components") or \
             self.path.endswith("/unit_components/oem") or \
             self.path.endswith("/unit_components/oem/search") or \
             self.path.endswith("/unit_components/oem/count") or \
             self.path.endswith("/v1/my_bikes/no_login") or \
             self.path.endswith("/v1/corporate_users/notify"):
            self._send(200, EMPTY)
        else:
            self._send(404, {"message": "not found", "code": 404})

    def do_GET(self):
        if self._passthru_if_enabled():
            return
        say("GET  %s" % self.path)
        if self.path.startswith("/v1/regulation_agreements") or \
           self.path.startswith("/v1/country_code"):
            self._send(200, EMPTY)
        elif self.path.startswith("/v1/continents"):
            self._send(200, {"continents": []})
        else:
            self._send(404, {"message": "not found", "code": 404})

    def do_PUT(self):
        if self._passthru_if_enabled():
            return
        say("PUT  %s" % self.path)
        self._send(200, EMPTY)

    def do_DELETE(self):
        if self._passthru_if_enabled():
            return
        say("DEL  %s" % self.path)
        self._send(200, EMPTY)


def cleanup():
    if _POSIX and _orig_term is not None:
        try:
            termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, _orig_term)
        except Exception:
            pass
    try:
        if TTY:
            rows, _ = _term_size()
            sys.stdout.write("\x1b[?25h\x1b[r\x1b[%d;1H\x1b[2K" % rows)
            sys.stdout.flush()
    except Exception:
        pass
    remove_hosts_entry()


def _winch_handler(signum, frame):
    try:
        apply_region()
        paint_status()
    except Exception:
        pass


def _signal_handler(signum, frame):
    try:
        say("")
        say("[!] signal %d received - cleaning up" % signum)
    except Exception:
        pass
    cleanup()
    os._exit(0)


# ---- interactive key handling ----
def read_keys(httpd):
    fd = sys.stdin.fileno()
    old = None
    if _POSIX:
        try:
            old = termios.tcgetattr(fd)
            tty.setraw(fd)
        except Exception:
            old = None
    try:
        while True:
            if _POSIX:
                r, _, _ = select.select([sys.stdin], [], [], 0.2)
                if not r:
                    continue
                ch = os.read(fd, 1).decode("latin1")
            else:
                import msvcrt
                if not msvcrt.kbhit():
                    time.sleep(0.1)
                    continue
                ch = msvcrt.getwch()
            if ch in ("\x03", "q", "Q"):
                say("[*] quitting...")
                httpd.shutdown()
                break
            elif ch in ("m", "M", "\t"):
                cycle_mode()
                say("[*] mode: %s" % MODE)
            elif ch in ("1", "2", "3"):
                set_mode(int(ch))
                say("[*] mode: %s" % MODE)
    finally:
        if _POSIX and old is not None:
            try:
                termios.tcsetattr(fd, termios.TCSADRAIN, old)
            except Exception:
                pass


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=443)
    ap.add_argument("--no-bootstrap", action="store_true")
    passthru = ap.add_mutually_exclusive_group()
    passthru.add_argument("--passthru", action="store_true",
                          help="forward every request to the real Shimano API")
    passthru.add_argument("--passthru-no-login", action="store_true",
                          help="forward everything except /v1/login and /v1/login/auto "
                               "(default)")
    passthru.add_argument("--no-passthru", action="store_true",
                          help="mock all endpoints instead of forwarding")
    a = ap.parse_args()

    enable_vt()
    setup_scroll_region()

    if a.no_passthru:
        set_mode(1)
    elif a.passthru:
        set_mode(2)
    else:
        set_mode(3)  # default: passthru-no-login (mock login, forward the rest)

    ensure_admin()

    if _POSIX:
        global _orig_term
        try:
            _orig_term = termios.tcgetattr(sys.stdin.fileno())
        except Exception:
            _orig_term = None

    signal.signal(signal.SIGINT, _signal_handler)
    for _sig in (signal.SIGTERM, getattr(signal, "SIGHUP", None)):
        if _sig is None:
            continue
        try:
            signal.signal(_sig, _signal_handler)
        except (ValueError, AttributeError, OSError):
            pass
    _winch = getattr(signal, "SIGWINCH", None)
    if _winch is not None:
        try:
            signal.signal(_winch, _winch_handler)
        except (ValueError, AttributeError, OSError):
            pass

    if not a.no_bootstrap:
        bootstrap_hosts()
        cert, _ = write_identity()
        bootstrap_cert(cert)
    else:
        cert, _ = write_identity()

    try:
        httpd = HTTPServer((a.host, a.port), Handler)
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ctx.load_cert_chain(cert, write_identity()[1])
        httpd.socket = ctx.wrap_socket(httpd.socket, server_side=True)
    except OSError as e:
        say("[!] cannot bind %s:%s - %s" % (a.host, a.port, e))
        sys.exit(1)

    remove_pems()

    say("[*] mock etubedb on https://%s:%s (mode: %s)" % (a.host, a.port, MODE))
    t = threading.Thread(target=read_keys, args=(httpd,), daemon=True)
    t.start()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()
        cleanup()


if __name__ == "__main__":
    main()