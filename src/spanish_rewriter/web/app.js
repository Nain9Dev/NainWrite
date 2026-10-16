'use strict';

import { mockDispatch, mockWorkbench } from "./mock-workbench.js";

const $ = (id) => document.getElementById(id);
const token = document.querySelector('meta[name="nainwrite-token"]')?.content || 'demo-token';

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

function notify(text) {
  const node = $('notice');
  if (node) node.textContent = text;
}

function updateEnvBadge() {
  const badge = document.querySelector('.local');
  if (!badge) return;
  if (useMock) {
    badge.textContent = 'Demo interactiva (Navegador)';
    badge.setAttribute('title', 'Ejecución en cliente sobre motor de dominio simulado');
    badge.classList.add('local--demo');
  } else {
    badge.textContent = 'Trabajo local';
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

    b.append(name, status);
    nav.append(b);
  }

  if (selected && state.documents[selected]) {
    $('progress').textContent = state.documents[selected].progress;
    $('stage').textContent = labels[state.documents[selected].status] || state.documents[selected].status;
    if (current && !dirty && current.status !== state.documents[selected].status) {
      await select(selected);
    }
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
  $('resume').hidden = !current.actions.resume;
  $('original').hidden = !current.intake;
  $('extraction-section').hidden = !current.intake;
  $('spanish-section').hidden = !current.result;
  $('exports-section').hidden = !Object.keys(current.exports || {}).length;

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
        })
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

// Arranque inicial
guard(async () => {
  updateEnvBadge();
  await refreshState();
  if (state) {
    $('mode').value = state.mode;
    $('night-start').value = state.night_start;
    $('night-end').value = state.night_end;
  }
  // En modo demo, autoseleccionar el primer documento para una experiencia instantánea
  if (useMock && Object.keys(state.documents || {}).length > 0) {
    const firstKey = Object.keys(state.documents)[0];
    await select(firstKey);
  }
});

setInterval(() => refreshState().catch((error) => notify(error.message)), 3000);

// API mínima en ventana para pruebas y control
window.NainWrite = {
  resetDemo: () => {
    mockWorkbench.reset();
    location.reload();
  },
  select
};
