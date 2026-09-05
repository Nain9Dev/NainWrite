"""Finite local calibration with immutable case evidence and withheld labels."""

import json
from pathlib import Path
import re

from .document import literal_issues
from .document_review import validate_review
from .document_store import canonical, digest, job_lock, new_job_dir, publish, read_published_json, read_state, save_state, verify_artifact
from .ollama_client import OllamaError


def _load_bank(path):
    bank = json.loads(path.read_text(encoding='utf-8'))
    cases = bank.get('cases', [])
    if bank.get('review_status') != 'draft' or not cases or len(cases) > 100:
        raise ValueError('Expected a finite draft calibration bank')
    seen = set()
    for case in cases:
        key = case.get('id', '')
        if (not isinstance(key, str) or not re.fullmatch(r'[A-Z]+-\d{3}', key)
                or key in seen or case.get('locale') not in ('es-ES', 'en-GB', 'en-US')
                or type(case.get('expected_equivalent')) is not bool
                or ('expected_style_acceptable' in case and type(case['expected_style_acceptable']) is not bool)):
            raise ValueError('Invalid calibration identity, locale or label')
        seen.add(key)
        for field in ('source', 'candidate'):
            text = case.get(field)
            if not isinstance(text, str) or not text.strip() or len(text.encode('utf-8')) > 1800:
                raise ValueError('Calibration text must be nonempty and bounded')
    return bank


def _semantic_detection(record):
    return bool(record['deterministic_drift']) or any(
        a.get('audit') is not None and a['audit']['equivalent'] is False
        for a in (record['evidence']['audits'] if record['evidence'] else []))


def summarize(records):
    invalid = [r for r in records if not r['case']['expected_equivalent']]
    equivalent = [r for r in records if r['case']['expected_equivalent']]
    valid = [r for r in equivalent if r['case'].get('expected_style_acceptable', True)]
    bad_style = [r for r in records if r['case'].get('expected_style_acceptable') is False]
    accepted = lambda r: bool(r['evidence']) and r['evidence']['status'] == 'accepted'
    return dict(invalid_cases=len(invalid),
                invalid_semantically_detected=sum(_semantic_detection(r) for r in invalid),
                invalid_automatically_accepted=sum(accepted(r) for r in invalid),
                valid_cases=len(valid), valid_automatically_accepted=sum(accepted(r) for r in valid),
                equivalent_cases=len(equivalent),
                valid_semantically_rejected=sum(_semantic_detection(r) for r in equivalent),
                style_cases=len(bad_style), style_cases_flagged=sum(
                    bool(r['evidence']) and any('editorial:' in i or 'naturalness_below_threshold:' in i
                                               or 'professional_tone_below_threshold:' in i
                                               for i in r['evidence']['issues']) for r in bad_style),
                execution_errors=sum(r['evidence'] is None for r in records),
                invalid_audit_cases=sum(bool(r['evidence']) and any(a.get('audit') is None
                                        for a in r['evidence']['audits']) for r in records))


def _validate_record(record, case, transformer):
    if record['case'] != case or record['deterministic_drift'] != literal_issues(case['source'], case['candidate']):
        raise ValueError('Saved case or deterministic findings changed')
    if record['evidence'] is None:
        if not isinstance(record.get('execution_error'), str) or not record['execution_error'].startswith('OllamaError: '):
            raise ValueError('Missing evidence without an execution error')
    else:
        items = [dict(id=case['id'], text=case['source'], role='prose')]
        validate_review(record['evidence'], items, case['locale'], transformer.config, {})
        if record['evidence']['replacements'] != {case['id']: case['candidate']}:
            raise ValueError('Saved candidate changed')


def run_experiment(bank_path, transformer, *, output_dir=None, resume=None, progress=None):
    path = Path(bank_path).resolve(strict=True)
    bank = _load_bank(path)
    job = Path(resume).resolve(strict=True) if resume else new_job_dir(path, output_dir)
    with job_lock(job):
        state = read_state(job) if resume else dict(
            version='corporate-evaluation-v2', bank_sha256=digest(bank), configuration=transformer.config,
            review_status='draft', human_approved=False, results=[], complete=False)
        if (state.get('version') != 'corporate-evaluation-v2' or state['bank_sha256'] != digest(bank)
                or state['configuration'] != transformer.config or len(state['results']) > len(bank['cases'])):
            raise ValueError('Bank or configuration changed; start a new experiment')
        if state['review_status'] != 'draft' or state['human_approved'] is not False:
            raise ValueError('Calibration cannot claim human approval')
        for record, case in zip(state['results'], bank['cases']):
            _validate_record(record, case, transformer)
            verify_artifact(job, case['id'] + '.json', canonical(record))
        if state['complete'] and len(state['results']) != len(bank['cases']):
            raise ValueError('Incomplete case coverage cannot be complete')
        save_state(job, state)
        if progress:
            progress(f'Experiment: {job}')
        for case in bank['cases'][len(state['results']):]:
            if _load_bank(path) != bank:
                raise ValueError('Bank changed during evaluation')
            recovered = read_published_json(job, case['id'] + '.json')
            if recovered is not None:
                _validate_record(recovered, case, transformer)
                verify_artifact(job, case['id'] + '.json', canonical(recovered))
                state['results'].append(recovered)
                save_state(job, state)
                if progress:
                    progress(f"{case['id']}: recovered published evidence")
                continue
            record = dict(case=case, deterministic_drift=literal_issues(case['source'], case['candidate']))
            try:
                record['evidence'] = transformer.review(
                    [dict(id=case['id'], text=case['source'], role='prose')],
                    {case['id']: case['candidate']}, case['locale'], {})
            except OllamaError as error:
                record.update(evidence=None, execution_error=f'OllamaError: {error}')
            _validate_record(record, case, transformer)
            publish(job, case['id'] + '.json', canonical(record))
            state['results'].append(record)
            save_state(job, state)
            if progress:
                progress(f"{case['id']}: " + (record['evidence']['status'] if record['evidence'] else 'execution_error'))
        if _load_bank(path) != bank:
            raise ValueError('Bank changed during evaluation')
        summary = summarize(state['results'])
        passed = (summary['execution_errors'] == 0 and summary['invalid_audit_cases'] == 0
                  and summary['valid_semantically_rejected'] == 0
                  and summary['invalid_semantically_detected'] == summary['invalid_cases']
                  and summary['valid_automatically_accepted'] == summary['valid_cases']
                  and summary['style_cases_flagged'] == summary['style_cases'])
        state.update(complete=True, summary=summary, quality_gate_passed=passed)
        publish(job, 'results.json', canonical(state))
        save_state(job, state)
        return job, state
