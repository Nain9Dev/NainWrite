"""Produce an offline per-auditor comparison from validated immutable evidence."""

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from spanish_rewriter.document_store import canonical, publish
from spanish_rewriter.independent_evaluation import load_comparison


def main():
    parser = argparse.ArgumentParser(description='Compara auditores sin volver a llamar a los modelos.')
    parser.add_argument('--job', type=Path, required=True)
    parser.add_argument('--bank', type=Path, required=True)
    args = parser.parse_args()
    result = load_comparison(args.job, args.bank)
    publish(args.job, 'auditor-comparison.json', canonical(result))
    print(canonical(result))


if __name__ == '__main__':
    main()
