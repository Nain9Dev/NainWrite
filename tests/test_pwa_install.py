"""The published page is installable: manifest, icons and head tags (PWA-001 to PWA-004)."""

import json
import re
import struct
import unittest
from pathlib import Path

WEB = Path(__file__).resolve().parents[1] / 'src' / 'spanish_rewriter' / 'web'
PNG_SIGNATURE = b'\x89PNG\r\n\x1a\n'


def png_size(path):
    """Read width and height from the IHDR chunk, so the test needs no image library."""
    header = path.read_bytes()[:24]
    assert header[:8] == PNG_SIGNATURE and header[12:16] == b'IHDR', f'{path.name} is not a PNG file'
    return struct.unpack('>II', header[16:24])


class InstallManifestTests(unittest.TestCase):
    def setUp(self):
        self.html = (WEB / 'index.html').read_text(encoding='utf-8')
        self.manifest = json.loads((WEB / 'manifest.webmanifest').read_text(encoding='utf-8'))

    def test_manifest_names_the_app_and_opens_it_standalone(self):
        manifest = self.manifest
        self.assertEqual('NainWrite', manifest['name'])
        self.assertEqual('NainWrite', manifest['short_name'])
        self.assertEqual('standalone', manifest['display'])
        self.assertEqual('es', manifest['lang'])
        self.assertEqual('ltr', manifest['dir'])
        self.assertEqual('./', manifest['start_url'])
        self.assertEqual(manifest['start_url'], manifest['id'])
        self.assertEqual('./', manifest['scope'])
        self.assertNotIn('prefer_related_applications', manifest)
        for key in ('theme_color', 'background_color'):
            self.assertRegex(manifest[key], r'^#[0-9a-f]{6}$')

    def test_manifest_description_and_theme_match_the_page(self):
        description = re.search(r'<meta name="description" content="([^"]+)"', self.html).group(1)
        self.assertEqual(description, self.manifest['description'])
        theme = re.search(r'<meta name="theme-color" content="([^"]+)"', self.html).group(1)
        self.assertEqual(theme.lower(), self.manifest['theme_color'])

    def test_declared_icons_exist_at_their_declared_size(self):
        icons = [(icon['src'], icon['sizes'], icon['type'], icon['purpose']) for icon in self.manifest['icons']]
        self.assertEqual([
            ('./icons/icon-192.png', '192x192', 'image/png', 'any'),
            ('./icons/icon-512.png', '512x512', 'image/png', 'any'),
            ('./icons/icon-maskable-512.png', '512x512', 'image/png', 'maskable'),
        ], icons)
        for src, sizes, _, _ in icons:
            width, height = png_size(WEB / src[2:])
            self.assertEqual(sizes, f'{width}x{height}', src)
        self.assertEqual((180, 180), png_size(WEB / 'icons' / 'apple-touch-icon.png'))

    def test_page_links_the_manifest_and_carries_the_ios_tags(self):
        html = self.html
        self.assertEqual(['./manifest.webmanifest'], re.findall(r'<link rel="manifest" href="([^"]+)"', html))
        self.assertEqual(['./icons/apple-touch-icon.png'],
                         re.findall(r'<link rel="apple-touch-icon" href="([^"]+)"', html))
        expected = {
            'mobile-web-app-capable': 'yes',
            'apple-mobile-web-app-capable': 'yes',
            'apple-mobile-web-app-title': self.manifest['short_name'],
            'apple-mobile-web-app-status-bar-style': 'default',
        }
        for name, content in expected.items():
            self.assertEqual([content], re.findall(rf'<meta name="{name}" content="([^"]*)"', html), name)

    def test_pages_artifact_publishes_the_whole_web_folder(self):
        workflow = (WEB.parents[2] / '.github' / 'workflows' / 'deploy.yml').read_text(encoding='utf-8')
        self.assertIn('path: src/spanish_rewriter/web', workflow)


if __name__ == '__main__':
    unittest.main()
