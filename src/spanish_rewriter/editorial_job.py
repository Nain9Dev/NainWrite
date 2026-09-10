"""Revision-aware Spanish approval and independent British/American translation jobs."""

from pathlib import Path
import re

from .document import BATCH_BYTES, MAX_ITEMS, make_batches, parse_document, sha
from .document_evidence import validate_transformation
from .document_job import _context, _global_checks, _items, _values
from .document_review import validate_review
from .document_revision import map_revision
from .document_store import (canonical, digest, initialize_editable, job_lock, new_job_dir,
                             publish, read_editable, read_input, read_state, save_state,
                             verify_artifact as _artifact, verify_artifact_hash)

JOB_VERSION = "approved-trilingual-job-v1"
ENGLISH = ("en-US", "en-GB")


def _name(revision, label, suffix):
    return f"revision-{revision}.{label}{suffix}"


def _identity(state):
    return {key: state[key] for key in ("source_path", "source_sha256", "manifest", "config",
                                       "configuration_sha256", "editable_file")}


def start_job(input_path, transformer, *, output_dir=None, clean_notes=False, omit_lines=()):
    source, text, source_hash = read_input(input_path)
    if not {"es-ES", *ENGLISH}.issubset(transformer.proofreaders):
        raise ValueError("Spanish, British and American proofreading are required")
    options = {"markdown": source.suffix.lower() == ".md", "clean_notes": clean_notes,
               "omit_lines": list(omit_lines)}
    manifest = parse_document(text, **options)
    if not manifest.editable:
        raise ValueError("No editable prose remains after parsing and cleanup")
    config = {"transformer": transformer.config, "parser": options,
              "batch_bytes": BATCH_BYTES, "max_items": MAX_ITEMS, "job_version": JOB_VERSION}
    job = new_job_dir(source, output_dir)
    state = {"source_path": str(source), "source_sha256": source_hash, "manifest": manifest.to_dict(),
             "config": config, "configuration_sha256": digest(config),
             "editable_file": "spanish.editable" + source.suffix.lower(),
             "phase": "es-ES", "generation_complete": False, "human_approved": False,
             "spanish_results": [], "baseline_sha256": None, "revisions": {},
             "current_revision": None, "active_approval": None, "report_hashes": {}}
    publish(job, "job-identity.json", canonical(_identity(state)))
    publish(job, "source.original" + source.suffix.lower(), text)
    save_state(job, state)
    return job


def _validate_generated(result, items, locale, config):
    expected = {i['id']: sha(i['text']) for i in items}
    if result['input_hashes'] != expected or set(result['replacements']) != set(expected):
        raise ValueError("Saved generation source or coverage mismatch")
    if result['output_hashes'] != {key: sha(value) for key, value in result['replacements'].items()}:
        raise ValueError("Saved generation candidate hash mismatch")
    validate_transformation(result, items, locale, config)


def _revision_identity(state, revision):
    return {"source_sha256": state['source_sha256'],
            "configuration_sha256": state['configuration_sha256'],
            "revision_sha256": revision['revision_sha256'], "replacements": revision['replacements']}


def _spanish_status(state, revision, manifest):
    checks = _global_checks(manifest, revision['replacements'], 'es-ES')
    failed = (any(result['status'] != 'accepted' for result in state['spanish_results'])
              or any(result['status'] != 'accepted' for result in revision['reviews'])
              or checks['literal_findings'] or checks['terminology_findings'])
    return 'review_required' if failed else 'accepted'


def _approval(state, revision, acknowledgement):
    return {"revision_sha256": revision['revision_sha256'],
            "source_sha256": state['source_sha256'],
            "configuration_sha256": state['configuration_sha256'],
            "review_sha256": revision['review_sha256'],
            "acknowledge_review": acknowledgement,
            "scope": "translation_of_exact_spanish_revision_only"}


def _validate_saved(job, state, manifest, batches):
    config = state['config']['transformer']
    suffix = Path(state['source_path']).suffix.lower()
    for name, expected_hash in state['report_hashes'].items():
        verify_artifact_hash(job, name, expected_hash)
    results = state['spanish_results']
    if not isinstance(results, list) or len(results) > len(batches):
        raise ValueError("Invalid Spanish batch count")
    for result, batch in zip(results, batches):
        _validate_generated(result, _items(batch), 'es-ES', config)
    baseline = _values(results)
    if len(results) != len(batches):
        if state['revisions'] or state['baseline_sha256'] is not None or state['active_approval'] is not None:
            raise ValueError("Revision cannot precede complete Spanish generation")
        return
    baseline_text = manifest.assemble(baseline)
    if state['baseline_sha256'] is not None:
        if state['baseline_sha256'] != sha(baseline_text):
            raise ValueError("Generated Spanish baseline hash mismatch")
        _artifact(job, 'spanish.baseline' + suffix, baseline_text)
        _artifact(job, 'spanish.baseline-evidence.json', canonical(results))
    elif state['revisions']:
        raise ValueError("Revision without a saved baseline")
    if not isinstance(state['revisions'], dict):
        raise ValueError("Invalid revision registry")
    for key, revision in state['revisions'].items():
        if not re.fullmatch(r'[a-f0-9]{64}', key) or key != revision['revision_sha256']:
            raise ValueError("Invalid revision identity")
        text = manifest.assemble(revision['replacements'])
        if sha(text) != key or map_revision(manifest, baseline, text) != revision['replacements']:
            raise ValueError("Revision content or mapping mismatch")
        _artifact(job, _name(key, 'es-ES', suffix), text)
        _artifact(job, _name(key, 'identity', '.json'), canonical(_revision_identity(state, revision)))
        reviews = revision['reviews']
        if not isinstance(reviews, list) or len(reviews) > len(batches):
            raise ValueError("Invalid Spanish review coverage")
        for review, batch in zip(reviews, batches):
            validate_review(review, _items(batch), 'es-ES', config, _context(manifest, batch))
            if review['replacements'] != {p.id: revision['replacements'][p.id] for p in batch}:
                raise ValueError("Review is not bound to the exact Spanish revision")
        if revision['review_sha256'] is not None:
            if len(reviews) != len(batches) or digest(reviews) != revision['review_sha256']:
                raise ValueError("Spanish review identity or coverage mismatch")
            _artifact(job, _name(key, 'spanish-review-evidence', '.json'), canonical(reviews))
        approval = revision['approval']
        if approval is not None:
            if (revision['review_sha256'] is None or type(approval.get('acknowledge_review')) is not bool
                    or approval != _approval(state, revision, approval['acknowledge_review'])
                    or (_spanish_status(state, revision, manifest) != 'accepted'
                        and not approval['acknowledge_review'])):
                raise ValueError("Saved Spanish approval is stale, incomplete or invalid")
            _artifact(job, _name(key, 'approval', '.json'), canonical(approval))
        if set(revision['english']) != set(ENGLISH):
            raise ValueError("Invalid English locale coverage")
        for locale in ENGLISH:
            stage = revision['english'][locale]
            generated, crosschecks = stage['results'], stage['crosschecks']
            if (not isinstance(generated, list) or not isinstance(crosschecks, list)
                    or len(generated) > len(batches) or len(crosschecks) > len(generated)
                    or (generated and approval is None)):
                raise ValueError("English evidence lacks approval or has invalid batch coverage")
            for result, batch in zip(generated, batches):
                _validate_generated(result, _items(batch, revision['replacements']), locale, config)
            for index, (review, batch) in enumerate(zip(crosschecks, batches)):
                validate_review(review, _items(batch), locale, config, _context(manifest, batch))
                if review['replacements'] != generated[index]['replacements']:
                    raise ValueError("Original-grounded crosscheck candidate differs from generated English")
            if stage['published']:
                if len(generated) != len(batches) or len(crosschecks) != len(batches):
                    raise ValueError("Published English has incomplete evidence")
                _artifact(job, _name(key, locale, suffix), manifest.assemble(_values(generated)))
                _artifact(job, _name(key, locale + '-evidence', '.json'), canonical(
                    {'results': generated, 'crosschecks': crosschecks}))
    current = state['current_revision']
    if current is not None and current not in state['revisions']:
        raise ValueError("Current revision does not exist")
    if state['active_approval'] is not None:
        if (current is None or state['revisions'][current]['approval'] is None
                or state['active_approval'] != digest(state['revisions'][current]['approval'])):
            raise ValueError("Current approval authority mismatch")


def _editable(job, state):
    try:
        return read_editable(job, state['editable_file'])
    except (OSError, ValueError):
        state.update(active_approval=None, human_approved=False, generation_complete=False,
                     phase='spanish_revision_changed')
        save_state(job, state)
        raise


def _unchanged(job, state, revision):
    _source_unchanged(state)
    if _editable(job, state)[2] != revision['revision_sha256']:
        state.update(active_approval=None, human_approved=False, generation_complete=False,
                     phase='spanish_revision_changed')
        save_state(job, state)
        raise ValueError("Editable Spanish changed during processing; review its new revision")


def _source_unchanged(state):
    if read_input(state['source_path'])[2] != state['source_sha256']:
        raise ValueError("Original document changed during processing")


def _summary(job, state, manifest, batches, revision):
    key = revision['revision_sha256']
    suffix = Path(state['source_path']).suffix.lower()
    approved = state['active_approval'] is not None
    complete = approved and all(len(stage['results']) == len(batches)
                                and len(stage['crosschecks']) == len(batches)
                                and stage['published'] for stage in revision['english'].values())
    status = _spanish_status(state, revision, manifest)
    files = {'es-ES': _name(key, 'es-ES', suffix)}
    checks = {'es-ES': _global_checks(manifest, revision['replacements'], 'es-ES')}
    for locale, stage in revision['english'].items():
        if stage['published'] and approved:
            files[locale] = _name(key, locale, suffix)
            checks[locale] = _global_checks(manifest, _values(stage['results']), locale)
            if (any(r['status'] != 'accepted' for r in stage['results'] + stage['crosschecks'])
                    or checks[locale]['literal_findings'] or checks[locale]['terminology_findings']):
                status = 'review_required'
    phase = 'complete' if complete else 'translating' if approved else 'awaiting_spanish_approval'
    report_label = 'complete-review' if complete else 'spanish-review'
    report = _name(key, report_label, '.md')
    # Reports are immutable revision/phase snapshots. Current staleness is in the returned summary.
    report_data = {'revision_sha256': key, 'source_sha256': state['source_sha256'],
                   'configuration_sha256': state['configuration_sha256'],
                   'automatic_status': status, 'checks': checks,
                   'spanish_review': revision['reviews'], 'baseline_results': state['spanish_results'],
                   'generation_complete': complete, 'human_approved': approved,
                   'files': files, 'approval': revision['approval'] if approved else None,
                   'english': revision['english'] if complete else {},
                   'cleanup_ranges': manifest.removals}
    report_json = _name(key, report_label, '.json')
    publish(job, report_json, canonical(report_data))
    state['report_hashes'][report_json] = sha(canonical(report_data))
    lines = ['# Revisión editorial', '', f'Revisión española: {key}',
             f'Estado automático: {status}. Generación completa: {complete}.',
             f'Autorización humana de traducción de esta revisión: {approved}.', '',
             'La aceptación automática no es aprobación de publicación ni garantía de equivalencia.',
             'Los estados de ambos auditores y del corrector se conservan en el informe JSON.',
             'Los hallazgos del español generado se conservan de forma conservadora tras editar.',
             'La comprobación semántica es por bloques; no acredita hechos ni ofrece una prueba exhaustiva.', '',
             '## Hallazgos por bloque', '']
    for index, review in enumerate(revision['reviews'], 1):
        lines.append(f"- es-ES {index}: {review['status']}. " + '; '.join(review['issues']))
    for locale, stage in revision['english'].items():
        if complete:
            for index, (result, crosscheck) in enumerate(zip(stage['results'], stage['crosschecks']), 1):
                lines.append(f"- {locale} {index}, desde español: {result['status']}; contra original: "
                             f"{crosscheck['status']}. " + '; '.join(result['issues'] + crosscheck['issues']))
    current_findings = [issue for review in revision['reviews'] for issue in review['issues']]
    if complete:
        current_findings.extend(issue for stage in revision['english'].values()
                                for result in stage['results'] + stage['crosschecks']
                                for issue in result['issues'])
    questions = []
    if any(issue.endswith(':source_ambiguity:alojamiento') for issue in current_findings):
        questions.append('¿«Alojamiento» se refiere a un servicio web, a una estancia de personas '
                         'o a otro significado? Aclara el pasaje original o aporta el contexto '
                         'que permite decidir antes de aprobar la traducción.')
    if any(issue.endswith(':contextual_sense_changed:alojamiento') for issue in current_findings):
        questions.append('La traducción de «alojamiento» usa un sentido distinto del indicado '
                         'en el original. Revisa ese pasaje antes de aprobarlo.')
    if questions:
        lines.extend(['', '## Dudas de contexto', ''] + ['- ' + question for question in questions])
    report_text = '\n'.join(lines) + '\n'
    publish(job, report, report_text)
    state['report_hashes'][report] = sha(report_text)
    return {'phase': phase, 'generation_complete': complete, 'automatic_status': status,
            'human_approved': approved, 'revision_sha256': key, 'files': files,
            'editable_file': state['editable_file'], 'review_file': report,
            'outdated_revisions': [old for old, record in state['revisions'].items()
                                  if old != key and any(s['results'] for s in record['english'].values())],
            'source_unchanged': True, 'checks': checks}


def run_job(job_dir, transformer, *, progress=None, approve_spanish=None, acknowledge_review=False):
    job = Path(job_dir).resolve(strict=True)
    if approve_spanish is not None and not re.fullmatch(r'[a-f0-9]{64}', approve_spanish):
        raise ValueError("Approval requires the exact Spanish revision SHA-256")
    if acknowledge_review and approve_spanish is None:
        raise ValueError("Review acknowledgement requires explicit Spanish approval")
    with job_lock(job):
        state = read_state(job)
        if state.get('config', {}).get('job_version') != JOB_VERSION:
            raise ValueError("Legacy checkpoint is incompatible with the approval workflow; start a new job. No migration performed")
        try:
            source, text, source_hash = read_input(state['source_path'])
            if source_hash != state['source_sha256']:
                raise ValueError("Original document changed; start a new job")
            config = state['config']
            if (config['transformer'] != transformer.config or digest(config) != state['configuration_sha256']
                    or config['batch_bytes'] != BATCH_BYTES or config['max_items'] != MAX_ITEMS):
                raise ValueError("Job configuration, prompts or model identities changed")
            _artifact(job, 'job-identity.json', canonical(_identity(state)))
            _artifact(job, 'source.original' + source.suffix.lower(), text)
            manifest = parse_document(text, **config['parser'])
            if manifest.to_dict() != state['manifest']:
                raise ValueError("Manifest identity changed")
            batches = make_batches(manifest)
            _validate_saved(job, state, manifest, batches)
            if state['baseline_sha256'] is not None:
                current_hash = _editable(job, state)[2]
                if current_hash != state['current_revision']:
                    state.update(active_approval=None, human_approved=False, generation_complete=False,
                                 phase='spanish_revision_changed')
                    save_state(job, state)
            if approve_spanish is not None:
                reviewed = state['revisions'].get(approve_spanish)
                if (reviewed is None or reviewed['review_sha256'] is None
                        or approve_spanish != state['current_revision']
                        or _editable(job, state)[2] != approve_spanish):
                    raise ValueError("Approval requires a complete review of the current exact Spanish revision; resume without approval first")
            for index in range(len(state['spanish_results']), len(batches)):
                _source_unchanged(state)
                if progress:
                    progress('es-ES', index + 1, len(batches))
                batch = batches[index]
                result = transformer.transform(_items(batch), 'es-ES', _context(manifest, batch))
                _validate_generated(result, _items(batch), 'es-ES', transformer.config)
                state['spanish_results'].append(result)
                save_state(job, state)
            _source_unchanged(state)
            baseline = _values(state['spanish_results'])
            baseline_text = manifest.assemble(baseline)
            if state['baseline_sha256'] is None:
                publish(job, 'spanish.baseline' + source.suffix.lower(), baseline_text)
                publish(job, 'spanish.baseline-evidence.json', canonical(state['spanish_results']))
                initialize_editable(job, state['editable_file'], baseline_text)
                state['baseline_sha256'] = sha(baseline_text)
                save_state(job, state)
            _, edited, key = _editable(job, state)
            if approve_spanish is not None and approve_spanish != key:
                raise ValueError("Approval SHA does not match current editable Spanish")
            replacements = map_revision(manifest, baseline, edited)
            if key != state['current_revision']:
                state.update(current_revision=key, active_approval=None, human_approved=False,
                             generation_complete=False, phase='spanish_review')
            if key not in state['revisions']:
                revision = {'revision_sha256': key, 'replacements': replacements,
                            'reviews': [], 'review_sha256': None, 'approval': None,
                            'english': {locale: {'results': [], 'crosschecks': [], 'published': False}
                                        for locale in ENGLISH}}
                publish(job, _name(key, 'es-ES', source.suffix.lower()), edited)
                publish(job, _name(key, 'identity', '.json'), canonical(_revision_identity(state, revision)))
                state['revisions'][key] = revision
            revision = state['revisions'][key]
            save_state(job, state)
            for index in range(len(revision['reviews']), len(batches)):
                _unchanged(job, state, revision)
                batch = batches[index]
                if progress:
                    progress('es-ES review', index + 1, len(batches))
                result = transformer.review(_items(batch), {p.id: replacements[p.id] for p in batch},
                                            'es-ES', _context(manifest, batch))
                validate_review(result, _items(batch), 'es-ES', transformer.config, _context(manifest, batch))
                if result['replacements'] != {p.id: replacements[p.id] for p in batch}:
                    raise ValueError("Review altered exact Spanish candidate")
                revision['reviews'].append(result)
                save_state(job, state)
            _unchanged(job, state, revision)
            publish(job, _name(key, 'spanish-review-evidence', '.json'), canonical(revision['reviews']))
            revision['review_sha256'] = digest(revision['reviews'])
            save_state(job, state)
            if approve_spanish is not None:
                if _spanish_status(state, revision, manifest) != 'accepted' and not acknowledge_review:
                    raise ValueError("Spanish requires review; explicit --acknowledge-review is required")
                if revision['approval'] is None:
                    revision['approval'] = _approval(state, revision, bool(acknowledge_review))
                    publish(job, _name(key, 'approval', '.json'), canonical(revision['approval']))
                state['active_approval'] = digest(revision['approval'])
                save_state(job, state)
            if state['active_approval'] is not None:
                for locale in ENGLISH:
                    stage = revision['english'][locale]
                    for index, batch in enumerate(batches):
                        _unchanged(job, state, revision)
                        if len(stage['results']) <= index:
                            if progress:
                                progress(locale, index + 1, len(batches))
                            items = _items(batch, replacements)
                            result = transformer.transform(items, locale, _context(manifest, batch, replacements))
                            _validate_generated(result, items, locale, transformer.config)
                            stage['results'].append(result)
                            save_state(job, state)
                        _unchanged(job, state, revision)
                        if len(stage['crosschecks']) <= index:
                            result = transformer.review(_items(batch), stage['results'][index]['replacements'],
                                                        locale, _context(manifest, batch))
                            validate_review(result, _items(batch), locale, transformer.config, _context(manifest, batch))
                            if result['replacements'] != stage['results'][index]['replacements']:
                                raise ValueError("Crosscheck altered exact English candidate")
                            stage['crosschecks'].append(result)
                            save_state(job, state)
                    _unchanged(job, state, revision)
                    publish(job, _name(key, locale, source.suffix.lower()), manifest.assemble(_values(stage['results'])))
                    publish(job, _name(key, locale + '-evidence', '.json'), canonical(
                        {'results': stage['results'], 'crosschecks': stage['crosschecks']}))
                    stage['published'] = True
                    save_state(job, state)
            _unchanged(job, state, revision)
            _validate_saved(job, state, manifest, batches)
            summary = _summary(job, state, manifest, batches, revision)
            _unchanged(job, state, revision)
            state.update(phase=summary['phase'], generation_complete=summary['generation_complete'],
                         human_approved=summary['human_approved'], summary=summary)
            state.pop('last_error', None)
            save_state(job, state)
            return summary
        except (KeyError, TypeError, IndexError, AttributeError) as error:
            raise ValueError("Incomplete editorial checkpoint or evidence contract") from error
