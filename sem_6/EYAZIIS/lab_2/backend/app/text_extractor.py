"""Извлечение текста из TXT/RTF/PDF/DOC/DOCX для backend API.

Логику повторяем с desktop-версии ЛР, чтобы в web-версии был тот же функционал загрузки файлов.
"""

import re
from pathlib import Path

try:
    from docx import Document as DocxDocument
except Exception:
    DocxDocument = None

try:
    from pypdf import PdfReader
except Exception:
    PdfReader = None

try:
    from striprtf.striprtf import rtf_to_text
except Exception:
    rtf_to_text = None


def extract_text_from_doc(filepath: str) -> str:
    """Упрощённое извлечение для .doc (как в исходном lab_1:text_processor)."""
    path = Path(filepath)
    try:
        raw = path.read_bytes()
        # Оставляем только printable ASCII/whitespace и переводим в utf-8.
        text = re.sub(rb"[^\x20-\x7E\n\r\t]", b" ", raw).decode("utf-8", errors="replace")
        text = re.sub(r"\s+", " ", text).strip()
        return text if len(text) > 50 else ""
    except Exception:
        return ""


def extract_text_from_file(filepath: str) -> str:
    path = Path(filepath)
    suffix = path.suffix.lower()

    if suffix == ".txt":
        # Пытаемся распознать кодировки, чтобы файл не ломался на UTF-8.
        try:
            for enc in ("utf-8", "cp1252", "latin-1"):
                try:
                    return path.read_text(encoding=enc)
                except UnicodeDecodeError:
                    continue
            return path.read_bytes().decode("utf-8", errors="replace")
        except Exception:
            return ""

    if suffix == ".rtf" and rtf_to_text is not None:
        try:
            raw = path.read_bytes()
            rtf_str = raw.decode("utf-8", errors="replace")
            return rtf_to_text(rtf_str, encoding="utf-8", errors="ignore") or ""
        except Exception:
            return ""

    if suffix == ".pdf" and PdfReader is not None:
        try:
            reader = PdfReader(str(filepath))
            parts: list[str] = []
            for page in reader.pages:
                t = page.extract_text()
                if t:
                    parts.append(t)
            return "\n".join(parts) if parts else ""
        except Exception:
            return ""

    if suffix == ".docx" and DocxDocument is not None:
        try:
            doc = DocxDocument(str(filepath))
            return "\n".join(p.text for p in doc.paragraphs)
        except Exception:
            return ""

    if suffix == ".doc":
        return extract_text_from_doc(str(filepath))

    return ""

