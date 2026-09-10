"""Local workbench repository; the sole owner of application persistence."""

from pathlib import Path
import threading

from . import intake_store as files
from .document_store import _atomic, canonical


class WorkbenchRepository:
    def __init__(self, root):
        self.root = Path(root).resolve()
        self.root.mkdir(parents=True, exist_ok=True)
        self.lock = threading.RLock()
        try:
            self.state = files.read_json(self.root, 'workbench.json')
        except FileNotFoundError:
            self.state = {'version': 1, 'paused': False, 'mode': 'limited',
                          'night_start': 22, 'night_end': 7, 'documents': {}}
        if self.state.get('version') != 1:
            raise ValueError('Unsupported workbench state version')
        for record in self.state['documents'].values():
            if record['status'] == 'running':
                record['status'] = 'paused'
                record['progress'] = 'Interrumpido; puedes reanudar el trabajo conservado.'
        self.save()

    def save(self):
        files.put_json(self.root, 'workbench.json', self.state, replace=True)

    def path(self, relative):
        return files.safe_path(self.root, relative)

    def read(self, relative):
        return files.read_bytes(self.root, relative)

    def immutable(self, relative, raw):
        path = self.path(relative)
        if path.exists():
            if path.read_bytes() != raw:
                raise ValueError('Immutable application artifact differs')
            return files.file_hash(raw)
        return files.put_bytes(self.root, relative, raw)

    def text(self, relative, text):
        _atomic(self.path(relative), text, replace=True)

    def relative(self, path):
        return str(Path(path).resolve().relative_to(self.root)).replace('\\', '/')
