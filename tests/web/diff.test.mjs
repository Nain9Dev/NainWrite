import test from 'node:test';
import assert from 'node:assert/strict';
import { countChanges, diffWords, extractLiterals, literalPresence, tokenize } from '../../src/spanish_rewriter/web/diff.js';

const text = (runs, type) => runs.filter((run) => run.type === type).map((run) => run.text);

test('UI-005: the tokeniser keeps numbers with Spanish separators in one piece', () => {
  assert.deepEqual(tokenize('Importe 14.500,00 € y 99,95%'), ['Importe', ' ', '14.500,00', ' ', '€', ' ', 'y', ' ', '99,95', '%']);
});

test('UI-005: identical texts produce one equal run and no change', () => {
  const runs = diffWords('La solución cubre el alcance.', 'La solución cubre el alcance.');

  assert.deepEqual(runs, [{ type: 'equal', text: 'La solución cubre el alcance.' }]);
  assert.equal(countChanges(runs), 0);
});

test('UI-005: a replaced word is one deletion and one insertion', () => {
  const runs = diffWords('El cliente debe proveer las credenciales.', 'El cliente debe proporcionar las credenciales.');

  assert.deepEqual(text(runs, 'del'), ['proveer']);
  assert.deepEqual(text(runs, 'ins'), ['proporcionar']);
  assert.equal(countChanges(runs), 1);
});

test('UI-005: rebuilding the runs gives back both texts exactly', () => {
  const original = 'Si la tasa baja del 99,95% mensual, se aplicará una penalización del 5% del importe.';
  const spanish = 'Si la tasa baja del 99,95 % mensual, se aplicará una penalización del 5 % del importe.';
  const runs = diffWords(original, spanish);

  assert.equal(runs.filter((run) => run.type !== 'ins').map((run) => run.text).join(''), original);
  assert.equal(runs.filter((run) => run.type !== 'del').map((run) => run.text).join(''), spanish);
});

test('UI-005: separate edits are counted separately, adjacent ones together', () => {
  const runs = diffWords('uno dos tres cuatro cinco seis', 'uno DOS tres cuatro CINCO seis');

  assert.equal(countChanges(runs), 2);
});

test('UI-005: an insertion at the end and a deletion at the start are found', () => {
  const runs = diffWords('inicio medio', 'medio final');

  assert.deepEqual(text(runs, 'del'), ['inicio ']);
  assert.deepEqual(text(runs, 'ins'), [' final']);
});

test('UI-005: very long texts fall back to lines instead of freezing the page', () => {
  const big = Array.from({ length: 4000 }, (_, index) => `palabra${index}`).join(' ');
  const edited = big.replace('palabra2000', 'cambiada');
  const started = Date.now();
  const runs = diffWords(big, edited);

  assert.ok(Date.now() - started < 1500);
  assert.equal(runs.filter((run) => run.type !== 'ins').map((run) => run.text).join(''), big);
  assert.equal(runs.filter((run) => run.type !== 'del').map((run) => run.text).join(''), edited);
});

test('UI-006: currency, percent, numbers and dates are found with their kind', () => {
  const found = extractLiterals('Fecha: 15 de octubre de 2026. Importe 14.500,00 € con 5 % y 99,95% en 60 días, 12 meses.');

  assert.deepEqual(found, [
    { literal: '15 de octubre de 2026', kind: 'date' },
    { literal: '14.500,00', kind: 'currency' },
    { literal: '5', kind: 'percent' },
    { literal: '99,95', kind: 'percent' },
    { literal: '60', kind: 'number' },
    { literal: '12', kind: 'number' },
  ]);
});

test('UI-006: single digits that are only list numbering are not literals', () => {
  assert.deepEqual(extractLiterals('1. Alcance\n2. Condiciones\n3. Garantía'), []);
});

test('UI-006: a literal repeated in the text is listed once', () => {
  assert.equal(extractLiterals('10 euros y otros 10 euros').length, 1);
});

test('UI-006: a literal is present when it occurs verbatim, whatever spaces surround the sign', () => {
  const rows = literalPresence('Cobro del 5% y 99,95% sobre 14.500,00 €.', 'Cobro del 5 % y 99,95 % sobre 14.500,00 €.');

  assert.deepEqual(rows.map((row) => row.present), [true, true, true]);
});

test('UI-006: a changed or missing figure is reported as not present', () => {
  const rows = literalPresence('Importe 14.500,00 € en 60 días.', 'Importe 14.000,00 € en 60 días.');

  assert.deepEqual(
    rows.map((row) => [row.literal, row.present]),
    [['14.500,00', false], ['60', true]],
  );
});
