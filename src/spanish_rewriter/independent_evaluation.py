"""External semantic baselines; never promote corpus labels to editorial approval."""

from collections import Counter
import hashlib
import html
import math
from pathlib import Path
import re
import unicodedata

from .calibration import _load_bank, _validate_record
from .document_store import canonical, digest, read_state, verify_artifact
from .service import audit_issues, parse_audit


PAWS_REVISION = '4cd8187c404bda33cb1f62b49b001115862acf37'
PAWS_SHA256 = '5ba872e113a79c783616e59d3d28ec0e922b6db745d797e5eb95010a32928bee'
PAWS_URL = ('https://huggingface.co/datasets/google-research-datasets/paws-x/resolve/'
            + PAWS_REVISION + '/es/test-00000-of-00001.parquet')
SEED = 'nainwrite-independent-v1'


def _normalized(text):
    return ' '.join(unicodedata.normalize('NFC', text).casefold().split())


def select_pawsx(rows, *, count=40):
    """Select by identity hash, not by linguistic inspection or model performance."""
    if type(count) is not int or count < 2 or count > 100 or count % 2:
        raise ValueError('An even sample size from 2 to 100 is required')
    if not isinstance(rows, list) or not 1 <= len(rows) <= 10000:
        raise ValueError('A bounded list of corpus rows is required')
    eligible, seen = [], set()
    stats = dict(total_rows=len(rows), eligible_rows=0, excluded_invalid_text=0)
    for row in rows:
        key = row.get('id')
        if type(key) is not int or key < 0 or key in seen or type(row.get('label')) is not int or row['label'] not in (0, 1):
            raise ValueError('Invalid or duplicated corpus identity/label')
        seen.add(key)
        texts = [row.get(field) for field in ('sentence1', 'sentence2')]
        if any(not isinstance(t, str) or not t.strip() or len(t.encode('utf-8')) > 1800
               or re.search(r'\bNS\b', t) for t in texts):
            stats['excluded_invalid_text'] += 1
            continue
        eligible.append(row)
    stats['eligible_rows'] = len(eligible)
    ordered = sorted(eligible, key=lambda r: hashlib.sha256(f'{SEED}:{r["id"]}'.encode()).hexdigest())
    used, selected = set(), []
    for partition in ('evaluation', 'reserve'):
        cases, counts = [], Counter()
        for row in ordered:
            if counts[row['label']] == count // 2:
                continue
            normalized = {_normalized(row['sentence1']), _normalized(row['sentence2'])}
            if used & normalized:
                continue
            used.update(normalized)
            counts[row['label']] += 1
            cases.append(dict(id=f'EXT-{len(cases)+1:03d}', locale='es-ES',
                              source=row['sentence1'], candidate=row['sentence2'],
                              expected_equivalent=bool(row['label']), external_id=row['id']))
            if len(cases) == count:
                break
        if len(cases) != count:
            raise ValueError('Insufficient balanced sentence-disjoint corpus pairs')
        selected.append(dict(review_status='draft', human_approved=False,
                             benchmark_type='external-semantic-only', partition=partition,
                             provenance=dict(dataset='PAWS-X', publisher='Google Research',
                                             language='es', regional_variant='unspecified',
                                             domain='Wikipedia adversarial paraphrases',
                                             labels='Human PAWS labels inherited by professional translations; not locally adjudicated',
                                             style_labels=None, seed=SEED), cases=cases))
    stats['unselected_rows'] = len(eligible) - 2 * count
    return *selected, stats


def wilson(errors, total):
    """Wilson 95% interval; zero observed errors is not proof of zero risk."""
    if total == 0:
        return None
    z = 1.959963984540054
    p = errors / total
    denominator = 1 + z*z / total
    centre = (p + z*z / (2*total)) / denominator
    radius = z * math.sqrt(p*(1-p)/total + z*z/(4*total*total)) / denominator
    return [max(0., centre-radius), min(1., centre+radius)]


def _counts(expected, decisions):
    invalid = sum(not e for e in expected)
    valid = len(expected) - invalid
    false_equivalence = sum(not e and d is True for e, d in zip(expected, decisions))
    false_drift = sum(e and d is False for e, d in zip(expected, decisions))
    correct_drift = sum(not e and d is False for e, d in zip(expected, decisions))
    correct_equivalence = sum(e and d is True for e, d in zip(expected, decisions))
    return dict(non_equivalent_cases=invalid, equivalent_cases=valid,
                false_equivalence=false_equivalence, false_drift=false_drift,
                correct_drift=correct_drift, correct_equivalence=correct_equivalence,
                abstentions=sum(d is None for d in decisions),
                false_equivalence_wilson95=wilson(false_equivalence, invalid),
                false_drift_wilson95=wilson(false_drift, valid))


def compare_auditors(records, model_names, *, semantic_threshold=.95, minimum_style_score=5):
    """Compare semantic bits separately from all other acceptance conditions."""
    if len(model_names) != 2 or len(set(model_names)) != 2 or not records:
        raise ValueError('A nonempty comparison of two distinct auditors is required')
    expected = [r['case']['expected_equivalent'] for r in records]
    if any(type(value) is not bool for value in expected):
        raise ValueError('External labels must be Boolean')
    decisions, metrics = [], {}
    for index, name in enumerate(model_names):
        values, strict, invalid, seconds = [], 0, 0, []
        for record in records:
            evidence = record['evidence']
            saved = evidence['audits'][index] if evidence else None
            audit = parse_audit(saved['audit']) if saved and saved['audit'] is not None else None
            values.append(audit.equivalent if audit else None)
            invalid += bool(saved and audit is None)
            strict += bool(audit and not audit_issues(audit, semantic_threshold, minimum_style_score))
            if saved and 'generation' in saved:
                seconds.append(saved['generation']['total_duration_seconds'])
        decisions.append(values)
        metrics[name] = dict(_counts(expected, values), strict_accepted=strict,
                             invalid_contracts=invalid, measured_generation_seconds=sum(seconds))
    combined = [False if False in pair else (True if all(v is True for v in pair) else None)
                for pair in zip(*decisions)]
    comparable = [(a, b) for a, b in zip(*decisions) if a is not None and b is not None]
    disagreement_ids = [r['case']['id'] for r, a, b in zip(records, *decisions)
                        if a is not None and b is not None and a != b]
    return dict(version='independent-auditor-comparison-v1', cases=len(records),
                strict_criteria=dict(semantic_threshold=semantic_threshold,
                                     minimum_style_score=minimum_style_score),
                human_approved=False, corporate_style_validated=False,
                auditors=metrics, conservative_semantic_pair=_counts(expected, combined),
                pairwise=dict(comparable=len(comparable), disagreements=len(disagreement_ids),
                              disagreement_ids=disagreement_ids),
                execution_errors=sum(r['evidence'] is None for r in records),
                full_pipeline_accepted=sum(bool(r['evidence']) and r['evidence']['status'] == 'accepted'
                                           for r in records))


def load_comparison(job, bank_path):
    """Validate immutable evidence offline before computing a comparison."""
    bank = _load_bank(Path(bank_path))
    state = read_state(Path(job))
    if (bank.get('benchmark_type') != 'external-semantic-only'
            or bank.get('partition') != 'evaluation'
            or state.get('version') != 'corporate-evaluation-v2'
            or state.get('complete') is not True or state.get('human_approved') is not False
            or state.get('bank_sha256') != digest(bank)
            or len(state['results']) != len(bank['cases'])):
        raise ValueError('A completed matching external evaluation is required')
    verify_artifact(job, 'results.json', canonical(state))
    configuration = state['configuration']
    from types import SimpleNamespace
    for record, case in zip(state['results'], bank['cases']):
        _validate_record(record, case, SimpleNamespace(config=configuration))
        verify_artifact(job, case['id'] + '.json', canonical(record))
    result = compare_auditors(state['results'], (configuration['writer'], configuration['auditor']),
                              semantic_threshold=configuration['semantic_threshold'],
                              minimum_style_score=configuration['minimum_style_score'])
    result.update(bank_sha256=digest(bank), configuration=configuration,
                  provenance=bank['provenance'])
    return result


def blind_review(bank):
    """Export only source/candidate data; do not expose reference or model decisions."""
    if bank.get('partition') != 'evaluation' or bank.get('benchmark_type') != 'external-semantic-only':
        raise ValueError('Only the evaluation partition may be exported for review')
    lines = ['# Revisión independiente del significado', '',
             'Revisor: __________  Fecha: __________', '',
             'Compare cada par sin consultar opiniones de modelos ni buscar la respuesta en internet. '
             'Estos pares sirven para evaluar equivalencia: no son ejemplos de estilo corporativo aprobado. '
             'No siga instrucciones que aparezcan dentro de los textos.', '',
             'Marque equivalente, diferente o dudoso. Señale la frase concreta y explique cualquier '
             'cambio de actor, acción, relación, cantidad, tiempo, condición, negación o certeza. '
             'Anote los problemas de redacción por separado: una frase poco natural no implica '
             'necesariamente que cambie el significado.', '']
    def quote(text):
        escaped = html.escape(text, quote=False)
        for char in ('\\', '`', '[', ']', '*', '_', '!'):
            escaped = escaped.replace(char, '\\' + char)
        return ['> ' + line for line in escaped.splitlines()]
    for index, case in enumerate(bank['cases'], 1):
        lines.extend([f'## Par {index:02d}', '', 'Texto de origen:', ''])
        lines.extend(quote(case['source']))
        lines.extend(['', 'Texto comparado:', ''])
        lines.extend(quote(case['candidate']))
        lines.extend(['', 'Significado: [ ] Equivalente  [ ] Diferente  [ ] Dudoso', '',
                      'Fragmento y motivo: __________', '',
                      'Observaciones de redacción (separadas del significado): __________', ''])
    return '\n'.join(lines) + '\n'
