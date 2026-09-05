"""Run the local revision-approved trilingual document workflow."""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from spanish_rewriter.editorial_job import run_job, start_job
from spanish_rewriter.document_transform import DocumentTransformer
from spanish_rewriter.ollama_client import OllamaClient


def main(argv=None):
    parser = argparse.ArgumentParser(description="Prepara es-ES y espera aprobación de su revisión antes de traducir a en-GB y en-US.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--input", type=Path)
    group.add_argument("--resume", type=Path)
    parser.add_argument("--both", action="store_true", help="Compatibilidad: no omite la aprobación obligatoria del español.")
    parser.add_argument("--approve-spanish", metavar="SHA256", help="Autoriza traducir la revisión española ya revisada; solo con --resume.")
    parser.add_argument("--acknowledge-review", action="store_true", help="Reconoce los hallazgos pendientes, sin cambiar su estado automático.")
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--clean-notes", action="store_true", help="Omite marcadores editoriales VERIFY/DAVID y registra los rangos.")
    parser.add_argument("--omit-lines", action="append", default=[], metavar="FIRST:LAST", help="Omite un rango explícito de preparación; no permite borrar encabezados numerados.")
    args = parser.parse_args(argv)
    if args.approve_spanish and not args.resume:
        parser.error("--approve-spanish solo se admite con --resume.")
    if args.acknowledge_review and not args.approve_spanish:
        parser.error("--acknowledge-review requiere --approve-spanish.")
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
                         print(f"{language}: bloque {number}/{total}", flush=True),
                         approve_spanish=args.approve_spanish, acknowledge_review=args.acknowledge_review)
        print(f"Fase: {result['phase']}. Estado automático: {result['automatic_status']}.", flush=True)
        print(f"Revisión española SHA-256: {result['revision_sha256']}", flush=True)
        print(f"Español editable: {job / result['editable_file']}", flush=True)
        for locale, name in result["files"].items():
            print(f"{locale}: {job / name}")
        print(f"Informe: {job / result['review_file']}")
        if result.get('outdated_revisions'):
            print("Aviso: las traducciones de revisiones anteriores están desactualizadas: "
                  + ", ".join(result['outdated_revisions']))
        if result['phase'] == 'awaiting_spanish_approval':
            print("Pausa: revisa el español y el informe. Después autoriza su SHA con --resume y --approve-spanish.")
            print("Si editas el archivo, reanuda primero sin aprobación para revisar la nueva versión.")
            return 3
        print("Generación completa; la autorización de traducción no es aprobación final de publicación.")
        return 0 if result["automatic_status"] == "accepted" else 2
    except (OSError, ValueError, RuntimeError) as error:
        print(f"Trabajo incompleto o no válido: {error}", file=sys.stderr)
        if job:
            print(f'Conserva el progreso. Reanudar: python tools/rewrite_document.py --resume "{job}"', file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
