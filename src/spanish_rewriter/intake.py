"""Document intake, coverage review and immutable handoff to the rewriting service."""

from datetime import datetime, timezone
import io
from pathlib import Path
import re

from . import intake_store as store
from .document import parse_document
from .document_store import canonical, job_lock
from .pdf_intake import extract_pdf

IMAGE = re.compile(r'!\[([^\]\r\n]*)\]\(([^)\r\n]+)\)')


def _validate_image(raw):
    from PIL import Image
    with Image.open(io.BytesIO(raw)) as image:
        if image.width * image.height > 20_000_000:
            raise ValueError('Image exceeds pixel limit')
        image.verify()


def import_document(path, output_root, *, ocr=None):
    source, raw = store.read_source(path)
    if source.suffix.lower() != '.pdf':
        text = raw.decode('utf-8-sig')
        if not text.strip():
            raise ValueError('Source is empty')
    folder = store.create_folder(output_root)
    original = 'original' + source.suffix.lower()
    files = {original: store.put_bytes(folder, original, raw)}
    pages, assets = [], []
    try:
        if source.suffix.lower() == '.pdf':
            sections = []
            for page in extract_pdf(raw):
                for name, content in page.pop('assets').items():
                    files[name] = store.put_bytes(folder, name, content)
                    assets.append(name)
                if page['method'] == 'ocr':
                    if ocr is None:
                        page.update(text='', extraction_error='Local OCR is unavailable')
                    else:
                        try:
                            page['ocr'] = ocr.recognize(store.safe_path(folder, page['preview']))
                            page['text'] = page['ocr']['text']
                            page['findings'].extend(page['ocr']['findings'])
                        except (OSError, ValueError, TimeoutError) as error:
                            page.update(text='', extraction_error=str(error))
                    page['findings'].append('scan_transcription_requires_review')
                if not page['text'].strip():
                    page['findings'].append('empty_page_requires_correction_or_blank_confirmation')
                sections.append(f"## Página {page['number']}\n\n{page['text']}\n")
                pages.append(page)
            text = '\n'.join(sections)
        elif source.suffix.lower() == '.md':
            def copy_image(match):
                relative = match[2]
                suffix, content = store.read_local_image(source, relative)
                _validate_image(content)
                name = f'assets/image-{len(assets) + 1}{suffix}'
                files[name] = store.put_bytes(folder, name, content)
                assets.append(name)
                return f'![{match[1]}]({name})'
            text = IMAGE.sub(copy_image, text)
        store.put_bytes(folder, 'extraction.baseline.md', text.encode('utf-8'))
        files['extraction.baseline.md'] = store.file_hash(text.encode('utf-8'))
        store.write_editable(folder, text)
        manifest = {'version': 'intake-v1', 'source_name': source.name, 'source_sha256': files[original],
                    'original': original, 'pages': pages, 'assets': assets, 'files': files}
        store.put_json(folder, 'intake.json', manifest)
        store.put_json(folder, 'intake-identity.json',
                       {'manifest_sha256': store.file_hash(canonical(manifest).encode('utf-8'))})
        return folder
    except Exception as error:
        store.put_json(folder, 'import-error.json', {'error': str(error), 'complete': False})
        raise


def intake_status(folder):
    manifest = store.verify(folder)
    raw = store.read_bytes(folder, 'extraction.md')
    revision = store.file_hash(raw)
    try:
        approval = store.read_json(folder, f'approval-{revision}.json')
        approved = (approval['revision'] == revision and approval['source_sha256'] == manifest['source_sha256']
                    and approval['complete'] is True and bool(approval['note'].strip()))
    except FileNotFoundError:
        approved = False
    return dict(manifest, revision=revision, approved=approved, text=raw.decode('utf-8'))


def _check_extraction(manifest, text):
    if not text.strip():
        raise ValueError('Extraction is empty')
    if manifest['pages']:
        headings = list(re.finditer(r'(?m)^## Página (\d+)\s*$', text))
        if [int(m[1]) for m in headings] != [p['number'] for p in manifest['pages']]:
            raise ValueError('Every PDF page must appear once, in order')
        for index, heading in enumerate(headings):
            end = headings[index + 1].start() if index + 1 < len(headings) else len(text)
            if not text[heading.end():end].strip():
                raise ValueError('Empty page must be corrected or explicitly described as blank')
    baseline = store.read_bytes(manifest['_folder'], 'extraction.baseline.md').decode('utf-8')
    expected_images = [m[2] for m in IMAGE.finditer(baseline)]
    actual_images = [m[2] for m in IMAGE.finditer(text)]
    if actual_images != expected_images:
        raise ValueError('Retained image references must remain unchanged')
    # Reject unsupported markup rather than silently sending an incomplete parser result.
    parse_document(text)


def approve_extraction(folder, revision, note, *, complete=False):
    if not complete or not isinstance(note, str) or not note.strip():
        raise ValueError('Explicit completeness confirmation and a review note are required')
    with job_lock(folder):
        status = intake_status(folder)
        if revision != status['revision']:
            raise ValueError('Extraction revision changed; review current text')
        _check_extraction(dict(status, _folder=folder), status['text'])
        snapshot = f'approved-{revision}.md'
        store.put_json(folder, f'approval-{revision}.json',
                       {'revision': revision, 'source_sha256': status['source_sha256'],
                        'note': note.strip(), 'complete': True,
                        'time': datetime.now(timezone.utc).isoformat()})
        if not store.safe_path(folder, snapshot).exists():
            store.put_bytes(folder, snapshot, status['text'].encode('utf-8'))
        return status


def approved_source(folder):
    status = intake_status(folder)
    if not status['approved']:
        raise ValueError('Current extraction must be reviewed and approved first')
    _check_extraction(dict(status, _folder=folder), status['text'])
    name = f"approved-{status['revision']}.md"
    if store.file_hash(store.read_bytes(folder, name)) != status['revision']:
        raise ValueError('Approved extraction snapshot changed')
    return store.safe_path(folder, name)
