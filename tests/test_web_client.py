"""The web client keeps its element contract and the loopback server serves its static files."""

import json
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

    def test_page_declares_one_canonical_url_matching_the_cname_host(self):
        links = re.findall(r'<link\s+rel="canonical"\s+href="([^"]+)"', self.html)
        self.assertEqual(1, len(links), 'exactly one canonical link is required')
        host = (WEB / 'CNAME').read_text(encoding='utf-8').strip()
        self.assertEqual(f'https://{host}/', links[0])

    def meta(self, attribute, value):
        return re.findall(rf'<meta\s+{attribute}="{re.escape(value)}"\s+content="([^"]*)"', self.html)

    def test_single_description_has_a_sensible_length(self):
        descriptions = self.meta('name', 'description')
        self.assertEqual(1, len(descriptions))
        self.assertTrue(70 <= len(descriptions[0]) <= 160, len(descriptions[0]))

    def test_page_declares_open_graph_and_twitter_cards(self):
        canonical = f"https://{(WEB / 'CNAME').read_text(encoding='utf-8').strip()}/"
        self.assertEqual(['website'], self.meta('property', 'og:type'))
        self.assertEqual([canonical], self.meta('property', 'og:url'))
        self.assertEqual(['NainWrite'], self.meta('property', 'og:site_name'))
        self.assertEqual(1, len(self.meta('property', 'og:title')))
        self.assertEqual(self.meta('name', 'description'), self.meta('property', 'og:description'))
        images = self.meta('property', 'og:image')
        self.assertEqual(1, len(images))
        self.assertTrue(images[0].startswith('https://'))
        self.assertEqual(['summary_large_image'], self.meta('name', 'twitter:card'))
        self.assertEqual(images, self.meta('name', 'twitter:image'))

    def test_page_links_the_author_and_has_one_h1(self):
        self.assertIn('<link rel="author" href="https://www.naindev.com/">', self.html)
        self.assertEqual(1, len(re.findall(r'<h1[\s>]', self.html)))

    def test_json_ld_describes_the_application_and_its_author(self):
        blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', self.html, flags=re.S)
        self.assertEqual(1, len(blocks))
        self.assertNotIn('<', blocks[0])
        data = json.loads(blocks[0])
        self.assertEqual('SoftwareApplication', data['@type'])
        self.assertEqual('https://write.naindev.com/', data['url'])
        self.assertEqual('Web', data['operatingSystem'])
        self.assertIs(True, data['isAccessibleForFree'])
        self.assertEqual('https://www.naindev.com/#person', data['author']['@id'])

    def test_markup_is_compatible_with_the_local_content_security_policy(self):
        self.assertIsNone(re.search(r'\son[a-z]+="', self.html), 'inline event handlers are blocked by CSP')
        self.assertIsNone(re.search(r'\sstyle="', self.html), 'inline style attributes are blocked by CSP')
        self.assertNotIn('<style', self.html)

    def test_referenced_modules_exist(self):
        for name in re.findall(r'(?:src|href)="\./([^"]+)"', self.html):
            self.assertTrue((WEB / name).is_file(), name)


class WebClientDiscoverabilityFileTests(unittest.TestCase):
    ORIGIN = f"https://{(WEB / 'CNAME').read_text(encoding='utf-8').strip()}/"

    def test_robots_txt_advertises_the_sitemap_and_blocks_nothing(self):
        lines = (WEB / 'robots.txt').read_text(encoding='utf-8').splitlines()
        self.assertIn('User-agent: *', lines)
        self.assertIn('Allow: /', lines)
        self.assertIn(f'Sitemap: {self.ORIGIN}sitemap.xml', lines)
        self.assertFalse([line for line in lines if line.startswith('Disallow: /')])

    def test_sitemap_lists_only_the_canonical_root(self):
        sitemap = (WEB / 'sitemap.xml').read_text(encoding='utf-8')
        self.assertEqual([self.ORIGIN], re.findall(r'<loc>([^<]*)</loc>', sitemap))

    def test_llms_txt_starts_with_an_h1_and_a_summary(self):
        text = (WEB / 'llms.txt').read_text(encoding='utf-8')
        self.assertTrue(text.startswith('# '))
        self.assertIn('\n> ', text)


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
