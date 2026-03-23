"""Извлечение текста из TXT, RTF, PDF, DOC, DOCX для корпуса (вариант 21 — английский, музыка)."""
import re
import sys
from pathlib import Path

# Добавляем родительскую папку (EYAZIIS) в путь для импорта lab_1
_eyaziis = Path(__file__).resolve().parent.parent
if str(_eyaziis) not in sys.path:
    sys.path.insert(0, str(_eyaziis))

try:
    from lab_1.text_processor import extract_text_from_file as extract_doc_docx
except ImportError:
    extract_doc_docx = None

# PDF
try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None

# RTF
try:
    from striprtf.striprtf import rtf_to_text
except ImportError:
    rtf_to_text = None


def extract_text_from_file(filepath):
    """Извлечение текста из TXT, RTF, PDF, DOC, DOCX."""
    path = Path(filepath)
    suffix = path.suffix.lower()

    if suffix == ".txt":
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
            try:
                return rtf_to_text(path.read_text(encoding="cp1252", errors="replace"))
            except Exception:
                return ""

    if suffix == ".pdf" and PdfReader is not None:
        try:
            reader = PdfReader(filepath)
            parts = []
            for page in reader.pages:
                t = page.extract_text()
                if t:
                    parts.append(t)
            return "\n".join(parts) if parts else ""
        except Exception:
            return ""

    if suffix in (".doc", ".docx") and extract_doc_docx is not None:
        return extract_doc_docx(filepath) or ""

    return ""
