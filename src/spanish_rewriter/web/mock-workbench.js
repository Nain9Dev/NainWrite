/**
 * In-browser deterministic mock workbench for static demo execution.
 * Faithful to the local Python workbench specification (spec-011):
 * - Strict editorial gates: extraction_review -> spanish_review -> final_review -> ready.
 * - Semantic invariant preservation: numbers, dates, currency, negations, and protected terms.
 * - LocalStorage persistence with reset capability.
 */

const STORAGE_KEY = "nainwrite.demo_db";

const DEFAULT_DOCUMENTS = {
  "doc-001": {
    id: "doc-001",
    name: "Propuesta_SaaS_Enterprise.md",
    status: "spanish_review",
    progress: "Borrador reescrito en es-ES. Pendiente de tu revisión contra el original.",
    error: null,
    intake_path: "intakes/doc-001",
    actions: {
      resume: false,
      edit_extraction: false,
      edit_spanish: true,
      review_spanish: true,
      translate: true
    },
    intake: {
      original: "Propuesta_SaaS_Enterprise.md",
      revision: "rev-intake-001-a1b2",
      pages: [
        { number: 1, method: "text", extraction_error: null, preview: "preview_p1.svg" },
        { number: 2, method: "text", extraction_error: null, preview: "preview_p2.svg" }
      ],
      text: `# Propuesta de Servicios Tecnológicos (Enterprise)

Fecha de emisión: 15 de octubre de 2026.
Importe acordado: 14.500,00 € (catorce mil quinientos euros), IVA no incluido.

1. Alcance y entregables
La solución contempla la integración de la API sobre arquitectura limpia y la entrega del panel de control en un plazo máximo de 60 días naturales.
No incluye alojamiento dedicado en nube privada salvo contratación expresa por escrito.

2. Condiciones críticas
- El cliente debe proveer las credenciales de prueba antes del día 5 de cada ciclo.
- Bajo ningún concepto se desplegará en producción sin la aprobación expresa de las pruebas de regresión.
- Si la tasa de disponibilidad desciende del 99,95% mensual, se aplicará una penalización del 5% del importe recurrente.

3. Garantía y soporte
Soporte técnico preferente en horario laboral (9:00 a 18:00 CET). La garantía cubre defectos de software durante 12 meses a partir de la firma.`
    },
    result: {
      revision_sha256: "9a8b7c6d5e4f3a2b1c0d9e8f7a6b5c4d3e2f1a0b9c8d7e6f5a4b3c2d1e0f9a8b",
      invariants_checked: 6,
      invariants_preserved: 6
    },
    spanish: `# Propuesta de Servicios Tecnológicos (Enterprise)

Fecha de emisión: 15 de octubre de 2026.
Importe acordado: 14.500,00 € (catorce mil quinientos euros), IVA no incluido.

1. Alcance y entregables
La solución contempla la integración de la API sobre Clean Architecture y la entrega del panel de control en un plazo máximo de 60 días naturales.
No incluye alojamiento dedicado en nube privada salvo contratación expresa por escrito.

2. Condiciones críticas
- El cliente debe proporcionar las credenciales de prueba antes del día 5 de cada ciclo.
- Bajo ningún concepto se desplegará en producción sin la aprobación expresa de las pruebas de regresión.
- Si la tasa de disponibilidad desciende del 99,95 % mensual, se aplicará una penalización del 5 % del importe recurrente.

3. Garantía y soporte
Soporte técnico preferente en horario laboral (9:00 a 18:00 CET). La garantía cubre los defectos de software durante 12 meses a partir de la firma.`,
    spanish_revision: "rev-es-001-f8e7",
    diff: `--- Original (Borrador)
+++ es-ES (Revisión NainWrite)
@@ -7,2 +7,2 @@
-La solución contempla la integración de la API sobre arquitectura limpia y la entrega del panel de control en un plazo máximo de 60 días naturales.
+La solución contempla la integración de la API sobre Clean Architecture y la entrega del panel de control en un plazo máximo de 60 días naturales.
@@ -11,2 +11,2 @@
-El cliente debe proveer las credenciales de prueba antes del día 5 de cada ciclo.
+El cliente debe proporcionar las credenciales de prueba antes del día 5 de cada ciclo.
@@ -13,2 +13,2 @@
-Si la tasa de disponibilidad desciende del 99,95% mensual, se aplicará una penalización del 5% del importe recurrente.
+Si la tasa de disponibilidad desciende del 99,95 % mensual, se aplicará una penalización del 5 % del importe recurrente.
@@ -17,2 +17,2 @@
-La garantía cubre defectos de software durante 12 meses a partir de la firma.
+La garantía cubre los defectos de software durante 12 meses a partir de la firma.`,
    review: `INVARIANTES SEMÁNTICOS (Verificación determinista):
- Cifras exactas: [14.500,00, 60, 5, 99,95, 12] -> 100 % preservadas.
- Monedas: [€] -> 100 % preservadas.
- Fechas y plazos: [15 de octubre de 2026, 60 días naturales, 12 meses] -> 100 % preservadas.
- Negaciones y límites: ["No incluye", "Bajo ningún concepto", "sin la aprobación"] -> Preservados íntegramente.
- Términos protegidos: ["Clean Architecture", "API", "IVA", "CET"] -> Respetados.

AUDITORÍA LINGÜÍSTICA (es-ES):
- Calco corregido: "proveer" -> "proporcionar".
- Espaciado ortotipográfico de porcentaje: "99,95%" -> "99,95 %" (según norma RAE).
- Naturalidad de artículo determinado: "cubre defectos" -> "cubre los defectos".
- Estado del evaluador: ACEPTADO (Sin discrepancias de significado).`,
    exports: {
      "es-ES": {
        pdf: "exports/doc-001-es.pdf",
        markdown: "exports/doc-001-es.md",
        bundle: "exports/doc-001-es.zip",
        text: `# Propuesta de Servicios Tecnológicos (Enterprise)\n\nFecha de emisión: 15 de octubre de 2026.\nImporte acordado: 14.500,00 € (catorce mil quinientos euros), IVA no incluido.\n\n1. Alcance y entregables\nLa solución contempla la integración de la API sobre Clean Architecture y la entrega del panel de control en un plazo máximo de 60 días naturales.\nNo incluye alojamiento dedicado en nube privada salvo contratación expresa por escrito.\n\n2. Condiciones críticas\n- El cliente debe proporcionar las credenciales de prueba antes del día 5 de cada ciclo.\n- Bajo ningún concepto se desplegará en producción sin la aprobación expresa de las pruebas de regresión.\n- Si la tasa de disponibilidad desciende del 99,95 % mensual, se aplicará una penalización del 5 % del importe recurrente.\n\n3. Garantía y soporte\nSoporte técnico preferente en horario laboral (9:00 a 18:00 CET). La garantía cubre los defectos de software durante 12 meses a partir de la firma.`,
        text_sha256: "9a8b7c6d5e4f3a2b1c0d9e8f7a6b5c4d3e2f1a0b9c8d7e6f5a4b3c2d1e0f9a8b"
      }
    },
    final_approvals: {}
  },

  "doc-002": {
    id: "doc-002",
    name: "Contrato_Marco_Cloud.md",
    status: "final_review",
    progress: "Traducciones generadas. Pendiente de aprobación final de cada variante.",
    error: null,
    intake_path: "intakes/doc-002",
    actions: {
      resume: false,
      edit_extraction: false,
      edit_spanish: false,
      review_spanish: false,
      translate: false
    },
    intake: {
      original: "Contrato_Marco_Cloud.md",
      revision: "rev-intake-002",
      pages: [{ number: 1, method: "text", extraction_error: null, preview: "preview_p1.svg" }],
      text: "Acuerdo marco de computación en la nube y protección de datos confidenciales."
    },
    result: {
      revision_sha256: "2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c",
      invariants_checked: 4,
      invariants_preserved: 4
    },
    spanish: `# Acuerdo Marco de Servicios Cloud

1. Confidencialidad y seguridad
Ambas partes se comprometen a salvaguardar los datos confidenciales con medidas técnicas y organizativas adecuadas.
Ninguna parte divulgará información propietaria a terceros sin consentimiento previo por escrito.

2. Nivel de servicio y compensación
El proveedor garantiza una disponibilidad del 99,9 % del servicio de infraestructura.
En caso de interrupción imputable al proveedor superior a 2 horas ininterrumpidas, se emitirá un abono compensatorio del 10 % de la cuota mensual.`,
    spanish_revision: "rev-es-002",
    diff: "Versión en español aprobada sin objeciones.",
    review: "Invariantes verificados: 0 discrepancias.",
    exports: {
      "es-ES": {
        pdf: "exports/doc-002-es.pdf",
        markdown: "exports/doc-002-es.md",
        bundle: "exports/doc-002-es.zip",
        text: `# Acuerdo Marco de Servicios Cloud\n\n1. Confidencialidad y seguridad\nAmbas partes se comprometen a salvaguardar los datos confidenciales con medidas técnicas y organizativas adecuadas.\nNinguna parte divulgará información propietaria a terceros sin consentimiento previo por escrito.\n\n2. Nivel de servicio y compensación\nEl proveedor garantiza una disponibilidad del 99,9 % del servicio de infraestructura.\nEn caso de interrupción imputable al proveedor superior a 2 horas ininterrumpidas, se emitirá un abono compensatorio del 10 % de la cuota mensual.`,
        text_sha256: "es-sha-002"
      },
      "en-US": {
        pdf: "exports/doc-002-en-us.pdf",
        markdown: "exports/doc-002-en-us.md",
        bundle: "exports/doc-002-en-us.zip",
        text: `# Cloud Services Master Agreement\n\n1. Confidentiality and Security\nBoth parties agree to protect confidential data through appropriate organizational and technical measures.\nNeither party shall disclose proprietary information to third parties without prior written consent.\n\n2. Service Level and Remedy\nThe service provider guarantees 99.9% availability for the infrastructure service.\nIn the event of an unscheduled interruption attributable to the provider exceeding 2 consecutive hours, a service credit equal to 10% of the monthly fee shall be issued.`,
        text_sha256: "us-sha-002"
      },
      "en-GB": {
        pdf: "exports/doc-002-en-gb.pdf",
        markdown: "exports/doc-002-en-gb.md",
        bundle: "exports/doc-002-en-gb.zip",
        text: `# Cloud Services Master Agreement\n\n1. Confidentiality and Security\nBoth parties undertake to safeguard confidential data through suitable technical and organisational measures.\nNeither party shall disclose proprietary information to third parties without prior written consent.\n\n2. Service Level and Compensation\nThe provider warrants 99.9% uptime across the infrastructure service.\nIn the event of an outage attributable to the provider exceeding 2 consecutive hours, a compensatory credit of 10% of the monthly charge will be granted.`,
        text_sha256: "gb-sha-002"
      }
    },
    final_approvals: {}
  },

  "doc-003": {
    id: "doc-003",
    name: "Nota_Tecnica_Extraccion.txt",
    status: "extraction_review",
    progress: "Extracción completada. Comprueba cifras y tablas antes de redactar.",
    error: null,
    intake_path: "intakes/doc-003",
    actions: {
      resume: false,
      edit_extraction: true,
      edit_spanish: false,
      review_spanish: false,
      translate: false
    },
    intake: {
      original: "Nota_Tecnica_Extraccion.txt",
      revision: "rev-intake-003",
      pages: [{ number: 1, method: "text", extraction_error: null, preview: "preview_p1.svg" }],
      text: `Nota técnica sobre el motor de reescritura determinista.
El sistema procesa texto en español peninsular y analiza 5 clases de invariantes:
1. Fechas y plazos temporales.
2. Magnitudes numéricas y porcentajes.
3. Importes monetarios y símbolos de divisas.
4. Polaridad y alcance de negaciones lógicas.
5. Vocabulario técnico protegido.`
    },
    result: null,
    spanish: "",
    spanish_revision: null,
    diff: "",
    review: "",
    exports: {},
    final_approvals: {}
  }
};

class MockWorkbench {
  constructor() {
    this.mode = "limited";
    this.night_start = 22;
    this.night_end = 7;
    this.paused = false;
    this.documents = {};
    this.load();
  }

  load() {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved) {
        const parsed = JSON.parse(saved);
        this.mode = parsed.mode || "limited";
        this.night_start = parsed.night_start ?? 22;
        this.night_end = parsed.night_end ?? 7;
        this.paused = Boolean(parsed.paused);
        this.documents = parsed.documents || {};
        return;
      }
    } catch {
      /* Fallback si el almacenamiento local está deshabilitado */
    }
    this.reset();
  }

  save() {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify({
        mode: this.mode,
        night_start: this.night_start,
        night_end: this.night_end,
        paused: this.paused,
        documents: this.documents
      }));
    } catch {
      /* Ignorar error de cuota */
    }
  }

  reset() {
    this.mode = "limited";
    this.night_start = 22;
    this.night_end = 7;
    this.paused = false;
    this.documents = JSON.parse(JSON.stringify(DEFAULT_DOCUMENTS));
    this.save();
  }

  summary() {
    const docs = {};
    for (const [id, doc] of Object.entries(this.documents)) {
      docs[id] = {
        id: doc.id,
        name: doc.name,
        status: doc.status,
        progress: doc.progress
      };
    }
    return {
      paused: this.paused,
      mode: this.mode,
      night_start: this.night_start,
      night_end: this.night_end,
      documents: docs
    };
  }

  detail(id) {
    const doc = this.documents[id];
    if (!doc) throw new Error(`Documento con id "${id}" no encontrado.`);
    return JSON.parse(JSON.stringify(doc));
  }

  upload(name, contentBase64) {
    let text = "";
    try {
      text = atob(contentBase64);
    } catch {
      text = `# ${name}\n\nDocumento cargado correctamente.\nContenido de muestra para revisión determinista.`;
    }

    const id = "doc-" + Math.random().toString(36).substring(2, 8);
    const newDoc = {
      id,
      name,
      status: "extraction_review",
      progress: "Extracción completada. Comprueba cifras y tablas antes de redactar.",
      error: null,
      intake_path: `intakes/${id}`,
      actions: {
        resume: false,
        edit_extraction: true,
        edit_spanish: false,
        review_spanish: false,
        translate: false
      },
      intake: {
        original: name,
        revision: "rev-" + Math.random().toString(36).substring(2, 6),
        pages: [{ number: 1, method: "text", extraction_error: null, preview: "preview_p1.svg" }],
        text
      },
      result: null,
      spanish: "",
      spanish_revision: null,
      diff: "",
      review: "",
      exports: {},
      final_approvals: {}
    };

    this.documents[id] = newDoc;
    this.save();
    return id;
  }

  edit_extraction(key, text) {
    const doc = this.documents[key];
    if (!doc || !doc.intake) throw new Error("Documento no encontrado o sin extracción.");
    doc.intake.text = text;
    doc.intake.revision = "rev-" + Math.random().toString(36).substring(2, 6);
    this.save();
  }

  accept_extraction(key, revision, note, complete) {
    const doc = this.documents[key];
    if (!doc) throw new Error("Documento no encontrado.");
    if (!complete) throw new Error("Debes marcar la casilla confirmando que has comprobado el contenido.");

    // Simulación determinista de reescritura conservadora en es-ES
    const rawText = doc.intake.text;
    const rewritten = this.applyConservativeSpanishRules(rawText);

    doc.status = "spanish_review";
    doc.progress = "Borrador reescrito en es-ES. Pendiente de tu revisión contra el original.";
    doc.spanish = rewritten;
    doc.spanish_revision = "rev-es-" + Math.random().toString(36).substring(2, 6);
    doc.actions.edit_extraction = false;
    doc.actions.edit_spanish = true;
    doc.actions.review_spanish = true;
    doc.actions.translate = true;

    doc.result = {
      revision_sha256: "hash-" + Math.random().toString(36).substring(2, 10),
      invariants_checked: 5,
      invariants_preserved: 5
    };

    doc.diff = this.generateUnifiedDiff(rawText, rewritten);
    doc.review = `VERIFICACIÓN DETERMINISTA:
- Invariantes de números y fechas: Preservados.
- Negaciones y límites: Preservados.
- Calcos y fórmulas redundantes: Corregidos al estándar profesional de España.
- Nota de extracción registrada: "${note || "Comprobado"}".`;

    doc.exports = {
      "es-ES": {
        pdf: `exports/${key}-es.pdf`,
        markdown: `exports/${key}-es.md`,
        bundle: `exports/${key}-es.zip`,
        text: rewritten,
        text_sha256: "sha-es-" + Math.random().toString(36).substring(2, 8)
      }
    };

    this.save();
  }

  edit_spanish(key, text) {
    const doc = this.documents[key];
    if (!doc) throw new Error("Documento no encontrado.");
    doc.spanish = text;
    doc.spanish_revision = "rev-es-" + Math.random().toString(36).substring(2, 6);
    doc.status = "spanish_edited";
    doc.progress = "Español editado. Requiere nueva revisión antes de traducir.";
    this.save();
  }

  review_spanish(key) {
    const doc = this.documents[key];
    if (!doc) throw new Error("Documento no encontrado.");
    doc.status = "spanish_review";
    doc.progress = "Revisión completada. Puedes proceder con la aprobación y traducción.";
    doc.diff = this.generateUnifiedDiff(doc.intake.text, doc.spanish);
    doc.review = "VERIFICACIÓN TRAS EDICIÓN:\n- Invariantes semánticos: Verificados con éxito.\n- Sin alteraciones de cifras ni fechas.";
    this.save();
  }

  translate(key, revision, note, resolved, acknowledge) {
    const doc = this.documents[key];
    if (!doc) throw new Error("Documento no encontrado.");
    if (!resolved) throw new Error("Debes confirmar que has resuelto todas las dudas de significado.");

    const esText = doc.spanish;
    const enUS = this.simulateTranslation(esText, "en-US");
    const enGB = this.simulateTranslation(esText, "en-GB");

    doc.status = "final_review";
    doc.progress = "Traducciones generadas. Pendiente de aprobación final de cada variante.";
    doc.actions.edit_spanish = false;
    doc.actions.translate = false;

    doc.exports = {
      "es-ES": {
        pdf: `exports/${key}-es.pdf`,
        markdown: `exports/${key}-es.md`,
        bundle: `exports/${key}-es.zip`,
        text: esText,
        text_sha256: "sha-es-" + key
      },
      "en-US": {
        pdf: `exports/${key}-en-us.pdf`,
        markdown: `exports/${key}-en-us.md`,
        bundle: `exports/${key}-en-us.zip`,
        text: enUS,
        text_sha256: "sha-us-" + key
      },
      "en-GB": {
        pdf: `exports/${key}-en-gb.pdf`,
        markdown: `exports/${key}-en-gb.md`,
        bundle: `exports/${key}-en-gb.zip`,
        text: enGB,
        text_sha256: "sha-gb-" + key
      }
    };
    doc.final_approvals = {};
    this.save();
  }

  approve_final(key, locale, revision, note) {
    const doc = this.documents[key];
    if (!doc) throw new Error("Documento no encontrado.");
    if (!doc.exports[locale]) throw new Error(`Variante ${locale} no disponible.`);

    doc.final_approvals[locale] = {
      approved_at: new Date().toISOString(),
      note: note || "Aprobado en revisión final",
      revision
    };

    const allApproved = ["es-ES", "en-US", "en-GB"].every((l) => Boolean(doc.final_approvals[l]));
    if (allApproved) {
      doc.status = "ready";
      doc.progress = "Listo: tres versiones aprobadas con revisión humana registrada.";
    }

    this.save();
  }

  settings(opts) {
    if (opts.mode) this.mode = opts.mode;
    if (opts.night_start !== undefined) this.night_start = opts.night_start;
    if (opts.night_end !== undefined) this.night_end = opts.night_end;
    if (opts.paused !== undefined) this.paused = Boolean(opts.paused);
    this.save();
  }

  resume(key) {
    const doc = this.documents[key];
    if (doc && doc.status === "paused") {
      doc.status = doc.intake ? "spanish_review" : "extraction_review";
      this.save();
    }
  }

  applyConservativeSpanishRules(text) {
    return text
      .replaceAll("performar", "rendir")
      .replaceAll("hacer sentido", "tener sentido")
      .replaceAll("customizar", "personalizar")
      .replaceAll("arquitectura limpia", "Clean Architecture")
      .replaceAll("proveer", "proporcionar")
      .replaceAll("soportar", "admitir");
  }

  generateUnifiedDiff(orig, mod) {
    if (orig === mod) return "Sin diferencias respecto al original.";
    return `--- Original\n+++ es-ES (Revisión NainWrite)\n@@ -1,4 +1,4 @@\n- ${orig.substring(0, 80)}…\n+ ${mod.substring(0, 80)}…\n(Calcos corregidos y estilo profesional aplicado sin alterar significado).`;
  }

  simulateTranslation(esText, locale) {
    if (locale === "en-US") {
      return esText
        .replaceAll("Propuesta de Servicios Tecnológicos", "Technology Services Proposal")
        .replaceAll("Acuerdo Marco de Servicios Cloud", "Cloud Services Master Agreement")
        .replaceAll("Confidencialidad y seguridad", "Confidentiality and Security")
        .replaceAll("Garantía y soporte", "Warranty and Support")
        .replaceAll("condiciones", "terms")
        .replaceAll("personalizar", "customize")
        .replaceAll("organización", "organization");
    }
    // en-GB
    return esText
      .replaceAll("Propuesta de Servicios Tecnológicos", "Technology Services Proposal")
      .replaceAll("Acuerdo Marco de Servicios Cloud", "Cloud Services Master Agreement")
      .replaceAll("Confidencialidad y seguridad", "Confidentiality and Security")
      .replaceAll("Garantía y soporte", "Warranty and Support")
      .replaceAll("condiciones", "terms")
      .replaceAll("personalizar", "customise")
      .replaceAll("organización", "organisation");
  }

  generateBlob(path) {
    const content = `# NainWrite Artifact: ${path}\n\nDocumento generado y validado con preservación de significado.`;
    return new Blob([content], { type: "text/markdown;charset=utf-8" });
  }
}

export const mockWorkbench = new MockWorkbench();

export async function mockDispatch(path, body) {
  // Simulación de latencia realista (15-35 ms)
  await new Promise((r) => setTimeout(r, 15 + Math.random() * 20));

  const url = new URL(path, "http://localhost");
  const pathname = url.pathname;
  const searchParams = url.searchParams;

  if (pathname === "/api/state") {
    return mockWorkbench.summary();
  }

  if (pathname === "/api/document") {
    const id = searchParams.get("id");
    return mockWorkbench.detail(id);
  }

  if (pathname === "/api/action") {
    const { action, ...data } = body || {};
    if (action === "upload") {
      const id = mockWorkbench.upload(data.name, data.content);
      return { id };
    }
    if (typeof mockWorkbench[action] === "function") {
      mockWorkbench[action](...Object.values(data));
      return { ok: true };
    }
    throw new Error(`Acción desconocida: ${action}`);
  }

  throw new Error(`Ruta ${pathname} no implementada en el mock.`);
}
