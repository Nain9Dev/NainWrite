import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from spanish_rewriter.document import parse_document
from spanish_rewriter.document_revision import map_revision


class DocumentRevisionTests(unittest.TestCase):
    def check(self, original, edited):
        manifest = parse_document(original)
        values = {p.id: p.text for p in manifest.editable}
        return manifest, map_revision(manifest, values, edited)

    def test_unchanged_and_ordinary_sentence_edits_preserve_crlf(self):
        source = '# Título\r\n\r\nUn informe claro.\r\n'
        for edited in (source, source.replace('claro', 'preciso')):
            manifest, values = self.check(source, edited)
            self.assertEqual(edited, manifest.assemble(values))

    def test_table_cell_edit_preserves_code(self):
        original = '| Texto claro | Otro texto |\n|---|---|\n```py\nvalue = 1\n```\n'
        edited = original.replace('claro', 'preciso')
        manifest, values = self.check(original, edited)
        self.assertEqual(edited, manifest.assemble(values))
        with self.assertRaises(ValueError):
            self.check(original, original.replace('value = 1', 'value = 2'))

    def test_structural_deletion_empty_prose_and_inline_changes_rejected(self):
        source = '# Título\n\nUn texto claro.\n'
        for edited in (source.replace('# ', ''), '# Título\n\n',
                       source.replace('claro', '**claro**'), source.replace('\n\n', '\n')):
            with self.subTest(edited=edited), self.assertRaises(ValueError):
                self.check(source, edited)

    def test_full_line_thematic_breaks_and_setext_underlines_are_rejected(self):
        for edited in ('---\n', '- - -\n', '-  -  -\n'):
            with self.subTest(edited=edited), self.assertRaises(ValueError):
                self.check('Texto claro.\n', edited)
        with self.assertRaises(ValueError):
            self.check('Título\nTexto claro.\n', 'Título\n===\n')
        for underline in ('=', '==', '-', '--'):
            with self.subTest(underline=underline), self.assertRaises(ValueError):
                self.check('Título\nTexto claro.\n', f'Título\n{underline}\n')

    def test_empty_atx_heading_and_list_markers_are_rejected_only_as_full_prose_lines(self):
        for marker in ('#', '##', '######', '-', '+'):
            with self.subTest(marker=marker), self.assertRaises(ValueError):
                self.check('Texto claro.\n', f'{marker}\n')
        for source, edited in (
            ('# Título\n', '# #\n'),
            ('- Elemento\n', '- -\n'),
            ('+ Elemento\n', '+ +\n'),
        ):
            with self.subTest(source=source, edited=edited), self.assertRaises(ValueError):
                self.check(source, edited)
        for source, edited in (
            ('# Texto claro.\n', '# Texto preciso.\n'),
            ('- Texto claro.\n', '- Texto preciso.\n'),
            ('Texto claro.\n', '#hashtag\n'),
            ('Texto claro.\n', '+texto\n'),
            ('| Texto claro |\n|---|\n', '| # |\n|---|\n'),
            ('| Texto claro |\n|---|\n', '| + |\n|---|\n'),
        ):
            with self.subTest(source=source, edited=edited):
                manifest, values = self.check(source, edited)
                self.assertEqual(edited, manifest.assemble(values))

    def test_unambiguous_prose_punctuation_and_table_cells_remain_editable(self):
        source = 'El informe —claro y preciso— confirma la calidad.\n'
        _, values = self.check(source, source.replace('claro', 'riguroso'))
        self.assertEqual('El informe —riguroso y preciso— confirma la calidad.', values['p00000'])
        _, values = self.check('Texto claro.\n', '=\n')
        self.assertEqual('=', values['p00000'])
        table = '| Texto claro |\n|---|\n'
        _, values = self.check(table, table.replace('Texto claro', '='))
        self.assertIn('=', values.values())

    def test_split_boundary_edits_rejected(self):
        source = ('Una frase breve. ' * 200).rstrip() + '\n'
        manifest = parse_document(source)
        first, second = manifest.editable[:2]
        edited = source[:first.end - 4] + 'cambio' + source[second.start + 4:]
        with self.assertRaises(ValueError):
            self.check(source, edited)

    def test_duplicate_unchanged_maps_but_ambiguous_edit_rejected(self):
        source = 'El mismo texto.\n\nEl mismo texto.\n'
        self.check(source, source)
        with self.assertRaises(ValueError):
            self.check(source, source.replace('mismo', 'nuevo', 1))

    def test_protected_literals_and_moved_inline_markers_rejected(self):
        source = 'El valor es 12 y usa `code` en https://example.org.\n'
        for edited in (source.replace('12', '13'), source.replace('`code`', '`other`'),
                       source.replace('example.org', 'example.com')):
            with self.subTest(edited=edited), self.assertRaises(ValueError):
                self.check(source, edited)
        with self.assertRaises(ValueError):
            self.check('Texto *claro* y preciso.\n', 'Texto claro y *preciso*.\n')
        with self.assertRaises(ValueError):
            self.check('Primero 12 y después 34.\n', 'Primero 34 y después 12.\n')
