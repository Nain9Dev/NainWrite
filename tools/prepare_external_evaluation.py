"""Decode one pinned PAWS-X snapshot offline; never download or execute dataset code."""

import argparse
import hashlib
import io
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from spanish_rewriter.document_store import canonical, digest, publish
from spanish_rewriter.independent_evaluation import PAWS_REVISION, PAWS_SHA256, PAWS_URL, select_pawsx, blind_review


def main():
    parser = argparse.ArgumentParser(description='Prepara una muestra semántica externa y una reserva.')
    parser.add_argument('--parquet', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    if not args.parquet.is_file() or args.parquet.stat().st_size > 2_000_000:
        raise ValueError('Expected the bounded pinned corpus file')
    raw = args.parquet.read_bytes()
    if hashlib.sha256(raw).hexdigest() != PAWS_SHA256:
        raise ValueError('Corpus snapshot hash does not match the frozen protocol')
    # This isolated optional reader is not imported by the rewriting runtime.
    sys.path.insert(0, str(ROOT / '.tools/benchmark-deps'))
    import pyarrow.parquet as pq
    table = pq.read_table(io.BytesIO(raw), columns=['id', 'sentence1', 'sentence2', 'label'])
    if table.num_rows != 2000:
        raise ValueError('Unexpected pinned snapshot row count')
    evaluation, reserve, stats = select_pawsx(table.to_pylist())
    for bank in (evaluation, reserve):
        bank['provenance'].update(source_url=PAWS_URL, revision=PAWS_REVISION,
                                  snapshot_sha256=PAWS_SHA256,
                                  licence_url='https://github.com/google-research-datasets/paws/blob/master/LICENSE',
                                  paper_url='https://aclanthology.org/D19-1382/',
                                  selection_statistics=stats)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for name, bank in (('evaluation.json', evaluation), ('reserve.json', reserve)):
        publish(args.output_dir, name, canonical(bank))
    manifest = dict(protocol='independent-pawsx-v1', evaluation_sha256=digest(evaluation),
                    reserve_sha256=digest(reserve), sample_size=40, reserve_size=40,
                    statistics=stats, provenance=evaluation['provenance'])
    publish(args.output_dir, 'manifest.json', canonical(manifest))
    publish(args.output_dir, 'independent-review.md', blind_review(evaluation))
    print(canonical(manifest))


if __name__ == '__main__':
    main()
