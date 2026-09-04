"""Resumable Spanish-first document orchestration, without presentation or transport."""

from pathlib import Path

from .document import BATCH_BYTES, MAX_ITEMS, literal_issues, make_batches, parse_document, sha
from .document_evidence import validate_transformation
from .document_store import canonical, digest, job_lock, new_job_dir, publish, read_input, read_state, save_state

JOB_VERSION = "bilingual-job-v2"
LOCALES = ("es-ES", "en-GB")


def start_job(input_path, transformer, *, output_dir=None, clean_notes=False, omit_lines=()):
    source, text, source_hash = read_input(input_path)
    options = {"markdown": source.suffix.lower() == ".md", "clean_notes": clean_notes,
               "omit_lines": list(omit_lines)}
    manifest = parse_document(text, **options)
    if not manifest.editable:
        raise ValueError("No editable prose remains after parsing and cleanup")
    config = {"transformer": transformer.config, "parser": options,
              "batch_bytes": BATCH_BYTES, "max_items": MAX_ITEMS, "job_version": JOB_VERSION}
    job = new_job_dir(source, output_dir)
    state = {"source_path": str(source), "source_sha256": source_hash,
             "manifest": manifest.to_dict(), "config": config, "configuration_sha256": digest(config),
             "phase": "es-ES", "generation_complete": False, "human_approved": False,
             "results": {locale: [] for locale in LOCALES}}
    save_state(job, state)
    return job


def _values(results):
    values = {}
    for result in results:
        if set(values) & set(result["replacements"]):
            raise ValueError("Duplicate completed block in checkpoint")
        values.update(result["replacements"])
    return values


def _items(batch, spanish=None):
    return [{"id": p.id, "text": spanish[p.id] if spanish is not None else p.text, "role": p.role}
            for p in batch]


def _validate_results(state, batches):
    spanish = _values(state["results"]["es-ES"])
    for locale in LOCALES:
        results = state["results"][locale]
        if not isinstance(results, list) or len(results) > len(batches):
            raise ValueError("Invalid completed batch count")
        if locale == "en-GB" and results and len(state["results"]["es-ES"]) != len(batches):
            raise ValueError("English cannot precede the complete Spanish candidate")
        for index, (result, batch) in enumerate(zip(results, batches)):
            items = _items(batch, spanish if locale == "en-GB" else None)
            expected = {i["id"]: sha(i["text"]) for i in items}
            if result["input_hashes"] != expected or set(result["replacements"]) != set(expected):
                raise ValueError("Checkpoint batch identity or source hashes mismatch")
            if any(not isinstance(v, str) or not v.strip() for v in result["replacements"].values()):
                raise ValueError("Invalid checkpoint replacement")
            if result["output_hashes"] != {k: sha(v) for k, v in result["replacements"].items()}:
                raise ValueError("Checkpoint candidate hash mismatch")
            if result["status"] not in {"accepted", "review_required"} or not result["attempts"]:
                raise ValueError("Checkpoint quality evidence missing")
            if result["status"] == "accepted" and result["issues"]:
                raise ValueError("Checkpoint accepted status contradicts findings")
            validate_transformation(result, items, locale, state["config"]["transformer"],
                                    upstream_review=locale == "en-GB" and
                                    state["results"]["es-ES"][index]["status"] != "accepted")
        _values(results)


def _context(manifest, batch, spanish=None):
    editable = manifest.editable
    first = next(i for i, p in enumerate(editable) if p.id == batch[0].id)
    last = first + len(batch) - 1
    context = {}
    # Include whole neighbours only; do not silently truncate their text.
    for label, index in (("previous", first - 1), ("next", last + 1)):
        if 0 <= index < len(editable):
            piece = editable[index]
            value = spanish[piece.id] if spanish is not None else piece.text
            if len(value.encode("utf-8")) <= 256:
                context[label] = value
    return context


def _global_checks(manifest, replacements, locale):
    issues = [f"{p.id}:{issue}" for p in manifest.editable
              for issue in literal_issues(p.text, replacements[p.id])]
    # Terminology is reviewed in bounded batches. Global detection is deliberately lexical.
    text = "\n".join(replacements.values()).lower()
    terminology = []
    for variants in (("conformidad", "conformancia"), ("activo", "asset")) if locale == "es-ES" else ():
        if all(v in text for v in variants):
            terminology.append("possible_terminology_inconsistency:" + "/".join(variants))
    headings = {}
    for piece in manifest.editable:
        if piece.role == "heading":
            headings.setdefault(piece.text, []).append(piece.id)
    for ids in headings.values():
        if len({replacements[block] for block in ids}) > 1:
            terminology.append("inconsistent_heading:" + ",".join(ids))
    return {"retained_editable_blocks": len(manifest.editable), "covered_blocks": len(replacements),
            "coverage_complete": set(replacements) == {p.id for p in manifest.editable},
            "structural_integrity": not any("inline_structure" in issue for issue in issues),
            "literal_findings": issues, "terminology_findings": terminology,
            "semantic_coverage": "Every bounded batch audited by two models; no exhaustive cross-section semantic proof."}


def _finish(job, state, manifest):
    files, checks = {}, {}
    status = "accepted"
    stem = Path(state["source_path"]).stem
    suffix = Path(state["source_path"]).suffix.lower()
    for locale in LOCALES:
        values = _values(state["results"][locale])
        output = manifest.assemble(values)
        checks[locale] = _global_checks(manifest, values, locale)
        failed = (any(r["status"] != "accepted" for r in state["results"][locale])
                  or checks[locale]["literal_findings"] or checks[locale]["terminology_findings"])
        if failed or status == "review_required":
            status = "review_required"
        label = "review-required" if status == "review_required" else "candidate"
        files[locale] = f"{stem}.{locale}.{label}{suffix}"
        publish(job, files[locale], output)
    summary = {"generation_complete": True, "automatic_status": status, "human_approved": False,
               "source_unchanged": True, "files": files, "checks": checks,
               "cleanup_ranges": manifest.removals,
               "model_configuration": state["config"]["transformer"],
               "limitations": ["Automated acceptance is not human approval or a guarantee of equivalence.",
                               "Claims, disclosure accuracy and empty fields were not fact-checked.",
                               "The existing Ollama server configuration was not changed or certified isolated."]}
    publish(job, "review.json", canonical(dict(summary, results=state["results"])))
    lines = ["# Revisión del documento", "", f"Generación completa: sí. Estado automático: {status}.",
             "Aprobación humana: pendiente. El original no se ha modificado.", "",
             "Se ha generado primero es-ES y después en-GB a partir del español.", "",
             "## Resultados por bloque", ""]
    for locale in LOCALES:
        lines += [f"### {locale}", ""]
        for index, result in enumerate(state["results"][locale], 1):
            lines.append(f"- Bloque {index}: {result['status']}. " + "; ".join(result["issues"]))
        lines += ["", f"Cobertura: {checks[locale]['covered_blocks']}/{checks[locale]['retained_editable_blocks']} fragmentos.",
                  "Hallazgos globales: " + ("; ".join(checks[locale]['literal_findings'] + checks[locale]['terminology_findings']) or "ninguno en las comprobaciones implementadas") + ".",
                  "Comprobación semántica limitada a bloques y contexto adyacente; no es una prueba exhaustiva del documento.", ""]
    lines += ["## Límites", "", "Las comprobaciones no acreditan la veracidad de las afirmaciones, la vigencia de los datos ni la exactitud de las declaraciones de autoría. Los campos vacíos siguen pendientes.",
              "", f"Rangos de preparación eliminados: {len(manifest.removals)}. El detalle y la evidencia completa están en review.json.", ""]
    publish(job, "review.md", "\n".join(lines))
    return summary


def run_job(job_dir, transformer, *, progress=None):
    job = Path(job_dir).resolve(strict=True)
    with job_lock(job):
        state = read_state(job)
        source, text, source_hash = read_input(state["source_path"])
        if source_hash != state["source_sha256"]:
            raise ValueError("Original document changed; start a new job")
        config = state["config"]
        if (config["transformer"] != transformer.config or digest(config) != state["configuration_sha256"]
                or config["job_version"] != JOB_VERSION or config["batch_bytes"] != BATCH_BYTES
                or config["max_items"] != MAX_ITEMS):
            raise ValueError("Job configuration, prompts or model identities changed")
        manifest = parse_document(text, **config["parser"])
        if manifest.to_dict() != state["manifest"]:
            raise ValueError("Manifest identity changed")
        batches = make_batches(manifest)
        _validate_results(state, batches)
        try:
            for locale in LOCALES:
                state["phase"] = locale
                save_state(job, state)
                spanish = _values(state["results"]["es-ES"]) if locale == "en-GB" else None
                if spanish is not None:
                    manifest.assemble(spanish)
                for index in range(len(state["results"][locale]), len(batches)):
                    if progress:
                        progress(locale, index + 1, len(batches))
                    batch = batches[index]
                    result = transformer.transform(_items(batch, spanish), locale, _context(manifest, batch, spanish))
                    if locale == "en-GB" and state["results"]["es-ES"][index]["status"] != "accepted":
                        result["issues"].append("upstream_spanish_review_required")
                        result["status"] = "review_required"
                    state["results"][locale].append(result)
                    _validate_results(state, batches)
                    save_state(job, state)
                save_state(job, state)
            if read_input(source)[2] != source_hash:
                raise ValueError("Original document changed during processing")
            summary = _finish(job, state, manifest)
            state.update(phase="complete", generation_complete=True, summary=summary)
            state.pop("last_error", None)
            save_state(job, state)
            return summary
        except Exception as error:
            state["generation_complete"] = False
            state["last_error"] = f"{type(error).__name__}: {error}"
            save_state(job, state)
            raise
