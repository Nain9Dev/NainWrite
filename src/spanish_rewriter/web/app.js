'use strict';

import { mockDispatch, mockWorkbench } from "./mock-workbench.js";
import { countChanges, diffWords, literalPresence } from "./diff.js";
import { mountShowcase } from "./showcase.js";

const $ = (id) => document.getElementById(id);
const token = document.querySelector('meta[name="nainwrite-token"]')?.content || 'demo-token';
const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

const isStaticHost = () => {
  if (typeof window === "undefined") return false;
  const host = window.location.hostname;
  return host.endsWith("naindev.com") || host.endsWith("github.io") || window.location.protocol === "file:" || Boolean(window.__NAINWRITE_MOCK__);
};

let useMock = isStaticHost();

let selected = null;
let current = null;
let state = null;
let dirty = false;

const labels = {
  ready: 'Listo: tres versiones aprobadas',
  queued: 'En cola',
  running: 'Procesando',
  extraction_review: 'Revisar extracción',
  spanish_review: 'Revisar español',
  spanish_edited: 'Español pendiente de nueva revisión',
  final_review: 'Revisión final pendiente',
  paused: 'Pausado',
  failed: 'Requiere atención'
};

const locales = {
  'es-ES': 'Español de España',
  'en-US': 'Inglés de Estados Unidos',
  'en-GB': 'Inglés del Reino Unido'
};

const STEPS = ['Extracción', 'Español', 'Traducción', 'Aprobación'];

/**
 * Index of the stage a document is in, 0 to 3, or 4 once it is ready (UI-004). Derived from the
 * status and, for the statuses that do not say it (queued, paused, failed), from what the
 * document already holds.
 */
function stageIndex(record) {
  if (record.status === 'ready') return 4;
  if (record.status === 'final_review') return 3;
  if (record.status === 'spanish_review' || record.status === 'spanish_edited') return 1;
  if (record.status === 'extraction_review') return 0;
  if (record.exports && Object.keys(record.exports).length) return 3;
  if (record.result) return 1;
  return 0;
}

let noticeTimer = null;

function notify(text) {
  const node = $('notice');
  if (!node) return;
  node.textContent = text;
  clearTimeout(noticeTimer);
  // A message that nobody dismisses would stay for ever: the toast clears itself.
  if (text) noticeTimer = setTimeout(() => { node.textContent = ''; }, 8000);
}

function updateEnvBadge() {
  document.documentElement.classList.toggle('app--local', !useMock);
  const badge = document.querySelector('.local');
  if (!badge) return;
  if (useMock) {
    badge.textContent = 'Demo interactiva (Navegador)';
    badge.setAttribute('title', 'Ejecución en cliente sobre motor de dominio simulado');
    badge.classList.add('local--demo');
  } else {
    badge.textContent = 'Trabajo local';
    badge.removeAttribute('title');
    badge.classList.remove('local--demo');
  }
}

async function api(path, body) {
  const started = performance.now();
  let result;

  if (useMock) {
    result = await mockDispatch(path, body);
  } else {
    try {
      const response = await fetch(path, {
        method: body ? 'POST' : 'GET',
        headers: {
          'X-NainWrite-Token': token,
          ...(body ? { 'Content-Type': 'application/json' } : {})
        },
        body: body ? JSON.stringify(body) : undefined
      });

      if (response.status === 404 || !response.ok) {
        if (response.status === 404) {
          useMock = true;
          updateEnvBadge();
          result = await mockDispatch(path, body);
        } else {
          const error = await response.json().catch(() => ({}));
          throw new Error(error.error || 'No se pudo completar la operación');
        }
      } else {
        result = await response.json();
      }
    } catch (err) {
      // Si la conexión falla (offline / hosting estático), conmuta al motor en memoria
      useMock = true;
      updateEnvBadge();
      result = await mockDispatch(path, body);
    }
  }

  const duration = Math.max(1, Math.round(performance.now() - started));
  if (typeof window !== "undefined") {
    window.dispatchEvent(new CustomEvent("nain:telemetry", {
      detail: {
        type: body ? "EditorialCommand" : "Query",
        name: `${body ? "POST" : "GET"} ${path}`,
        latencyMs: duration,
        status: 200,
        payload: { path, action: body?.action || path, runtime: useMock ? "InBrowserMockWorkbench" : "LocalPythonOllama" }
      }
    }));
  }

  return result;
}

async function action(act, data = {}) {
  return api('/api/action', { action: act, ...data });
}

async function bytes(path) {
  if (useMock) {
    return mockWorkbench.generateBlob(path);
  }

  try {
    const response = await fetch('/api/file?path=' + encodeURIComponent(path), {
      headers: { 'X-NainWrite-Token': token }
    });
    if (!response.ok) throw new Error('No se pudo leer el archivo local');
    return response.blob();
  } catch {
    return mockWorkbench.generateBlob(path);
  }
}

async function download(path) {
  const blob = await bytes(path);
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = path.split('/').pop();
  a.click();
  setTimeout(() => URL.revokeObjectURL(url), 10000);
}

function button(text, callback, style = 'secondary') {
  const b = document.createElement('button');
  b.textContent = text;
  b.className = style;
  b.type = 'button';
  b.addEventListener('click', () => guard(callback));
  return b;
}

async function guard(callback) {
  try {
    notify('');
    await callback();
    await refreshState();
  } catch (error) {
    notify(error.message);
  }
}

function pips(index) {
  const bar = document.createElement('span');
  bar.className = 'pips';
  bar.setAttribute('aria-hidden', 'true');
  for (let step = 0; step < STEPS.length; step += 1) {
    const pip = document.createElement('i');
    if (step < index) pip.className = 'is-done';
    else if (step === index) pip.className = 'is-active';
    bar.append(pip);
  }
  return bar;
}

function renderStepper(index) {
  $('stepper').replaceChildren(
    ...STEPS.map((name, step) => {
      const item = document.createElement('li');
      const number = document.createElement('span');
      number.setAttribute('aria-hidden', 'true');
      number.textContent = step < index ? '✓' : String(step + 1);
      const label = document.createElement('b');
      label.textContent = name;
      item.append(number, label);
      if (step < index) {
        item.className = 'is-done';
        // The tick is decorative; a screen reader needs the word.
        const done = document.createElement('span');
        done.className = 'visually-hidden';
        done.textContent = ' (hecho)';
        label.append(done);
      } else if (step === index) {
        item.className = 'is-active';
        item.setAttribute('aria-current', 'step');
      }
      return item;
    })
  );
}

async function refreshState() {
  state = await api('/api/state');
  $('pause').textContent = state.paused ? 'Continuar cola' : 'Pausar cola';

  const nav = $('documents');
  nav.replaceChildren();

  for (const record of Object.values(state.documents)) {
    const b = button('', () => select(record.id));
    b.className = 'document-card';
    b.setAttribute('aria-current', String(record.id === selected));

    const name = document.createElement('strong');
    name.textContent = record.name;

    const status = document.createElement('span');
    status.textContent = (labels[record.status] || record.status) + ' · ' + record.progress;

    b.append(name, status, pips(stageIndex(record)));
    nav.append(b);
  }

  if (selected && state.documents[selected]) {
    $('progress').textContent = state.documents[selected].progress;
    $('stage').textContent = labels[state.documents[selected].status] || state.documents[selected].status;
    renderStepper(stageIndex(state.documents[selected]));
    if (current && !dirty && current.status !== state.documents[selected].status) {
      await select(selected);
    }
  }
}

/** The side-by-side reading of original and Spanish, computed here from the two texts (UI-005, UI-006). */
function renderComparison() {
  const original = current.intake?.text ?? '';
  const spanish = current.spanish ?? '';
  const runs = diffWords(original, spanish);

  $('compare').replaceChildren(
    ...runs.map((run) => {
      if (run.type === 'equal') return document.createTextNode(run.text);
      const node = document.createElement(run.type === 'del' ? 'del' : 'ins');
      node.textContent = run.text;
      return node;
    })
  );
  const changes = countChanges(runs);
  $('change-count').textContent = changes ? String(changes) : '';

  const rows = literalPresence(original, spanish);
  $('literals').replaceChildren(
    ...rows.map((row) => {
      const item = document.createElement('li');
      item.className = row.present ? '' : 'is-missing';
      item.textContent = (row.present ? '✓ ' : '✗ ') + row.literal;
      item.title = row.present ? 'Aparece igual en el español' : 'No aparece igual en el español: revísalo';
      return item;
    })
  );

  const missing = rows.filter((row) => !row.present).length;
  const verdict = $('verdict');
  verdict.replaceChildren();
  if (rows.length) {
    const chip = document.createElement('span');
    chip.className = missing ? 'chip chip--warn' : 'chip';
    chip.textContent = missing
      ? `Revisa ${missing} ${missing === 1 ? 'cifra que no aparece' : 'cifras que no aparecen'} igual en el español`
      : `Cifras y fechas intactas: ${rows.length} de ${rows.length}`;
    verdict.append(chip);
  }
}

function showTab(name) {
  for (const tab of document.querySelectorAll('[data-tab]')) {
    const active = tab.dataset.tab === name;
    tab.setAttribute('aria-selected', String(active));
    tab.tabIndex = active ? 0 : -1;
    $('panel-' + tab.dataset.tab).hidden = !active;
  }
}

async function select(key) {
  if (dirty && key !== selected) {
    notify('Guarda o vuelve a cargar tus cambios antes de cambiar de documento.');
    return;
  }

  current = await api('/api/document?id=' + encodeURIComponent(key));
  selected = key;
  dirty = false;

  $('empty').hidden = true;
  $('document').hidden = false;
  $('title').textContent = current.name;
  $('stage').textContent = labels[current.status] || current.status;
  $('progress').textContent = current.progress;
  $('error').textContent = current.error || '';
  renderStepper(stageIndex(current));
  $('resume').hidden = !current.actions.resume;
  $('original').hidden = !current.intake;
  // Only the panel of the stage the document is in (UI-004): the earlier ones stay in the stepper,
  // and the page stops growing into one long scroll as a document advances.
  const stage = stageIndex(current);
  $('extraction-section').hidden = !current.intake || stage !== 0;
  $('spanish-section').hidden = !current.result || stage !== 1;
  $('exports-section').hidden = !Object.keys(current.exports || {}).length || stage < 3;

  if (current.intake) {
    $('extraction').value = current.intake.text;
    $('extraction').readOnly = !current.actions.edit_extraction;
    $('extraction-actions').hidden = !current.actions.edit_extraction;
    $('complete').checked = false;
    $('extraction-note').value = '';

    const pages = $('pages');
    pages.replaceChildren();

    for (const page of current.intake.pages) {
      const details = document.createElement('details');
      const summary = document.createElement('summary');
      summary.textContent = 'Página ' + page.number + ' · ' + (page.method === 'ocr' ? 'Lectura mediante OCR' : 'Texto extraído');

      const note = document.createElement('p');
      note.className = 'page-note';
      note.textContent = 'Comprueba orden, cifras, tablas, notas e imágenes. ' + (page.extraction_error || '');

      details.append(summary, note);
      pages.append(details);
    }
  }

  if (current.result) {
    $('spanish').value = current.spanish;
    $('spanish').readOnly = !current.actions.edit_spanish;
    $('save-spanish').disabled = !current.actions.edit_spanish;
    $('review-spanish').disabled = !current.actions.review_spanish;
    $('diff').textContent = current.diff;
    $('review').textContent = current.review;
    $('translation-actions').hidden = !current.actions.translate;
    $('resolved').checked = false;
    $('acknowledge').checked = false;
    $('spanish-note').value = '';
    renderComparison();
    showTab('changes');
  }

  const exports = $('exports');
  exports.replaceChildren();

  for (const [locale, artifact] of Object.entries(current.exports || {})) {
    const card = document.createElement('div');
    card.className = 'export-card';

    const title = document.createElement('strong');
    title.textContent = locales[locale] || locale;

    const controls = document.createElement('div');
    controls.className = 'actions';
    controls.append(
      button('PDF', () => download(artifact.pdf)),
      button('Markdown', () => download(artifact.markdown)),
      button('Markdown e imágenes', () => download(artifact.bundle))
    );

    const preview = document.createElement('details');
    const summary = document.createElement('summary');
    summary.textContent = 'Leer el documento completo';

    const text = document.createElement('pre');
    text.className = 'locale-preview';
    text.textContent = artifact.text;

    preview.append(summary, text);
    card.append(title, preview, controls);

    if (current.final_approvals && current.final_approvals[locale]) {
      const status = document.createElement('p');
      status.className = 'approved';
      status.textContent = 'Aprobación final registrada para esta versión.';
      card.append(status);
    } else {
      const label = document.createElement('label');
      label.textContent = 'Nota de tu revisión final';
      const input = document.createElement('input');
      input.placeholder = 'Confirma fidelidad, naturalidad y variante del idioma';
      label.append(input);

      card.append(
        label,
        button('Aprobar esta versión', async () => {
          await action('approve_final', {
            key: selected,
            locale,
            revision: artifact.text_sha256,
            note: input.value
          });
          await select(selected);
        }, 'primary')
      );
    }

    exports.append(card);
  }
}

function base64(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result.split(',')[1]);
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
}

$('upload-form').addEventListener('submit', (event) => {
  event.preventDefault();
  guard(async () => {
    const assets = await Promise.all(
      [...$('assets').files].map(async (file) => ({
        name: file.name,
        content: await base64(file)
      }))
    );

    for (const file of $('uploads').files) {
      const result = await action('upload', {
        name: file.name,
        content: await base64(file),
        assets
      });
      selected = result.id;
      current = null;
    }

    if (selected) await select(selected);
    $('uploads').value = '';
    $('assets').value = '';
    notify('Documentos añadidos. La extracción se procesará en la cola.');
  });
});

// Drag and drop onto the upload area: the dropped files go through the same form as a chosen file.
{
  const zone = $('upload-form');
  const over = (on) => zone.classList.toggle('is-over', on);
  zone.addEventListener('dragover', (event) => { event.preventDefault(); over(true); });
  zone.addEventListener('dragleave', () => over(false));
  zone.addEventListener('drop', (event) => {
    event.preventDefault();
    over(false);
    if (!event.dataTransfer?.files?.length) return;
    $('uploads').files = event.dataTransfer.files;
    zone.requestSubmit();
  });
}

$('pause').onclick = () => guard(() => action('settings', { paused: !state.paused }));
$('save-settings').onclick = () =>
  guard(() =>
    action('settings', {
      mode: $('mode').value,
      night_start: Number($('night-start').value),
      night_end: Number($('night-end').value)
    })
  );

$('refresh').onclick = () =>
  guard(async () => {
    dirty = false;
    await select(selected);
  });

$('resume').onclick = () => guard(() => action('resume', { key: selected }));
$('original').onclick = () => guard(() => download(current.intake_path + '/' + current.intake.original));
$('extraction').oninput = $('spanish').oninput = () => {
  dirty = true;
};

$('save-extraction').onclick = () =>
  guard(async () => {
    await action('edit_extraction', {
      key: selected,
      text: $('extraction').value,
      revision: current.intake.revision
    });
    dirty = false;
    await select(selected);
    notify('Correcciones guardadas. Revisa la versión antes de aprobarla.');
  });

$('approve-extraction').onclick = () =>
  guard(async () => {
    if (dirty) throw new Error('Guarda primero las correcciones.');
    await action('accept_extraction', {
      key: selected,
      revision: current.intake.revision,
      note: $('extraction-note').value,
      complete: $('complete').checked
    });
    await select(selected);
  });

$('save-spanish').onclick = () =>
  guard(async () => {
    await action('edit_spanish', {
      key: selected,
      text: $('spanish').value,
      revision: current.spanish_revision
    });
    dirty = false;
    await select(selected);
  });

$('review-spanish').onclick = () =>
  guard(async () => {
    if (dirty) throw new Error('Guarda primero los cambios.');
    await action('review_spanish', { key: selected });
    await select(selected);
  });

$('translate').onclick = () =>
  guard(async () => {
    if (dirty) throw new Error('Guarda y revisa los cambios antes de aprobar.');
    await action('translate', {
      key: selected,
      revision: current.result.revision_sha256,
      note: $('spanish-note').value,
      resolved: $('resolved').checked,
      acknowledge: $('acknowledge').checked
    });
    await select(selected);
  });

// Tabs of the Spanish review: click, and the arrow keys move between them.
for (const tab of document.querySelectorAll('[data-tab]')) {
  tab.addEventListener('click', () => showTab(tab.dataset.tab));
  tab.addEventListener('keydown', (event) => {
    const tabs = [...document.querySelectorAll('[data-tab]')];
    const at = tabs.indexOf(tab);
    const next = event.key === 'ArrowRight' ? tabs[(at + 1) % tabs.length] : event.key === 'ArrowLeft' ? tabs[(at - 1 + tabs.length) % tabs.length] : null;
    if (!next) return;
    event.preventDefault();
    showTab(next.dataset.tab);
    next.focus();
  });
}

// Landing actions and the reset button (no inline handlers: the local CSP forbids them).
const scrollTo = (node) => node.scrollIntoView({ behavior: reducedMotion ? 'auto' : 'smooth', block: 'start' });

$('cta-sample').onclick = () =>
  guard(async () => {
    const first = Object.keys(state?.documents || {})[0];
    if (first) await select(first);
    scrollTo($('workbench'));
  });

$('cta-upload').onclick = () => {
  scrollTo($('workbench'));
  $('uploads').focus({ preventScroll: true });
};

$('reset-demo').onclick = () => {
  mockWorkbench.reset();
  location.reload();
};

mountShowcase($('showcase'), { reducedMotion });

// Arranque inicial
guard(async () => {
  updateEnvBadge();
  await refreshState();
  if (state) {
    $('mode').value = state.mode;
    $('night-start').value = state.night_start;
    $('night-end').value = state.night_end;
  }
  // El panel de cola es útil de entrada en el trabajo local; en la demo se queda plegado.
  $('queue-settings').open = !useMock;
  // En modo demo, autoseleccionar el primer documento para una experiencia instantánea
  if (useMock && Object.keys(state.documents || {}).length > 0) {
    const firstKey = Object.keys(state.documents)[0];
    await select(firstKey);
  }
});

updateEnvBadge();

setInterval(() => refreshState().catch((error) => notify(error.message)), 3000);

// API mínima en ventana para pruebas y control
window.NainWrite = {
  resetDemo: () => {
    mockWorkbench.reset();
    location.reload();
  },
  select
};
