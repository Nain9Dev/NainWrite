"""The web client keeps its element contract and the loopback server serves its static files."""

import re
import sys
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from spanish_rewriter.workbench import Workbench
from spanish_rewriter.workbench_http import create_server

WEB = Path(__file__).resolve().parents[1] / 'src' / 'spanish_rewriter' / 'web'

REQUIRED_IDS = {
    'mode', 'night-start', 'night-end', 'save-settings', 'pause', 'upload-form', 'uploads', 'assets',
    'documents', 'notice', 'empty', 'document', 'stage', 'title', 'progress', 'error', 'refresh', 'resume',
    'original', 'extraction-section', 'pages', 'extraction', 'extraction-actions', 'save-extraction',
    'extraction-note', 'complete', 'approve-extraction', 'spanish-section', 'spanish', 'save-spanish',
    'review-spanish', 'diff', 'review', 'translation-actions', 'spanish-note', 'resolved', 'acknowledge',
    'translate', 'exports-section', 'exports',
}


class WebClientMarkupTests(unittest.TestCase):
    def setUp(self):
        self.html = (WEB / 'index.html').read_text(encoding='utf-8')

    def test_editorial_element_ids_are_present(self):
        found = set(re.findall(r'\sid="([^"]+)"', self.html))
        self.assertEqual(set(), REQUIRED_IDS - found)

    def test_markup_is_compatible_with_the_local_content_security_policy(self):
        self.assertIsNone(re.search(r'\son[a-z]+="', self.html), 'inline event handlers are blocked by CSP')
        self.assertIsNone(re.search(r'\sstyle="', self.html), 'inline style attributes are blocked by CSP')
        self.assertNotIn('<style', self.html)

    def test_referenced_modules_exist(self):
        for name in re.findall(r'(?:src|href)="\./([^"]+)"', self.html):
            self.assertTrue((WEB / name).is_file(), name)


class WebClientStaticServingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.server = create_server(Workbench(self.temp.name), port=0)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.addCleanup(self.server.server_close)
        self.addCleanup(self.server.shutdown)
        self.base = f'http://127.0.0.1:{self.server.server_port}'
        self.open = urllib.request.build_opener(urllib.request.ProxyHandler({})).open

    def test_every_module_and_asset_in_the_web_directory_is_served(self):
        for path in sorted(WEB.iterdir()):
            if path.suffix not in {'.js', '.css', '.svg'}:
                continue
            with self.open(self.base + '/' + path.name) as response:
                self.assertEqual(200, response.status, path.name)
                self.assertEqual(path.read_bytes(), response.read(), path.name)
                expected = {'.js': 'text/javascript', '.css': 'text/css', '.svg': 'image/svg+xml'}[path.suffix]
                self.assertTrue(response.headers['Content-Type'].startswith(expected), path.name)

    def test_paths_outside_the_web_directory_are_refused(self):
        for path in ('/../workbench_http.py', '/web/../workbench.py', '/index.html', '/CNAME', '/missing.js'):
            with self.assertRaises(urllib.error.HTTPError, msg=path) as error:
                self.open(self.base + path)
            self.assertEqual(404, error.exception.code, path)


if __name__ == '__main__':
    unittest.main()
