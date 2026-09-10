"""Synthetic intake cases exercise content preservation and review authority."""

import hashlib
import io
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from spanish_rewriter.intake import import_document, approve_extraction, approved_source, intake_status


class IntakeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def pdf(self, pages=2):
        from reportlab.pdfgen.canvas import Canvas
        path = self.root / 'source.pdf'
        canvas = Canvas(str(path))
        for number in range(pages):
            canvas.drawString(50, 760, f'Proposal page {number + 1}. Delivery costs 125 EUR.')
            canvas.showPage()
        canvas.save()
        return path

    def test_every_pdf_page_has_evidence_and_requires_review(self):
        source = self.pdf()
        original = source.read_bytes()
        folder = import_document(source, self.root / 'intakes')
        status = intake_status(folder)
        self.assertEqual(2, len(status['pages']))
        self.assertFalse(status['approved'])
        for page in status['pages']:
            self.assertTrue((folder / page['preview']).is_file())
        self.assertEqual(original, (folder / 'original.pdf').read_bytes())
        with self.assertRaises(ValueError):
            approved_source(folder)
        approve_extraction(folder, status['revision'], 'Compared both pages.', complete=True)
        self.assertIn('125', approved_source(folder).read_text(encoding='utf-8'))
        self.assertEqual(original, source.read_bytes())

    def test_exact_approval_is_invalidated_by_edits(self):
        source = self.root / 'draft.txt'
        source.write_text('No se garantiza la entrega.\n', encoding='utf-8')
        folder = import_document(source, self.root / 'intakes')
        revision = intake_status(folder)['revision']
        with self.assertRaises(ValueError):
            approve_extraction(folder, revision, '', complete=True)
        approve_extraction(folder, revision, 'Reviewed.', complete=True)
        (folder / 'extraction.md').write_text('Se garantiza la entrega.\n', encoding='utf-8')
        with self.assertRaises(ValueError):
            approved_source(folder)
        self.assertFalse(intake_status(folder)['approved'])

    def test_tampered_original_or_asset_blocks_approval(self):
        folder = import_document(self.pdf(1), self.root / 'intakes')
        status = intake_status(folder)
        (folder / status['pages'][0]['preview']).write_bytes(b'changed')
        with self.assertRaises(ValueError):
            approve_extraction(folder, status['revision'], 'Reviewed.', complete=True)

    def test_remote_and_escaping_markdown_images_are_never_read(self):
        for image in ('https://example.org/private.png', '../secret.png', 'C:/secret.png'):
            source = self.root / 'source.md'
            source.write_text(f'Hello\n\n![Image]({image})\n', encoding='utf-8')
            with self.subTest(image=image), self.assertRaises(ValueError):
                import_document(source, self.root / 'intakes')

    def test_missing_page_and_empty_extraction_cannot_be_approved(self):
        folder = import_document(self.pdf(), self.root / 'intakes')
        (folder / 'extraction.md').write_text('## Página 1\n\nOnly first page.\n', encoding='utf-8')
        with self.assertRaises(ValueError):
            approve_extraction(folder, intake_status(folder)['revision'], 'Reviewed.', complete=True)

    def test_scanned_page_uses_local_ocr_and_retains_confidence(self):
        from PIL import Image, ImageDraw
        from reportlab.pdfgen.canvas import Canvas
        from reportlab.lib.utils import ImageReader
        image = Image.new('RGB', (900, 400), 'white')
        ImageDraw.Draw(image).text((30, 30), 'A scanned proposal.', fill='black')
        source = self.root / 'scan.pdf'
        canvas = Canvas(str(source))
        canvas.drawImage(ImageReader(image), 40, 350, 500, 220)
        canvas.save()
        class OCR:
            def recognize(self, path):
                return {'text': 'A scanned proposal.', 'words': [{'text':'proposal', 'confidence':91.0}],
                        'engine': 'synthetic-test-ocr', 'findings': []}
        folder = import_document(source, self.root / 'intakes', ocr=OCR())
        page = intake_status(folder)['pages'][0]
        self.assertEqual('ocr', page['method'])
        self.assertEqual(91.0, page['ocr']['words'][0]['confidence'])
        self.assertFalse(intake_status(folder)['approved'])

    def test_markdown_image_assets_are_copied_and_validated(self):
        from PIL import Image
        Image.new('RGB', (20, 20), 'blue').save(self.root / 'diagram.png')
        source = self.root / 'source.md'
        source.write_text('# Report\n\n![Diagram](diagram.png)\n', encoding='utf-8')
        folder = import_document(source, self.root / 'intakes')
        status = intake_status(folder)
        self.assertTrue(status['assets'])
        approve_extraction(folder, status['revision'], 'Reviewed image.', complete=True)
        self.assertIn('assets/', approved_source(folder).read_text(encoding='utf-8'))

    def test_encrypted_pdf_rejected(self):
        from pypdf import PdfReader, PdfWriter
        writer = PdfWriter(clone_from=PdfReader(self.pdf(1)))
        writer.encrypt('secret')
        target = self.root / 'encrypted.pdf'
        writer.write(target)
        with self.assertRaises(ValueError):
            import_document(target, self.root / 'intakes')

    def test_two_columns_keep_column_order_and_heading(self):
        from reportlab.pdfgen.canvas import Canvas
        source = self.root / 'columns.pdf'
        canvas = Canvas(str(source), pagesize=(595, 842))
        canvas.setFont('Helvetica-Bold', 20)
        canvas.drawString(48, 790, 'Conditions')
        canvas.setFont('Helvetica', 12)
        for y, left, right in [(745, 'Left one.', 'Right one.'), (720, 'Left two.', 'Right two.')]:
            canvas.drawString(48, y, left)
            canvas.drawString(310, y, right)
        canvas.save()
        folder = import_document(source, self.root / 'intakes')
        text = intake_status(folder)['text']
        self.assertLess(text.index('Left two.'), text.index('Right one.'))
        self.assertIn('### Conditions', text)


if __name__ == '__main__':
    unittest.main()
