# etubedb-mock-server

Local HTTPS mock of the Shimano E-TUBE PROJECT API
(`https://etubedb.shimanoweb.com`) with a passthrough proxy to the real
backend.

## Purpose

The E-TUBE PROJECT Professional PC application calls the Shimano web API to
authenticate the operator (the "Shimano rep password" flow: an OEM ID /
password web login). This tool lets you run the app without a valid account
by faking the login endpoints locally while forwarding everything else to
the real Shimano API, so the rest of the application works normally.

## Modes

| Mode | `/v1/login` + `/v1/login/auto` | Everything else |
|------|-------------------------------|-----------------|
| `passthru-no-login` (default) | faked (login as `userType: 1`) | forwarded to the real API |
| `passthru` | forwarded | forwarded |
| `mock` | faked (login as `userType: 1`) | empty success responses |

`--passthru-no-login`, `--passthru`, and `--no-passthru` are mutually
exclusive. The default is `passthru-no-login`.

## Usage

```
python3 mock_etubedb.py [--host 127.0.0.1] [--port 443]
                        [--passthru | --passthru-no-login | --no-passthru]
                        [--no-bootstrap]
```

Run as Administrator (Windows) or root-ish user that can write `/etc/hosts`
so the bootstrap can add:

```
127.0.0.1  etubedb.shimanoweb.com
```

On Windows the script requests elevation automatically via UAC if not
already running as Administrator.

The hosts entry is added at startup if absent and removed again when the
tool exits (including Ctrl-C / terminate signals). A pre-existing entry is
left untouched.

### Bootstrap

The first run writes the embedded self-signed certificate
(`CN=etubedb.shimanoweb.com`) to `cert.pem` / `key.pem` and, on Windows,
imports it into the Trusted Root Certification Authorities store
(`certutil -addstore -f Root cert.pem`). Use `--no-bootstrap` to skip.

### Interactive keys

- `m` / `Tab` - cycle mode
- `1` / `2` / `3` - select mode (mock / passthru / passthru-no-login)
- `q` - quit

The current mode and key hints are shown in a status bar pinned to the
bottom of the terminal while the tool runs. When stdout is redirected the
status bar is disabled and output is plain text.

## How the passthrough works

Because the hosts file points `etubedb.shimanoweb.com` at `127.0.0.1`, the
forwarding path cannot use the system resolver. It queries public DNS over
HTTPS (DoH, via `1.1.1.1` / `dns.google`) for the real IP, opens a raw
socket, upgrades it to TLS with `server_hostname=etubedb.shimanoweb.com`
(SNI + real certificate validation), and relays the request/response over
that connection.

## Faking the login journal

In `passthru-no-login` mode the two authentication endpoints return a
`userType: 1` (Shimano 1) session, which the client application stores in
its login journal. If you need the application to trust the journal
entirely offline you can pre-place the encrypted journal files in the
application data directory:

- `_usnmkey.dat` - AES-128-CBC (key `bf1f1a85f82a0242e73be71d7a105f26`),
  16-byte IV prefix, UTF-16LE payload with four lines:
  `userID / password / userType / MAC`
- `AccessKey.dat` - plaintext bearer token, content irrelevant (existence
  only)

with a valid journal and any non-empty MAC the client can log in offline
even if the server never answers. See the application's `AutoLoginImpl`
logic for the exact conditions.

## Files

- `mock_etubedb.py` - the server (`CERT_PEM` / `KEY_PEM` embedded)
- `cert.pem`, `key.pem` - written transiently at startup for the TLS
  context and (on Windows) the root-store import, then deleted again once
  the server is running

Requires Python 3.7+. The keyboard handling uses raw ANSI terminal codes
(no curses dependency).