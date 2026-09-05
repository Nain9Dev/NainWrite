import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from spanish_rewriter.document import parse_document, make_batches


class CorporateControlTests(unittest.TestCase):
    def test_draft_bank_has_paired_controls_without_gold_claims(self):
        bank = json.loads((ROOT / 'benchmark/corporate_review_controls.json').read_text(encoding='utf-8'))
        self.assertEqual('draft', bank['review_status'])
        cases = bank['cases']
        self.assertEqual([f'CORP-{n:03d}' for n in range(1, 13)], [c['id'] for c in cases])
        self.assertEqual(6, sum(c['expected_equivalent'] is True for c in cases))
        self.assertEqual(6, sum(c['expected_equivalent'] is False for c in cases))
        self.assertEqual({'es-ES', 'en-GB', 'en-US'}, {c['locale'] for c in cases})
        for case in cases:
            for field in ('source', 'candidate', 'reason', 'phenomenon'):
                self.assertTrue(case[field].strip())
            self.assertLess(len(case['source'].encode('utf-8')), 1800)
            self.assertLess(len(case['candidate'].encode('utf-8')), 1800)

    def test_frozen_smoke_has_lossless_structure_and_bounded_batches(self):
        source = (ROOT / 'tests/fixtures/corporate-review-smoke.md').read_text(encoding='utf-8')
        manifest = parse_document(source)
        self.assertEqual(source, manifest.assemble({p.id: p.text for p in manifest.editable}))
        self.assertTrue(make_batches(manifest))
        self.assertIn('El equipo revisará la documentación antes de la entrega.', source)
        self.assertIn('`Color Center`', source)
        self.assertIn('12', source)


if __name__ == '__main__':
    unittest.main()
