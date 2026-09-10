"""Render a conservative Markdown subset to a local PDF and portable asset bundle."""

import io
from pathlib import Path
import re
from xml.sax.saxutils import escape
import zipfile

from .intake import IMAGE
from . import intake_store as store


def render_pdf(text, assets_root):
    import reportlab
    from reportlab.lib import colors
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image

    font_dir = Path(reportlab.__file__).parent / 'fonts'
    for name, file in [('NWBody', 'Vera.ttf'), ('NWBold', 'VeraBd.ttf'), ('NWMono', 'Vera.ttf')]:
        if name not in pdfmetrics.getRegisteredFontNames():
            pdfmetrics.registerFont(TTFont(name, str(font_dir / file)))
    font = pdfmetrics.getFont('NWBody')
    missing = {char for char in text if not char.isspace() and ord(char) not in font.face.charToGlyph}
    if missing:
        raise ValueError('PDF font lacks characters: ' + ', '.join(f'U+{ord(c):04X}' for c in sorted(missing)))
    body = ParagraphStyle('Body', fontName='NWBody', fontSize=10.5, leading=15,
                          spaceAfter=8, textColor=colors.HexColor('#172b3a'), splitLongWords=True)
    styles = {level: ParagraphStyle(f'H{level}', parent=body, fontName='NWBold',
                                   fontSize=20 if level == 1 else 15 if level == 2 else 12,
                                   leading=25 if level == 1 else 20 if level == 2 else 17,
                                   spaceBefore=10, spaceAfter=9, keepWithNext=True)
              for level in range(1, 7)}
    small = ParagraphStyle('Cell', parent=body, fontSize=9, leading=12, spaceAfter=2)
    code_style = ParagraphStyle('Code', parent=body, fontName='NWMono', fontSize=9,
                                leading=12, backColor=colors.HexColor('#f0f3f6'))

    def inline(value):
        value = escape(value)
        value = re.sub(r'\[([^\]]+)\]\((https?://[^\s)]+)\)',
                       lambda m: m[1] + ' (' + m[2] + ')', value)
        value = re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', value)
        value = re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)', r'<i>\1</i>', value)
        return value.replace('`', '')

    pdfmetrics.registerFontFamily('NWBody', normal='NWBody', bold='NWBold', italic='NWBody', boldItalic='NWBold')
    flow, lines, index = [], text.splitlines(), 0
    while index < len(lines):
        line = lines[index]
        index += 1
        if not line.strip():
            continue
        if line.startswith('```'):
            code = []
            while index < len(lines) and not lines[index].startswith('```'):
                code.append(lines[index]); index += 1
            if index >= len(lines):
                raise ValueError('Unclosed code fence')
            index += 1
            flow.append(Paragraph('<br/>'.join(escape(part) for part in code), code_style))
            continue
        image_match = IMAGE.fullmatch(line.strip())
        if image_match:
            raw = store.read_bytes(assets_root, image_match[2])
            item = Image(io.BytesIO(raw))
            scale = min(1, 507 / item.imageWidth, 430 / item.imageHeight)
            item.drawWidth, item.drawHeight = item.imageWidth * scale, item.imageHeight * scale
            flow.extend([item, Spacer(1, 8)])
            continue
        if IMAGE.search(line):
            raise ValueError('Place each image on its own line before PDF export')
        if line.strip().startswith('|'):
            rows = [line]
            while index < len(lines) and lines[index].strip().startswith('|'):
                rows.append(lines[index]); index += 1
            cells = []
            for row in rows:
                parts = re.split(r'(?<!\\)\|', row.strip().strip('|'))
                if all(re.fullmatch(r'\s*:?-+:?\s*', part) for part in parts):
                    continue
                cells.append([Paragraph(inline(part.replace('\\|', '|').strip()), small) for part in parts])
            count = max(map(len, cells))
            if any(len(row) != count for row in cells):
                raise ValueError('Table columns differ; correct extraction before export')
            table = Table(cells, colWidths=[507 / count] * count, repeatRows=1, hAlign='LEFT')
            table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e7eef2')),
                                       ('GRID', (0, 0), (-1, -1), .4, colors.HexColor('#b2c2cb')),
                                       ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                                       ('LEFTPADDING', (0, 0), (-1, -1), 7),
                                       ('RIGHTPADDING', (0, 0), (-1, -1), 7),
                                       ('TOPPADDING', (0, 0), (-1, -1), 7),
                                       ('BOTTOMPADDING', (0, 0), (-1, -1), 7)]))
            flow.extend([table, Spacer(1, 10)])
            continue
        heading = re.match(r'^(#{1,6})\s+(.*)', line)
        if heading:
            flow.append(Paragraph(inline(heading[2]), styles[len(heading[1])]))
        elif re.fullmatch(r'\s*([-*_])(?:\s*\1){2,}\s*', line):
            flow.append(Spacer(1, 10))
        else:
            flow.append(Paragraph(inline(line), body))
    if not flow:
        raise ValueError('No printable content')
    result = io.BytesIO()
    document = SimpleDocTemplate(result, pagesize=(595, 842), leftMargin=44, rightMargin=44,
                                 topMargin=44, bottomMargin=48, title='Documento revisado',
                                 author='', pageCompression=1)
    def footer(canvas, doc):
        canvas.saveState(); canvas.setFont('NWBody', 8)
        canvas.setFillColor(colors.HexColor('#607482'))
        canvas.drawRightString(551, 25, str(doc.page))
        canvas.restoreState()
    document.build(flow, onFirstPage=footer, onLaterPages=footer)
    return result.getvalue()


def portable_markdown(text, assets_root, locale):
    output = io.BytesIO()
    with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(f'{locale}.md', text.encode('utf-8'))
        for name in dict.fromkeys(match[2] for match in IMAGE.finditer(text)):
            archive.writestr(name, store.read_bytes(assets_root, name))
    return output.getvalue()
