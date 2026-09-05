"""Run a finite synthetic corporate evaluation through existing local services."""

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from spanish_rewriter.calibration import run_experiment
from spanish_rewriter.document_transform import DocumentTransformer
from spanish_rewriter.ollama_client import OllamaClient


def main():
    parser = argparse.ArgumentParser(description='Evalúa controles sintéticos con los modelos locales.')
    parser.add_argument('--bank', type=Path, default=ROOT / 'benchmark/corporate_calibration_controls.json')
    parser.add_argument('--output-dir', type=Path, default=ROOT / 'artifacts/corporate-calibration.rewritten')
    parser.add_argument('--resume', type=Path)
    args = parser.parse_args()
    try:
        worker = DocumentTransformer(OllamaClient())
        for proofreader in worker.proofreaders.values():
            proofreader.check('Texto de prueba.' if proofreader.language == 'es' else 'Test text.')
        job, result = run_experiment(args.bank, worker, output_dir=args.output_dir,
                                    resume=args.resume, progress=lambda message: print(message, flush=True))
        print(json.dumps(result['summary']), flush=True)
        print(f"Informe: {job / 'results.json'}", flush=True)
        return 0 if result['quality_gate_passed'] else 2
    except (OSError, ValueError, RuntimeError) as error:
        print(f'Evaluación incompleta: {error}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
