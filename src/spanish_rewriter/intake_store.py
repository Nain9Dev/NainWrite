"""Persistence boundary for original documents, extraction and review evidence."""

import hashlib
import json
from pathlib import Path
import uuid

from .document_store import _atomic, canonical


def file_hash(raw):
    return hashlib.sha256(raw).hexdigest()


def safe_path(folder, name):
    root = Path(folder).resolve(strict=True)
    relative = Path(name)
    if relative.is_absolute() or '..' in relative.parts or ':' in str(name):
        raise ValueError('Artifact path escapes the intake')
    target = root / relative
    if any(part.is_symlink() or (hasattr(part, 'is_junction') and part.is_junction())
           for part in (target, *target.parents) if part != root and root in part.parents):
        raise ValueError('Linked artifact paths are forbidden')
    if not target.resolve().is_relative_to(root):
        raise ValueError('Artifact path escapes the intake')
    return target


def read_source(path):
    source = Path(path)
    if source.is_symlink() or not source.is_file():
        raise ValueError('Source must be a regular file')
    source = source.resolve(strict=True)
    if source.suffix.lower() not in {'.pdf', '.md', '.txt'}:
        raise ValueError('Only PDF, Markdown and TXT are supported')
    if not 0 < source.stat().st_size <= 100 * 1024 * 1024:
        raise ValueError('Source is empty or exceeds the 100 MB limit')
    raw = source.read_bytes()
    if len(raw) > 100 * 1024 * 1024:
        raise ValueError('Source grew beyond its size limit')
    return source, raw


def create_folder(root):
    root = Path(root).resolve()
    root.mkdir(parents=True, exist_ok=True)
    folder = root / uuid.uuid4().hex
    folder.mkdir()
    return folder


def put_bytes(folder, name, raw):
    path = safe_path(folder, name)
    path.parent.mkdir(parents=True, exist_ok=True)
    # Unique intake artifacts are never overwritten.
    with path.open('xb') as stream:
        stream.write(raw)
    return file_hash(raw)


def put_json(folder, name, value, *, replace=False):
    path = safe_path(folder, name)
    _atomic(path, canonical(value), replace=replace)


def read_json(folder, name):
    return json.loads(safe_path(folder, name).read_text(encoding='utf-8'))


def read_bytes(folder, name):
    return safe_path(folder, name).read_bytes()


def write_editable(folder, text):
    if not isinstance(text, str) or not text.strip():
        raise ValueError('Extraction cannot be empty')
    _atomic(safe_path(folder, 'extraction.md'), text, replace=True)


def read_local_image(source, relative):
    path = safe_path(source.parent, relative)
    if not path.is_file() or path.stat().st_size > 25 * 1024 * 1024:
        raise ValueError('Missing or oversized local image')
    if path.suffix.lower() not in {'.png', '.jpg', '.jpeg'}:
        raise ValueError('Only local PNG/JPEG images are supported')
    return path.suffix.lower(), path.read_bytes()


def verify(folder):
    manifest = read_json(folder, 'intake.json')
    identity = read_json(folder, 'intake-identity.json')
    if file_hash(canonical(manifest).encode('utf-8')) != identity['manifest_sha256']:
        raise ValueError('Intake manifest changed')
    for name, expected in manifest['files'].items():
        if file_hash(read_bytes(folder, name)) != expected:
            raise ValueError(f'Original or asset changed: {name}')
    return manifest
