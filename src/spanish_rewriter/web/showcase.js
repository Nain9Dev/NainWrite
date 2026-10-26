/**
 * The hero animation of the landing (specs/016-client-visual-redesign, UI-001).
 *
 * It replays a few bundled example sentences through the three phases of the pipeline: the
 * literal figures are detected, the Spanish is rewritten (a real word comparison, not a mock-up)
 * and the figures are checked against the result. No network request, no model run: it is an
 * illustration, and the page says so. Under reduced motion it shows one static final frame, and
 * the visitor can pause the loop at any time.
 */
import { diffWords, literalPresence, splitByLiterals } from './diff.js';

export const PHASES = ['detect', 'rewrite', 'verify'];

export const EXAMPLES = [
  {
    original: 'El cliente debe proveer las credenciales antes del día 5 de cada ciclo, por 14.500,00 €.',
    revised: 'El cliente debe proporcionar las credenciales antes del día 5 de cada ciclo, por 14.500,00 €.',
  },
  {
    original: 'Si la disponibilidad baja del 99,95% mensual, se aplicará una penalización del 5%.',
    revised: 'Si la disponibilidad baja del 99,95 % mensual, se aplicará una penalización del 5 %.',
  },
  {
    original: 'La garantía cubre defectos de software durante 12 meses a partir del 15 de octubre de 2026.',
    revised: 'La garantía cubre los defectos de software durante 12 meses a partir del 15 de octubre de 2026.',
  },
];

/** What one phase of one example shows: the text split into parts and, at the end, the figure checks. */
export function frameFor(example, phase) {
  if (phase === 'detect') return { phase, parts: splitByLiterals(example.original), checks: [] };

  if (phase === 'rewrite') {
    const parts = diffWords(example.original, example.revised).map((run) => ({
      text: run.text,
      kind: run.type === 'equal' ? 'plain' : run.type,
    }));
    return { phase, parts, checks: [] };
  }

  return { phase, parts: splitByLiterals(example.revised), checks: literalPresence(example.original, example.revised) };
}

const STEP_MS = 2200;

function render(nodes, frame, example) {
  nodes.stage.dataset.phase = frame.phase;
  nodes.text.replaceChildren(
    ...frame.parts.map((part) => {
      const node = document.createElement(part.kind === 'del' ? 'del' : part.kind === 'ins' ? 'ins' : part.kind === 'literal' ? 'mark' : 'span');
      node.textContent = part.text;
      return node;
    }),
  );

  nodes.steps.forEach((item, index) => {
    const active = PHASES[index] === frame.phase;
    item.classList.toggle('is-active', active);
    item.classList.toggle('is-done', index < PHASES.indexOf(frame.phase));
    if (active) item.setAttribute('aria-current', 'step');
    else item.removeAttribute('aria-current');
  });

  const preserved = frame.checks.filter((check) => check.present).length;
  nodes.result.textContent = frame.checks.length ? `${preserved} de ${frame.checks.length} cifras y fechas intactas` : '';
  nodes.result.hidden = !frame.checks.length;
  nodes.live.textContent = frame.checks.length
    ? `Ejemplo reescrito. ${preserved} de ${frame.checks.length} cifras y fechas intactas.`
    : '';
  void example;
}

/**
 * Binds the animation to the markup of the landing. `root` holds `[data-showcase-*]` nodes; the
 * function returns `{ stop }`. With reduced motion it renders the final frame once and starts no timer.
 */
export function mountShowcase(root, { reducedMotion = false } = {}) {
  const nodes = {
    stage: root.querySelector('[data-showcase-stage]'),
    text: root.querySelector('[data-showcase-text]'),
    steps: [...root.querySelectorAll('[data-showcase-step]')],
    result: root.querySelector('[data-showcase-result]'),
    live: root.querySelector('[data-showcase-live]'),
    toggle: root.querySelector('[data-showcase-toggle]'),
  };
  if (!nodes.stage || !nodes.text) return { stop() {} };

  let example = 0;
  let phase = 0;
  let timer = null;
  let paused = false;

  const show = () => render(nodes, frameFor(EXAMPLES[example], PHASES[phase]), EXAMPLES[example]);
  const stop = () => {
    clearInterval(timer);
    timer = null;
  };
  const tick = () => {
    phase += 1;
    if (phase === PHASES.length) {
      phase = 0;
      example = (example + 1) % EXAMPLES.length;
    }
    show();
  };
  const start = () => {
    if (!timer) timer = setInterval(tick, STEP_MS);
  };

  phase = PHASES.length - 1;
  show();

  if (reducedMotion) {
    if (nodes.toggle) nodes.toggle.hidden = true;
    return { stop };
  }

  phase = 0;
  show();
  start();

  nodes.toggle?.addEventListener('click', () => {
    paused = !paused;
    if (paused) stop();
    else start();
    nodes.toggle.textContent = paused ? 'Reanudar animación' : 'Pausar animación';
    nodes.toggle.setAttribute('aria-pressed', String(paused));
  });

  return { stop };
}
