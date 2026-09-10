"""Revalidate saved bilingual evidence before reusing a completed batch."""

from dataclasses import asdict

from .document import literal_issues, protected_literals
from .document_editorial import editorial_issues
from .document_ambiguity import contextual_issues
from .language_tool import partition_proofreading_issues
from .models import LanguageIssue
from .service import AuditValidationError, audit_issues, parse_audit


def validate_transformation(result, items, locale, config, *, upstream_review=False):
    """Reject corrupt or inconsistent evidence; checksums are not authentication."""
    try:
        _validate(result, items, locale, config, upstream_review)
    except (KeyError, TypeError, IndexError, AttributeError) as error:
        raise ValueError("Incomplete checkpoint evidence contract") from error


def _validate(result, items, locale, config, upstream_review):
    if result["locale"] != locale or not 1 <= len(result["attempts"]) <= 2:
        raise ValueError("Checkpoint locale or repair limit mismatch")
    uncertain = False
    expected_ids = [i["id"] for i in items]

    def identity(generation, model):
        if generation["model_digest"] != config["models"][model] or generation["model"] != model:
            raise ValueError("Checkpoint model evidence does not match the configured model")

    for attempt in result["attempts"]:
        generation = attempt["generation"]
        identity(generation, config["writer"])
        content = generation["content"]
        if type(content["uncertain"]) is not bool:
            raise ValueError("Invalid saved writer uncertainty")
        uncertain |= content["uncertain"]
        values = content["items"]
        if [v["id"] for v in values] != expected_ids or any(not v["text"].strip() for v in values):
            raise ValueError("Saved generation has incomplete or reordered IDs")
        candidate = [{"id": v["id"], "text": v["text"].strip()} for v in values]
        issues = [f"{source['id']}:{issue}" for source, target in zip(items, candidate)
                  for issue in literal_issues(source["text"], target["text"])]
        issues.extend(f"{target['id']}:{issue}" for target in candidate
                      for issue in editorial_issues(target['text'], locale))
        issues.extend(f"{source['id']}:{issue}" for source, target in zip(items, candidate)
                      for issue in contextual_issues(source['text'], target['text'], locale))
        proof = attempt["proofreading"]
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
            if attempt[key] != [asdict(value) for value in expected]:
                raise ValueError("Saved proofreading classification mismatch")
        issues.extend(f"language_tool:{i.rule_id}:{i.message}" for i in blocking)
        if len(attempt["audits"]) != 2:
            raise ValueError("Both audit records are required")
        for saved, model in zip(attempt["audits"], (config["writer"], config["auditor"])):
            identity(saved["generation"], model)
            try:
                audit = parse_audit(saved["generation"]["content"])
                if saved["audit"] != asdict(audit):
                    raise ValueError("Saved parsed audit contradicts original audit response")
                issues.extend(audit_issues(audit, config["semantic_threshold"],
                                           config["minimum_style_score"], prefix=f"{model}:"))
            except AuditValidationError as error:
                if saved["audit"] is not None or saved["validation_error"] != error.code:
                    raise ValueError("Invalid audit was not retained as a rejection")
                issues.append(f"{model}:invalid_audit:{error.code}")
        if uncertain:
            issues.append("writer_reported_uncertainty")
        if attempt["issues"] != issues:
            raise ValueError("Saved batch findings contradict their evidence")
    if result["replacements"] != {v["id"]: v["text"] for v in candidate}:
        raise ValueError("Saved replacements do not match the final generation")
    if upstream_review:
        issues = issues + ["upstream_spanish_review_required"]
    if result["issues"] != issues or result["status"] != ("review_required" if issues else "accepted"):
        raise ValueError("Saved batch quality status contradicts evidence or upstream status")
