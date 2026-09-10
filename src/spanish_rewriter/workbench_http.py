"""Loopback-only HTTP presentation adapter for the local workbench service."""

import base64
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import mimetypes
from pathlib import Path
import secrets
from urllib.parse import parse_qs, urlsplit


def create_server(workbench, *, port=8765):
    static_root = Path(__file__).parent / 'web'

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def _send(self, status, data, kind='application/json; charset=utf-8'):
            self.send_response(status)
            self.send_header('Content-Type', kind)
            self.send_header('Content-Length', str(len(data)))
            self.send_header('Cache-Control', 'no-store')
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.send_header('Referrer-Policy', 'no-referrer')
            self.send_header('X-Frame-Options', 'DENY')
            self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' blob:; connect-src 'self'; object-src 'none'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'")
            self.end_headers()
            self.wfile.write(data)

        def _json(self, status, value):
            self._send(status, json.dumps(value, ensure_ascii=False).encode('utf-8'))

        def _guard(self, *, private):
            allowed = {f'127.0.0.1:{self.server.server_port}', f'localhost:{self.server.server_port}'}
            if self.headers.get('Host') not in allowed:
                raise PermissionError('Unexpected local host')
            origin = self.headers.get('Origin')
            if origin and origin not in {'http://' + host for host in allowed}:
                raise PermissionError('Cross-origin requests are forbidden')
            if self.headers.get('Sec-Fetch-Site') == 'cross-site':
                raise PermissionError('Cross-site requests are forbidden')
            if private and not secrets.compare_digest(self.headers.get('X-NainWrite-Token', ''), self.server.token):
                raise PermissionError('Local application token is required')

        def do_GET(self):
            try:
                parsed = urlsplit(self.path)
                self._guard(private=parsed.path.startswith('/api/'))
                query = parse_qs(parsed.query)
                if parsed.path == '/':
                    text = (static_root / 'index.html').read_text(encoding='utf-8')
                    self._send(200, text.replace('__TOKEN__', self.server.token).encode('utf-8'), 'text/html; charset=utf-8')
                elif parsed.path in {'/app.js', '/app.css'}:
                    kind = 'text/javascript' if parsed.path.endswith('.js') else 'text/css'
                    self._send(200, (static_root / parsed.path[1:]).read_bytes(), kind + '; charset=utf-8')
                elif parsed.path == '/api/state':
                    self._json(200, workbench.summary())
                elif parsed.path == '/api/document':
                    self._json(200, workbench.detail(query.get('id', [''])[0]))
                elif parsed.path == '/api/file':
                    name = query.get('path', [''])[0]
                    raw = workbench.read_artifact(name)
                    kind = 'image/png' if name.endswith('.png') else 'application/octet-stream'
                    self._send(200, raw, kind)
                else:
                    self._json(404, {'error': 'Recurso no encontrado'})
            except PermissionError as error:
                self._json(403, {'error': str(error)})
            except (ValueError, OSError, KeyError, TypeError) as error:
                self._json(400, {'error': str(error)})

        def do_POST(self):
            try:
                self._guard(private=True)
                if self.path != '/api/action' or self.headers.get_content_type() != 'application/json':
                    raise ValueError('Expected a JSON application action')
                size = int(self.headers.get('Content-Length', '0'))
                if not 0 < size <= 140 * 1024 * 1024:
                    raise ValueError('Request exceeds the local upload limit')
                data = json.loads(self.rfile.read(size))
                if not isinstance(data, dict):
                    raise ValueError('Invalid action object')
                action = data.pop('action', None)
                if action == 'upload':
                    raw = base64.b64decode(data['content'], validate=True)
                    assets = [(a['name'], base64.b64decode(a['content'], validate=True)) for a in data.get('assets', [])]
                    key = workbench.upload(data['name'], raw, assets)
                    self._json(200, {'id': key}); return
                routes = {'settings': workbench.settings, 'edit_extraction': workbench.edit_extraction,
                          'accept_extraction': workbench.accept_extraction, 'edit_spanish': workbench.edit_spanish,
                          'review_spanish': workbench.review_spanish, 'translate': workbench.translate,
                          'approve_final': workbench.approve_final, 'resume': workbench.resume}
                if action not in routes:
                    raise ValueError('Unknown application action')
                routes[action](**data)
                self._json(200, {'ok': True})
            except PermissionError as error:
                self._json(403, {'error': str(error)})
            except (ValueError, OSError, KeyError, TypeError) as error:
                self._json(400, {'error': str(error)})

    server = ThreadingHTTPServer(('127.0.0.1', port), Handler)
    server.token = secrets.token_urlsafe(32)
    server.daemon_threads = True
    return server
