"""Exercise real local OCR and mixed PDF evidence using public synthetic text."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from spanish_rewriter.intake import import_document, intake_status
from spanish_rewriter.pdf_intake import LocalOCR


def main():
    from PIL import Image, ImageDraw, ImageFont
    from reportlab.pdfgen.canvas import Canvas
    from reportlab.lib.utils import ImageReader
    output = ROOT / 'artifacts/document-intake-smoke'
    output.mkdir(parents=True, exist_ok=True)
    source = output / 'mixed-source.pdf'
    if source.exists():
        raise ValueError('Preserve prior evidence; choose a new smoke folder')
    canvas = Canvas(str(source), pagesize=(595, 842))
    canvas.setTitle('Synthetic intake verification')
    canvas.setFont('Helvetica-Bold', 20)
    canvas.drawString(48, 790, 'Propuesta de servicios')
    canvas.setFont('Helvetica', 12)
    canvas.drawString(48, 753, 'La entrega no esta garantizada sin aprobacion previa.')
    for x in (48, 250, 540):
        canvas.line(x, 640, x, 720)
    for y in (640, 680, 720):
        canvas.line(48, y, 540, y)
    for x, y, text in [(60, 695, 'Servicio'), (270, 695, 'Importe'),
                       (60, 655, 'Revision'), (270, 655, '125 EUR')]:
        canvas.drawString(x, y, text)
    figure = Image.new('RGB', (600, 180), '#e8eef4')
    draw = ImageDraw.Draw(figure)
    draw.rectangle((30, 30, 250, 140), fill='#274b65')
    draw.rectangle((350, 30, 570, 140), fill='#48786a')
    canvas.drawImage(ImageReader(figure), 48, 460, 492, 148)
    canvas.drawString(48, 440, 'Figura 1. Fases del servicio.')
    canvas.drawString(48, 400, 'Referencia: https://example.org/specification')
    canvas.linkURL('https://example.org/specification', (48, 395, 420, 415))
    canvas.showPage()
    canvas.setFont('Helvetica-Bold', 18)
    canvas.drawString(48, 790, 'Condiciones y alcance')
    canvas.setFont('Helvetica', 12)
    for y, left, right in [(745, 'Primera columna: propuesta.', 'Segunda columna: restricciones.'),
                            (720, 'No incluye alojamiento.', 'Requiere revision del cliente.')]:
        canvas.drawString(48, y, left)
        canvas.drawString(310, y, right)
    canvas.setFont('Helvetica', 9)
    canvas.drawString(48, 70, '1. La fecha depende de la aprobacion expresa.')
    canvas.showPage()
    scan = Image.new('RGB', (1600, 900), 'white')
    font_path = Path('C:/Windows/Fonts/arial.ttf')
    font = ImageFont.truetype(str(font_path), 42)
    draw = ImageDraw.Draw(scan)
    for index, line in enumerate(['Documento escaneado de prueba.',
                                  'No se garantiza la entrega el 15 de octubre.',
                                  'El importe es 125 EUR y requiere aprobacion.',
                                  'The proposed delivery remains conditional.']):
        draw.text((60, 90 + index * 120), line, font=font, fill='black')
    canvas.drawImage(ImageReader(scan), 30, 260, 535, 301)
    canvas.save()
    ocr = LocalOCR(ROOT / '.tools/tesseract/tesseract.exe', ROOT / '.tools/tesseract/tessdata')
    folder = import_document(source, output / 'intakes', ocr=ocr)
    status = intake_status(folder)
    assert len(status['pages']) == 3 and not status['approved']
    assert status['pages'][0]['tables'] == 1
    assert status['pages'][0]['images'] == 1
    assert status['pages'][2]['method'] == 'ocr'
    assert '125' in status['pages'][2]['text'] and 'No se garantiza' in status['pages'][2]['text']
    print(f'PASS: 3 pages, native table/image/link, columns/footnote retained for review, real bilingual OCR.\n{folder}')


if __name__ == '__main__':
    main()
