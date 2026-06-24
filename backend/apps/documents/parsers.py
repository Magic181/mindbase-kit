from pathlib import Path

from docx import Document as DocxDocument
from pypdf import PdfReader


class ParseError(Exception):
    pass


def parse_file(file_path: Path, file_type: str) -> str:
    parsers = {
        'txt': _parse_text,
        'md': _parse_text,
        'pdf': _parse_pdf,
        'docx': _parse_docx,
    }
    parser = parsers.get(file_type)
    if not parser:
        raise ParseError(f'不支持的文件类型: .{file_type}')
    return parser(file_path)


def _parse_text(file_path: Path) -> str:
    for encoding in ('utf-8', 'utf-8-sig', 'gbk'):
        try:
            return file_path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
    raise ParseError('无法识别文本编码')


def _parse_pdf(file_path: Path) -> str:
    reader = PdfReader(str(file_path))
    pages = []
    for index, page in enumerate(reader.pages, start=1):
        text = (page.extract_text() or '').strip()
        if text:
            pages.append(f'[第{index}页]\n{text}')
    if not pages:
        raise ParseError('PDF 中未提取到文本内容')
    return '\n\n'.join(pages)


def _parse_docx(file_path: Path) -> str:
    doc = DocxDocument(str(file_path))
    paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
    if not paragraphs:
        raise ParseError('DOCX 中未提取到文本内容')
    return '\n\n'.join(paragraphs)
