"""Command-line interface for one local Spanish rewrite."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .ollama_client import OllamaClient, OllamaError
from .service import DEFAULT_MODEL, SpanishRewriteService


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Rewrite text into professional Spanish from Spain using local Ollama."
    )
    source = parser.add_mutually_exclusive_group()
    source.add_argument("--text", help="Source text. Reads stdin when omitted.")
    source.add_argument("--file", type=Path, help="UTF-8 source file.")
    parser.add_argument("--protected", action="append", default=[])
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--ollama-url", default="http://127.0.0.1:11434")
    parser.add_argument(
        "--plain",
        action="store_true",
        help="Print only accepted rewritten text; rejected results remain JSON.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.file:
        source_text = args.file.read_text(encoding="utf-8")
    elif args.text is not None:
        source_text = args.text
    else:
        source_text = sys.stdin.read()
    if not source_text.strip():
        print("Source text must not be empty.", file=sys.stderr)
        return 2

    try:
        service = SpanishRewriteService(
            client=OllamaClient(base_url=args.ollama_url),
            model=args.model,
        )
        result = service.rewrite(source_text, protected_literals=args.protected)
    except (OllamaError, ValueError, OSError) as error:
        print(json.dumps({"status": "error", "error": str(error)}, ensure_ascii=False))
        return 3

    if args.plain and result.status == "accepted":
        print(result.rewritten_text)
    else:
        print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
    return 0 if result.status == "accepted" else 2


if __name__ == "__main__":
    raise SystemExit(main())
