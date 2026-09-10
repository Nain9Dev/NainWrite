"""Exercise exported content and assets independently of model responses."""

import io
from pathlib import Path
import sys
import tempfile
import unittest
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from spanish_rewriter.document_export import render_pdf, portable_markdown


class DocumentExportTests(unittest.TestCase):
    def test_pdf_and_bundle_preserve_table_image_and_critical_text(self):
        from PIL import Image
        from pypdf import PdfReader
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / 'assets').mkdir()
            image = root / 'assets' / 'sample.png'
            Image.new('RGB', (160, 80), '#26564c').save(image)
            text = ('# Propuesta profesional\n\nNo incluye alojamiento.\n\n'
                    '| Concepto | Importe |\n| --- | --- |\n| Informe | 125 euros |\n\n'
                    '![Esquema](assets/sample.png)\n\n'
                    'Solo si recibimos la aprobación antes del día 10.\n\n'
                    '[Referencia](https://example.com/terms)\n')
            raw = render_pdf(text, root)
            reader = PdfReader(io.BytesIO(raw))
            extracted = '\n'.join(page.extract_text() for page in reader.pages)
            for phrase in ('No incluye alojamiento.', '125 euros', 'Solo si recibimos',
                           'aprobación antes del día 10.', 'https://example.com/terms'):
                self.assertIn(phrase, extracted)
            self.assertGreater(sum(len(page.images) for page in reader.pages), 0)
            with zipfile.ZipFile(io.BytesIO(portable_markdown(text, root, 'es-ES'))) as bundle:
                self.assertEqual(text.encode(), bundle.read('es-ES.md'))
                self.assertEqual(image.read_bytes(), bundle.read('assets/sample.png'))

    def test_export_never_fetches_remote_images(self):
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaises(ValueError):
                render_pdf('![Remote](https://example.com/image.png)', Path(folder))


if __name__ == '__main__':
    unittest.main()
