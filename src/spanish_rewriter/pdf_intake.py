"""Local PDF extraction and explicit on-disk OCR, without inference downloads."""

import csv
import io
import math
from pathlib import Path
import statistics
import subprocess


class LocalOCR:
    def __init__(self, executable, data_dir):
        self.executable = Path(executable).resolve(strict=True)
        self.data_dir = Path(data_dir).resolve(strict=True)
        for language in ('spa', 'eng'):
            if not (self.data_dir / f'{language}.traineddata').is_file():
                raise ValueError(f'Local OCR language missing: {language}')

    def recognize(self, image_path):
        try:
            result = subprocess.run(
                [str(self.executable), str(image_path), 'stdout', '--tessdata-dir', str(self.data_dir),
                 '-l', 'spa+eng', '--psm', '3', 'tsv'], capture_output=True, timeout=180,
                creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0), check=False)
        except subprocess.TimeoutExpired as error:
            raise ValueError('Local OCR timed out; page needs correction or replacement') from error
        if result.returncode:
            raise ValueError('Local OCR failed; page must be corrected or replaced')
        rows = csv.DictReader(io.StringIO(result.stdout.decode('utf-8')), delimiter='\t')
        words, lines = [], {}
        for row in rows:
            if row.get('level') != '5' or not row.get('text', '').strip():
                continue
            confidence = float(row['conf'])
            if not math.isfinite(confidence):
                raise ValueError('Invalid OCR confidence')
            word = {key: int(row[key]) for key in ('left', 'top', 'width', 'height')}
            word.update(text=row['text'], confidence=confidence)
            words.append(word)
            key = tuple(row[k] for k in ('block_num', 'par_num', 'line_num'))
            lines.setdefault(key, []).append(row['text'])
        return {'text': '\n'.join(' '.join(line) for line in lines.values()), 'words': words,
                'engine': 'tesseract-spa-eng',
                'findings': ['ocr_low_confidence'] if any(w['confidence'] < 85 for w in words) else []}


def _png(image):
    stream = io.BytesIO()
    image.save(stream, format='PNG')
    return stream.getvalue()


def _cell(value):
    return str(value or '').replace('|', '\\|').replace('\r', ' ').replace('\n', ' ')


def _native_lines(page):
    words = page.extract_words(extra_attrs=['size', 'fontname'])
    typical_size = statistics.median([word['size'] for word in words]) if words else 12
    rows = []
    for word in sorted(words, key=lambda w: (w['top'], w['x0'])):
        if not rows or abs(rows[-1][0]['top'] - word['top']) > 3:
            rows.append([word])
        else:
            rows[-1].append(word)
    records, split_rows = [], []
    for row in rows:
        chunks = [[]]
        for word in sorted(row, key=lambda w: w['x0']):
            if chunks[-1] and word['x0'] - chunks[-1][-1]['x1'] > 50:
                chunks.append([])
            chunks[-1].append(word)
        if len(chunks) == 2 and chunks[0][-1]['x1'] < page.width * .55 and chunks[1][0]['x0'] > page.width * .45:
            split_rows.append(row[0]['top'])
        for chunk in chunks:
            text = ' '.join(word['text'] for word in chunk)
            if all(word['size'] > typical_size * 1.2 for word in chunk):
                text = '### ' + text
            records.append([chunk[0]['top'], chunk[0]['x0'], text])
    if len(split_rows) >= 2:
        first, last = min(split_rows), max(split_rows)
        left = sorted([r for r in records if first <= r[0] <= last and r[1] < page.width * .5])
        right = sorted([r for r in records if first <= r[0] <= last and r[1] >= page.width * .5])
        # Collate a simple repeated two-column region; uncertain layouts still require review.
        records = [r for r in records if not first <= r[0] <= last]
        records.append([first, 0, '\n\n'.join(r[2] for r in left + right)])
    return records


def extract_pdf(raw):
    import pdfplumber
    import pypdfium2
    from pypdf import PdfReader

    reader = PdfReader(io.BytesIO(raw))
    if reader.is_encrypted:
        raise ValueError('Encrypted PDFs require a separate decrypted copy')
    if not 0 < len(reader.pages) <= 200:
        raise ValueError('PDF page count exceeds the supported limit')
    with pdfplumber.open(io.BytesIO(raw)) as document, pypdfium2.PdfDocument(raw) as renderer:
        if len(document.pages) != len(renderer):
            raise ValueError('PDF readers disagree about page coverage')
        for index, page in enumerate(document.pages):
            width, height = float(page.width), float(page.height)
            if not all(math.isfinite(v) and v > 0 for v in (width, height)):
                raise ValueError('Invalid PDF page dimensions')
            scale = min(2.5, math.sqrt(20_000_000 / (width * height)))
            render_page = renderer[index]
            try:
                bitmap = render_page.render(scale=scale)
                image = bitmap.to_pil().copy()
                bitmap.close()
            finally:
                render_page.close()
            number = index + 1
            prefix = f'assets/page-{number:04d}'
            assets = {f'{prefix}.png': _png(image)}
            findings = ['pdf_extraction_requires_review']
            tables = page.find_tables()
            blocks = []
            for table in tables:
                rows = table.extract()
                if rows and rows[0]:
                    count = max(len(row) for row in rows)
                    normalized = [list(row) + [''] * (count - len(row)) for row in rows]
                    rendered = ['| ' + ' | '.join(map(_cell, row)) + ' |' for row in normalized]
                    rendered.insert(1, '| ' + ' | '.join(['---'] * count) + ' |')
                    blocks.append((table.bbox[1], table.bbox[0], '\n'.join(rendered)))
                    findings.append('table_structure_requires_review')
            def outside_tables(obj):
                x, y = (obj['x0'] + obj['x1']) / 2, (obj['top'] + obj['bottom']) / 2
                return not any(a <= x <= c and b <= y <= d for a, b, c, d in (t.bbox for t in tables))
            filtered = page.filter(lambda obj: obj.get('object_type') != 'char' or outside_tables(obj))
            blocks.extend(tuple(line) for line in _native_lines(filtered))
            native = bool(page.chars)
            # Cropped images are retained in the editable document; page previews stay evidence only.
            if native:
                for offset, item in enumerate(page.images):
                    box = (max(0, item['x0']), max(0, item['top']),
                           min(width, item['x1']), min(height, item['bottom']))
                    if box[2] <= box[0] or box[3] <= box[1]:
                        findings.append('image_bounds_unresolved')
                        continue
                    name = f'{prefix}-image-{offset + 1}.png'
                    assets[name] = _png(image.crop(tuple(round(v * scale) for v in box)))
                    blocks.append((box[1], box[0], f'![Figura {number}.{offset + 1}]({name})'))
                    findings.append('image_text_and_caption_relationship_require_review')
            links = []
            for link in page.hyperlinks:
                uri = link.get('uri')
                if uri:
                    links.append(str(uri))
            if links:
                findings.append('link_relationship_requires_review')
                existing_text = '\n'.join(block[2] for block in blocks)
                missing_links = [link for link in links if link not in existing_text]
                if missing_links:
                    blocks.append((height + 1, 0, '\n'.join(missing_links)))
            if page.annots:
                findings.append('annotations_require_review')
            # Column/footnote order and native hidden OCR layers are never automatically certified.
            findings.append('reading_order_and_footnotes_require_review')
            text = '\n\n'.join(text for _, _, text in sorted(blocks))
            yield {'number': number, 'width': width, 'height': height, 'method': 'native' if native else 'ocr',
                   'text': text, 'preview': f'{prefix}.png', 'findings': sorted(set(findings)),
                   'tables': len(tables), 'images': len(page.images), 'links': links, 'assets': assets}
            image.close()
