"""Run the local Spanish-first bilingual document workflow."""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from spanish_rewriter.document_job import run_job, start_job
from spanish_rewriter.document_transform import DocumentTransformer
from spanish_rewriter.ollama_client import OllamaClient


def main(argv=None):
    parser = argparse.ArgumentParser(description="Reescribe un archivo UTF-8 .md/.txt en es-ES y después en en-GB, sin modificar el original.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--input", type=Path)
    group.add_argument("--resume", type=Path)
    parser.add_argument("--both", action="store_true", help="Genera ambos idiomas (comportamiento predeterminado).")
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--clean-notes", action="store_true", help="Omite marcadores editoriales VERIFY/DAVID y registra los rangos.")
    parser.add_argument("--omit-lines", action="append", default=[], metavar="FIRST:LAST", help="Omite un rango explícito de preparación; no permite borrar encabezados numerados.")
    args = parser.parse_args(argv)
    if args.resume and (args.clean_notes or args.omit_lines or args.output_dir):
        parser.error("La reanudación utiliza las opciones guardadas; no admite cambiar la limpieza o el destino.")
    job = args.resume
    try:
        ranges = [tuple(map(int, value.split(":"))) for value in args.omit_lines]
        if any(len(pair) != 2 for pair in ranges):
            raise ValueError("Use FIRST:LAST for each omitted range")
        transformer = DocumentTransformer(OllamaClient())
        for locale, proofreader in transformer.proofreaders.items():
            proofreader.check("Texto de comprobación." if locale == "es-ES" else "Proofreading check.")
        if job is None:
            job = start_job(args.input, transformer, output_dir=args.output_dir,
                            clean_notes=args.clean_notes, omit_lines=ranges)
        print(f"Trabajo: {job}", flush=True)
        print(f'Reanudar: python tools/rewrite_document.py --resume "{job}"', flush=True)
        result = run_job(job, transformer, progress=lambda language, number, total:
                         print(f"{language}: bloque {number}/{total}", flush=True))
        print(f"Generación completa. Estado: {result['automatic_status']}. Aprobación humana pendiente.", flush=True)
        for locale, name in result["files"].items():
            print(f"{locale}: {job / name}")
        print(f"Informe: {job / 'review.md'}")
        return 0 if result["automatic_status"] == "accepted" else 2
    except (OSError, ValueError, RuntimeError) as error:
        print(f"Trabajo incompleto o no válido: {error}", file=sys.stderr)
        if job:
            print(f'Conserva el progreso. Reanudar: python tools/rewrite_document.py --resume "{job}"', file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
