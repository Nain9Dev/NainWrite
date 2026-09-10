"""Review-only evidence for exact human edits and original-grounded crosschecks."""

from dataclasses import asdict

from .document import literal_issues, protected_literals, sha
from .document_editorial import editorial_issues
from .document_ambiguity import contextual_issues
from .document_prompts import build_prompt
from .language_tool import partition_proofreading_issues
from .models import LanguageIssue
from .prompts import AUDIT_SCHEMA
from .service import AuditValidationError, audit_issues, parse_audit


def _findings(evidence, items, candidate, locale, config):
    issues = [f"{source['id']}:{issue}" for source, target in zip(items, candidate)
              for issue in literal_issues(source["text"], target["text"])]
    issues.extend(f"{target['id']}:{issue}" for target in candidate
                  for issue in editorial_issues(target['text'], locale))
    issues.extend(f"{source['id']}:{issue}" for source, target in zip(items, candidate)
                  for issue in contextual_issues(source['text'], target['text'], locale))
    proof = evidence["proofreading"]
    allowed = {"es", "es-ES"} if locale == "es-ES" else {locale}
    if proof["language"] not in allowed or proof["software_name"] != "LanguageTool":
        raise ValueError("Saved proofreading identity mismatch")
    proof_issues = [LanguageIssue(**value) for value in proof["issues"]]
    for finding in proof_issues:
        if (not finding.rule_id or not finding.issue_type or type(finding.offset) is not int
                or type(finding.length) is not int or finding.offset < 0 or finding.length < 0):
            raise ValueError("Invalid saved proofreading finding")
    text = "\n\n".join(v["text"] for v in candidate)
    blocking, advisory, ignored = partition_proofreading_issues(text, proof_issues, protected_literals(text))
    for key, expected in (("blocking", blocking), ("advisory", advisory), ("ignored_technical_spelling", ignored)):
        if evidence[key] != [asdict(value) for value in expected]:
            raise ValueError("Saved proofreading classification mismatch")
    issues.extend(f"language_tool:{i.rule_id}:{i.message}" for i in blocking)
    if len(evidence["audits"]) != 2:
        raise ValueError("Both audit records are required")
    for saved, model in zip(evidence["audits"], (config["writer"], config["auditor"])):
        generation = saved["generation"]
        if generation["model_digest"] != config["models"][model] or generation["model"] != model:
            raise ValueError("Saved review model identity mismatch")
        try:
            audit = parse_audit(generation["content"])
            if saved["audit"] != asdict(audit):
                raise ValueError("Saved parsed audit contradicts original audit response")
            issues.extend(audit_issues(audit, config["semantic_threshold"],
                                       config["minimum_style_score"], prefix=f"{model}:"))
        except AuditValidationError as error:
            if saved["audit"] is not None or saved["validation_error"] != error.code:
                raise ValueError("Invalid audit was not retained as a rejection")
            issues.append(f"{model}:invalid_audit:{error.code}")
    return issues


def review(transformer, items, replacements, locale, context):
    if locale not in ("es-ES", "en-GB", "en-US") or locale not in transformer.proofreaders:
        raise ValueError("A language-appropriate proofreader is required")
    if (not items or len({i['id'] for i in items}) != len(items)
            or set(replacements) != {i['id'] for i in items}
            or any(not isinstance(v, str) or not v.strip() for v in replacements.values())):
        raise ValueError("Review requires exact nonempty source and replacement coverage")
    candidate = [{"id": i["id"], "text": replacements[i["id"]]} for i in items]
    if sum(len(v["text"].encode("utf-8")) for v in candidate) > 4800:
        raise ValueError("Review candidate exceeds the bounded audit budget")
    prompt = build_prompt("audit", locale, items, context, candidate)
    text = "\n\n".join(v["text"] for v in candidate)
    proofreading = transformer.proofreaders[locale].check(text)
    allowed = {"es", "es-ES"} if locale == "es-ES" else {locale}
    if proofreading.language not in allowed:
        raise ValueError("Proofreader locale does not match the review")
    blocking, advisory, ignored = partition_proofreading_issues(
        text, proofreading.issues, protected_literals(text))
    audits = []
    for model in (transformer.model, transformer.audit_model):
        generation = transformer._generate(model, prompt, AUDIT_SCHEMA)
        saved = {"generation": asdict(generation), "prompt_sha256": sha(prompt)}
        try:
            saved["audit"] = asdict(parse_audit(generation.content))
        except AuditValidationError as error:
            saved.update(audit=None, validation_error=error.code)
        audits.append(saved)
    result = {"evidence_type": "review-only-v1", "locale": locale,
              "replacements": dict(replacements), "proofreading": asdict(proofreading),
              "blocking": [asdict(i) for i in blocking], "advisory": [asdict(i) for i in advisory],
              "ignored_technical_spelling": [asdict(i) for i in ignored], "audits": audits,
              "input_hashes": {i['id']: sha(i['text']) for i in items},
              "output_hashes": {key: sha(value) for key, value in replacements.items()}}
    issues = _findings(result, items, candidate, locale, transformer.config)
    result.update(issues=issues, status="review_required" if issues else "accepted")
    validate_review(result, items, locale, transformer.config, context)
    return result


def validate_review(result, items, locale, config, context):
    """Recompute all derivable review facts without inventing a writer generation."""
    try:
        if (result["evidence_type"] != "review-only-v1" or result["locale"] != locale
                or "generation" in result or "attempts" in result):
            raise ValueError("Review-only evidence identity mismatch")
        expected = {i['id']: sha(i['text']) for i in items}
        if result['input_hashes'] != expected or set(result['replacements']) != set(expected):
            raise ValueError("Saved review source or coverage mismatch")
        if any(not isinstance(v, str) or not v.strip() for v in result['replacements'].values()):
            raise ValueError("Invalid review replacement")
        if result['output_hashes'] != {key: sha(value) for key, value in result['replacements'].items()}:
            raise ValueError("Saved review candidate hash mismatch")
        candidate = [{"id": i["id"], "text": result["replacements"][i["id"]]} for i in items]
        if sum(len(v["text"].encode("utf-8")) for v in candidate) > 4800:
            raise ValueError("Saved review exceeds the bounded audit budget")
        expected_prompt = sha(build_prompt("audit", locale, items, context, candidate))
        if any(audit["prompt_sha256"] != expected_prompt for audit in result["audits"]):
            raise ValueError("Saved audit prompt identity mismatch")
        issues = _findings(result, items, candidate, locale, config)
        if result["issues"] != issues or result["status"] != ("review_required" if issues else "accepted"):
            raise ValueError("Saved review status contradicts evidence")
    except (KeyError, TypeError, IndexError, AttributeError) as error:
        raise ValueError("Incomplete saved review evidence") from error
