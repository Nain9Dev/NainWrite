"""Run the local NainWrite browser application and one resumable queue worker."""

import argparse
from pathlib import Path
import sys
import threading

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from spanish_rewriter.document_store import job_lock
from spanish_rewriter.pdf_intake import LocalOCR
from spanish_rewriter.workbench import Workbench
from spanish_rewriter.workbench_http import create_server


def main():
    parser = argparse.ArgumentParser(description='NainWrite: revisión local de documentos.')
    parser.add_argument('--data-dir', type=Path, default=ROOT / 'private/workbench')
    parser.add_argument('--port', type=int, default=8765)
    args = parser.parse_args()
    # Dependency check is explicit; serving the application never installs or downloads.
    import pdfplumber, pypdfium2, reportlab, PIL
    args.data_dir.mkdir(parents=True, exist_ok=True)
    with job_lock(args.data_dir):
        ocr = LocalOCR(ROOT / '.tools/tesseract/tesseract.exe', ROOT / '.tools/tesseract/tessdata')
        app = Workbench(args.data_dir, ocr=ocr)
        server = create_server(app, port=args.port)
        thread = threading.Thread(target=app.run, daemon=True)
        thread.start()
        print(f'NainWrite disponible en http://127.0.0.1:{server.server_port}', flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            app.stop.set()
            server.server_close()
            thread.join(timeout=5)


if __name__ == '__main__':
    main()
