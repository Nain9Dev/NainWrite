"""Prepare and explicitly approve local document extraction before rewriting."""

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from spanish_rewriter.intake import import_document, intake_status, approve_extraction, approved_source
from spanish_rewriter.pdf_intake import LocalOCR


def main():
    parser = argparse.ArgumentParser(description='Extrae documentos localmente para su revisión.')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--input', type=Path)
    group.add_argument('--review', type=Path)
    parser.add_argument('--output-dir', type=Path, default=ROOT / 'private' / 'intakes')
    parser.add_argument('--approve', metavar='SHA256')
    parser.add_argument('--note')
    parser.add_argument('--confirm-complete', action='store_true')
    parser.add_argument('--tesseract', type=Path, default=ROOT / '.tools/tesseract/tesseract.exe')
    parser.add_argument('--tessdata', type=Path, default=ROOT / '.tools/tesseract/tessdata')
    args = parser.parse_args()
    if args.approve and not args.review:
        parser.error('--approve requiere --review')
    try:
        folder = args.review
        if args.input:
            ocr = LocalOCR(args.tesseract, args.tessdata) if args.tesseract.exists() else None
            folder = import_document(args.input, args.output_dir, ocr=ocr)
        if args.approve:
            approve_extraction(folder, args.approve, args.note, complete=args.confirm_complete)
        status = intake_status(folder)
        print(f"Carpeta: {folder}\nRevisión: {status['revision']}\nPáginas: {len(status['pages'])}")
        print(f"Editable: {folder / 'extraction.md'}\nAprobada: {status['approved']}")
        if status['approved']:
            print(f'Entrada revisada para reescribir: {approved_source(folder)}')
            return 0
        print('Compara la extracción con el original y las páginas; corrige dudas antes de aprobar.')
        return 3
    except (OSError, ValueError, RuntimeError) as error:
        print(f'Extracción incompleta: {error}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
