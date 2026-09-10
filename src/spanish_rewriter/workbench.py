"""Application services for the local review queue and revision-specific delivery."""

import copy
from datetime import datetime
import difflib
from pathlib import Path
import threading
import uuid

from . import intake_store as files
from .intake import import_document, intake_status, approve_extraction, approved_source
from .document_export import render_pdf, portable_markdown
from .document_transform import DocumentTransformer
from .editorial_job import start_job, run_job
from .ollama_client import OllamaClient
from .pdf_intake import LocalOCR
from .workbench_store import WorkbenchRepository


class PausedWork(RuntimeError):
    pass


class ControlledClient(OllamaClient):
    def __init__(self, control):
        super().__init__(timeout_seconds=3600)
        self.control = control

    def _request(self, path, payload):
        if path == '/api/generate':
            mode = self.control()
            payload = copy.deepcopy(payload)
            payload['options'].update(num_gpu=0 if mode == 'limited' else -1,
                                      num_thread=4 if mode == 'limited' else 0)
            payload['keep_alive'] = '0s' if mode == 'limited' else '5m'
        return super()._request(path, payload)


class Workbench:
    def __init__(self, root, *, transformer_factory=None, ocr=None):
        self.repo = WorkbenchRepository(root)
        self.transformer_factory = transformer_factory
        self.ocr = ocr
        self.stop = threading.Event()

    def summary(self):
        with self.repo.lock:
            state = copy.deepcopy(self.repo.state)
            for record in state['documents'].values():
                record.pop('result', None)
                record.pop('translation', None)
            return state

    def _record(self, key):
        if key not in self.repo.state['documents']:
            raise ValueError('Unknown document')
        return self.repo.state['documents'][key]

    def _editable(self, record):
        if record['status'] in {'running', 'queued'}:
            raise ValueError('Pause or wait for the current operation before editing or approving')

    def settings(self, **values):
        with self.repo.lock:
            allowed = {'paused', 'mode', 'night_start', 'night_end'}
            if set(values) - allowed:
                raise ValueError('Unknown setting')
            if 'paused' in values and type(values['paused']) is not bool:
                raise ValueError('Invalid pause setting')
            if 'mode' in values and values['mode'] not in {'limited', 'intensive', 'scheduled'}:
                raise ValueError('Invalid resource mode')
            for key in ('night_start', 'night_end'):
                if key in values and (type(values[key]) is not int or not 0 <= values[key] <= 23):
                    raise ValueError('Night hours must be between 0 and 23')
            self.repo.state.update(values); self.repo.save()

    def effective_mode(self, hour=None):
        state = self.repo.state
        if state['mode'] != 'scheduled':
            return state['mode']
        hour = datetime.now().hour if hour is None else hour
        start, end = state['night_start'], state['night_end']
        active = start <= hour < end if start < end else hour >= start or hour < end
        return 'intensive' if active else 'limited'

    def upload(self, name, raw, assets=()):
        if Path(name).name != name or ':' in name or '\\' in name or not name:
            raise ValueError('Invalid upload name')
        suffix = Path(name).suffix.lower()
        if suffix not in {'.pdf', '.md', '.txt'} or not 0 < len(raw) <= 100 * 1024 * 1024:
            raise ValueError('Upload must be a PDF/MD/TXT under 100 MB')
        key = uuid.uuid4().hex
        with self.repo.lock:
            source = f'uploads/{key}/source{suffix}'
            self.repo.immutable(source, raw)
            for asset_name, content in assets:
                if asset_name in {f'source{suffix}'} or not 0 < len(content) <= 25 * 1024 * 1024:
                    raise ValueError('Invalid upload asset')
                self.repo.immutable(f'uploads/{key}/{asset_name}', content)
            self.repo.state['documents'][key] = {'id': key, 'name': name, 'source_path': source,
                                                'status': 'queued', 'action': 'import',
                                                'progress': 'En cola', 'exports': {}, 'final_approvals': {}}
            self.repo.save()
        return key

    def detail(self, key):
        with self.repo.lock:
            record = copy.deepcopy(self._record(key))
            idle = record['status'] not in {'queued', 'running'}
            record['actions'] = {'resume': record['status'] in {'paused', 'failed'},
                                 'edit_extraction': idle and 'editorial_path' not in record and 'intake_path' in record,
                                 'edit_spanish': idle and bool(record.get('result')),
                                 'review_spanish': idle and bool(record.get('result')),
                                 'translate': record['status'] == 'spanish_review'}
            if 'intake_path' in record:
                record['intake'] = intake_status(self.repo.path(record['intake_path']))
            for artifact in record['exports'].values():
                artifact['text'] = self.read_artifact(artifact['markdown']).decode('utf-8')
            if record.get('result'):
                result = record['result']
                prefix = record['editorial_path']
                text = self.repo.read(f"{prefix}/{result['editable_file']}").decode('utf-8')
                record['spanish'] = text
                record['spanish_revision'] = files.file_hash(text.encode('utf-8'))
                record['review'] = self.repo.read(f"{prefix}/{result['review_file']}").decode('utf-8')
                record['diff'] = '\n'.join(difflib.unified_diff(record['intake']['text'].splitlines(),
                                                               text.splitlines(), fromfile='Original', tofile='Español', lineterm=''))
            return record

    def edit_extraction(self, key, text, revision):
        with self.repo.lock:
            record = self._record(key); self._editable(record)
            if 'editorial_path' in record:
                raise ValueError('A rewriting job already exists; import a new source to change extraction')
            folder = self.repo.path(record['intake_path'])
            if intake_status(folder)['revision'] != revision:
                raise ValueError('Extraction changed; reload before saving')
            files.write_editable(folder, text)

    def accept_extraction(self, key, revision, note, complete):
        with self.repo.lock:
            record = self._record(key); self._editable(record)
            if 'editorial_path' in record:
                raise ValueError('Extraction is already associated with a rewriting job')
            approve_extraction(self.repo.path(record['intake_path']), revision, note, complete=complete)
            record.update(status='queued', action='rewrite', progress='Extracción aprobada; español en cola')
            self.repo.save()

    def _current_source(self, record):
        source = approved_source(self.repo.path(record['intake_path']))
        if record.get('approved_source') and self.repo.relative(source) != record['approved_source']:
            raise ValueError('Approved extraction differs from this rewriting job')
        return source

    def edit_spanish(self, key, text, revision):
        if not isinstance(text, str) or not text.strip():
            raise ValueError('Spanish cannot be empty')
        with self.repo.lock:
            record = self._record(key); self._editable(record)
            self._current_source(record)
            path = f"{record['editorial_path']}/{record['result']['editable_file']}"
            if files.file_hash(self.repo.read(path)) != revision:
                raise ValueError('Spanish changed; reload before saving')
            self.repo.text(path, text)
            record.update(status='spanish_edited', exports={}, final_approvals={}, action='review')
            record.pop('translation', None)
            self.repo.save()

    def review_spanish(self, key):
        with self.repo.lock:
            record = self._record(key); self._editable(record)
            self._current_source(record)
            record.update(status='queued', action='review', progress='Revisión del español en cola')
            record.pop('translation', None); self.repo.save()

    def translate(self, key, revision, note, resolved, acknowledge):
        if resolved is not True or not isinstance(note, str) or not note.strip():
            raise ValueError('Confirm all meaning doubts are resolved and provide your review note')
        with self.repo.lock:
            record = self._record(key); self._editable(record)
            self._current_source(record)
            if record['status'] != 'spanish_review' or record['result']['revision_sha256'] != revision:
                raise ValueError('Review the current Spanish revision before translating')
            path = f"{record['editorial_path']}/{record['result']['editable_file']}"
            if files.file_hash(self.repo.read(path)) != revision:
                raise ValueError('Spanish changed since review')
            if record['result']['automatic_status'] != 'accepted' and acknowledge is not True:
                raise ValueError('Review and explicitly acknowledge the retained automatic findings')
            record.update(status='queued', action='translate', progress='Traducciones en cola',
                          translation={'revision': revision, 'note': note.strip(), 'acknowledge': acknowledge})
            self.repo.save()

    def approve_final(self, key, locale, revision, note):
        if not isinstance(note, str) or not note.strip():
            raise ValueError('A final review note is required')
        with self.repo.lock:
            record = self._record(key); self._editable(record)
            self._current_source(record)
            if locale not in record['exports'] or record['exports'][locale]['text_sha256'] != revision:
                raise ValueError('Final approval must match the current exported locale revision')
            exported = record['exports'][locale]
            for kind in ('pdf', 'markdown', 'bundle'):
                self.read_artifact(exported[kind])
            if files.file_hash(self.repo.read(exported['markdown'])) != revision:
                raise ValueError('Exported text changed')
            spanish_path = f"{record['editorial_path']}/{record['result']['editable_file']}"
            if files.file_hash(self.repo.read(spanish_path)) != record['result']['revision_sha256']:
                raise ValueError('Spanish changed; exports are outdated')
            if record['final_approvals'].get(locale, {}).get('revision') == revision:
                return
            approval = {'revision': revision, 'note': note.strip(), 'time': datetime.now().isoformat()}
            self.repo.immutable(f'final-reviews/{key}/{locale}-{revision}.json',
                                files.canonical(approval).encode('utf-8'))
            record['final_approvals'][locale] = approval
            if (record['result']['generation_complete'] and
                    all(record['final_approvals'].get(language, {}).get('revision') ==
                        record['exports'].get(language, {}).get('text_sha256')
                        and language in record['final_approvals']
                        for language in ('es-ES', 'en-US', 'en-GB'))):
                record.update(status='ready', progress='Las tres versiones tienen aprobación final')
            self.repo.save()

    def resume(self, key):
        with self.repo.lock:
            record = self._record(key)
            if record['status'] not in {'paused', 'failed'}:
                raise ValueError('Only paused or failed work can be resumed')
            record.update(status='queued', progress='Reanudación en cola')
            record.pop('error', None); self.repo.save()

    def _control(self, key, message=None):
        with self.repo.lock:
            if self.stop.is_set() or self.repo.state['paused']:
                raise PausedWork('Pausa solicitada; progreso conservado')
            mode = self.effective_mode()
            record = self._record(key)
            if message:
                record['progress'] = message
            record['effective_mode'] = mode
            self.repo.save()
            return mode

    def _export(self, record, result):
        intake = self.repo.path(record['intake_path'])
        exports = {}
        export_id = uuid.uuid4().hex[:12]
        for locale, filename in result['files'].items():
            text = self.repo.read(f"{record['editorial_path']}/{filename}").decode('utf-8')
            revision = files.file_hash(text.encode('utf-8'))
            prefix = f"exports/{record['id']}/{export_id}/{locale}"
            pdf_path, md_path, zip_path = prefix + '.pdf', prefix + '.md', prefix + '.zip'
            self.repo.immutable(md_path, text.encode('utf-8'))
            if not self.repo.path(pdf_path).exists():
                self.repo.immutable(pdf_path, render_pdf(text, intake))
            if not self.repo.path(zip_path).exists():
                self.repo.immutable(zip_path, portable_markdown(text, intake, locale))
            exports[locale] = {'pdf': pdf_path, 'markdown': md_path, 'bundle': zip_path,
                               'text_sha256': revision, 'pdf_sha256': files.file_hash(self.repo.read(pdf_path)),
                               'bundle_sha256': files.file_hash(self.repo.read(zip_path))}
        return exports

    def step(self):
        with self.repo.lock:
            if self.repo.state['paused'] or self.stop.is_set():
                return False
            record = next((r for r in self.repo.state['documents'].values() if r['status'] == 'queued'), None)
            if record is None:
                return False
            key, action = record['id'], record['action']
            record.update(status='running', progress='Preparando ' + action)
            self.repo.save()
        try:
            if action == 'import':
                intake = import_document(self.repo.path(record['source_path']), self.repo.path('intakes'), ocr=self.ocr)
                with self.repo.lock:
                    record.update(intake_path=self.repo.relative(intake), status='extraction_review', progress='Revisa la extracción completa')
            else:
                self._control(key)
                source = self._current_source(record)
                transformer = (self.transformer_factory() if self.transformer_factory else
                               DocumentTransformer(ControlledClient(lambda: self._control(key))))
                for locale, proofreader in transformer.proofreaders.items():
                    proofreader.check('Prueba local.' if locale == 'es-ES' else 'Local check.')
                if 'editorial_path' not in record:
                    job = start_job(source, transformer, output_dir=self.repo.path('jobs'))
                    with self.repo.lock:
                        record.update(editorial_path=self.repo.relative(job), approved_source=self.repo.relative(source))
                        self.repo.save()
                authority = record.get('translation', {}) if action == 'translate' else {}
                result = run_job(self.repo.path(record['editorial_path']), transformer,
                                 progress=lambda locale, n, total: self._control(key, f'{locale}: bloque {n}/{total}'),
                                 approve_spanish=authority.get('revision'),
                                 acknowledge_review=bool(authority.get('acknowledge')))
                self._current_source(record)
                with self.repo.lock:
                    record['result'] = result
                    self.repo.save()
                exports = self._export(record, result)
                with self.repo.lock:
                    record.update(result=result, exports=exports,
                                  status='final_review' if result['generation_complete'] else 'spanish_review',
                                  progress='Generación completa; revisión humana pendiente' if result['generation_complete'] else 'Español listo para revisar')
            with self.repo.lock:
                record.pop('error', None); self.repo.save()
        except PausedWork as error:
            with self.repo.lock:
                record.update(status='paused', progress=str(error)); self.repo.save()
        except Exception as error:
            with self.repo.lock:
                record.update(status='failed', error=str(error), progress='Trabajo detenido; evidencia conservada')
                self.repo.save()
        return True

    def read_artifact(self, relative):
        with self.repo.lock:
            raw = self.repo.read(relative)
            for record in self.repo.state['documents'].values():
                for artifact in record.get('exports', {}).values():
                    for kind, hash_name in [('pdf', 'pdf_sha256'), ('markdown', 'text_sha256'), ('bundle', 'bundle_sha256')]:
                        if artifact[kind] == relative and files.file_hash(raw) != artifact[hash_name]:
                            raise ValueError('Exported artifact changed; download refused')
            return raw

    def run(self):
        while not self.stop.is_set():
            if not self.step():
                self.stop.wait(.5)
