import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from spanish_rewriter.document_evidence import validate_transformation
from spanish_rewriter.document_review import validate_review
from test_editorial_job import service


class DocumentEditorialTests(unittest.TestCase):
    def test_redundant_conformance_definition_is_flagged_without_changing_scope(self):
        worker = service()
        source = 'The benchmark checks conformance rather than execution speed.'
        candidate = 'Las pruebas de conformidad comprueban la conformidad, no la velocidad de ejecución.'
        result = worker.review([dict(id='p1', text=source)], {'p1': candidate}, 'es-ES', {})
        self.assertIn('p1:editorial:redundant_conformance_definition', result['issues'])
        self.assertEqual(candidate, result['replacements']['p1'])
        good = 'Las pruebas comprueban la conformidad, no la velocidad de ejecución.'
        result = worker.review([dict(id='p1', text=source)], {'p1': good}, 'es-ES', {})
        self.assertFalse(any('editorial:' in issue for issue in result['issues']))

    def test_calque_and_empty_emphasis_reach_repair_despite_perfect_audits(self):
        worker = service()
        items = [dict(id='p1', text='El conjunto de referencia está poblado. Es importante destacar que falta validarlo.')]
        result = worker.transform(items, 'es-ES', {})
        self.assertEqual('review_required', result['status'])
        self.assertEqual(2, len(result['attempts']))
        self.assertIn('p1:editorial:populated_data_calque', result['issues'])
        self.assertIn('p1:editorial:empty_emphasis', result['issues'])
        repair = next(data for _, data, _ in worker.client.calls if data['task'] == 'repair')
        self.assertIn('p1:editorial:empty_emphasis', repair['findings'])
        validate_transformation(result, items, 'es-ES', worker.config)

    def test_review_recomputes_editorial_findings_and_rejects_suppression(self):
        worker = service()
        items = [dict(id='p1', text='The reference dataset contains data.')]
        result = worker.review(items, {'p1': 'El conjunto de referencia está poblado.'}, 'es-ES', {})
        self.assertEqual('review_required', result['status'])
        self.assertIn('p1:editorial:populated_data_calque', result['issues'])
        validate_review(result, items, 'es-ES', worker.config, {})
        forged = copy.deepcopy(result)
        forged['issues'] = []
        forged['status'] = 'accepted'
        with self.assertRaises(ValueError):
            validate_review(forged, items, 'es-ES', worker.config, {})

    def test_good_prose_geography_and_quoted_expressions_do_not_trigger(self):
        worker = service()
        for text in ('El conjunto de referencia contiene datos.',
                     'El valle está poblado. El conjunto de datos sigue vacío.',
                     'El informe cita «es importante destacar que».',
                     "La expresión 'es importante destacar que' aparece en el informe.",
                     'La expresión ‘es importante destacar que’ aparece en el informe.',
                     'La expresión "está poblado" figura en el conjunto de ejemplos.',
                     'La etiqueta `es importante destacar que` se conserva.',
                     'Consulte [es importante destacar que](https://example.org).'):
            with self.subTest(text=text):
                result = worker.review([dict(id='p1', text=text)], {'p1': text}, 'es-ES', {})
                self.assertFalse(any('editorial:' in issue for issue in result['issues']))

    def test_apostrophes_do_not_hide_unquoted_editorial_findings(self):
        worker = service()
        text = "El catálogo de O'Connor indica que es importante destacar que D'Angelo participará."
        result = worker.review([dict(id='p1', text=text)], {'p1': text}, 'es-ES', {})
        self.assertIn('p1:editorial:empty_emphasis', result['issues'])

    def test_rules_do_not_run_on_english_or_mislabel_semantic_equivalence(self):
        worker = service()
        items = [dict(id='p1', text='Es importante destacar que existe una condición.')]
        spanish = worker.review(items, {'p1': items[0]['text']}, 'es-ES', {})
        self.assertIn('p1:editorial:empty_emphasis', spanish['issues'])
        self.assertTrue(all(a['audit']['equivalent'] for a in spanish['audits']))
        english = worker.review(items, {'p1': items[0]['text']}, 'en-GB', {})
        self.assertFalse(any('editorial:' in issue for issue in english['issues']))
