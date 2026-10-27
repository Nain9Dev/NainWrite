"""Automated architectural fitness functions for NainWrite.

Enforces layer isolation and dependency direction rules:
1. Core invariants and models must not depend on HTTP presentation or CLI interfaces.
2. Domain evaluation and service orchestration must not depend on CLI modules.
3. All source modules in spanish_rewriter must maintain clean AST syntax trees.
"""

from __future__ import annotations

import ast
from pathlib import Path


def _get_imported_modules(py_path: Path) -> list[str]:
    with open(py_path, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename=str(py_path))

    modules: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                modules.append(alias.name)
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.append(node.module)
    return modules


def test_core_invariants_and_models_have_no_http_or_cli_dependencies():
    """Verify core domain contracts have zero presentation, HTTP, or CLI dependencies."""
    pkg_dir = Path(__file__).resolve().parent.parent / "src" / "spanish_rewriter"
    core_files = ["invariants.py", "models.py", "calibration.py"]
    forbidden = ("cli", "workbench_http", "local_http", "fastapi", "flask", "aiohttp", "urllib", "requests")

    for fname in core_files:
        py_file = pkg_dir / fname
        assert py_file.exists(), f"Expected core module {fname} not found"
        imported = _get_imported_modules(py_file)
        for imp in imported:
            for bad in forbidden:
                assert not (imp == bad or imp.endswith(f".{bad}")), (
                    f"Core domain module {fname} violates architecture by importing '{imp}'"
                )


def test_evaluator_and_service_do_not_depend_on_cli():
    """Verify services and evaluators never import CLI or argument parsing layers."""
    pkg_dir = Path(__file__).resolve().parent.parent / "src" / "spanish_rewriter"
    service_files = ["evaluator.py", "service.py", "editorial_job.py", "document_transform.py"]
    forbidden = ("cli", "argparse")

    for fname in service_files:
        py_file = pkg_dir / fname
        if not py_file.exists():
            continue
        imported = _get_imported_modules(py_file)
        for imp in imported:
            for bad in forbidden:
                assert not (imp == bad or imp.endswith(f".{bad}")), (
                    f"Service module {fname} violates architecture by importing '{imp}'"
                )


def test_all_source_modules_are_valid_python_syntax():
    """Ensure all package files compile into clean abstract syntax trees."""
    pkg_dir = Path(__file__).resolve().parent.parent / "src" / "spanish_rewriter"
    for py_file in pkg_dir.glob("*.py"):
        with open(py_file, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=str(py_file))
        assert tree is not None, f"Failed to parse AST for {py_file.name}"
