"""Извлечение текста из TXT, RTF, PDF, HTML, DOC, DOCX — Лабораторная работа №3."""
import re
import sys
from pathlib import Path

_eyaziis = Path(__file__).resolve().parent.parent
if str(_eyaziis) not in sys.path:
    sys.path.insert(0, str(_eyaziis))

try:
    from lab_1.text_processor import extract_text_from_file as extract_doc_docx
except ImportError:
    extract_doc_docx = None

try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None

try:
    from striprtf.striprtf import rtf_to_text
except ImportError:
    rtf_to_text = None

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None


def _extract_from_doc(filepath: str) -> str:
    """Упрощённое извлечение для .doc."""
    path = Path(filepath)
    try:
        raw = path.read_bytes()
        text = re.sub(rb"[^\x20-\x7E\n\r\t]", b" ", raw).decode("utf-8", errors="replace")
        text = re.sub(r"\s+", " ", text).strip()
        return text if len(text) > 50 else ""
    except Exception:
        return ""


def extract_text_from_file(filepath: str) -> str:
    """Извлечение текста из TXT, RTF, PDF, HTML, DOC, DOCX."""
    path = Path(filepath)
    suffix = path.suffix.lower()

    if suffix == ".txt":
        try:
            for enc in ("utf-8", "cp1252", "latin-1", "cp1251"):
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
            reader = PdfReader(str(filepath))
            parts = []
            for page in reader.pages:
                t = page.extract_text()
                if t:
                    parts.append(t)
            return "\n".join(parts) if parts else ""
        except Exception:
            return ""

    if suffix in (".html", ".htm") and BeautifulSoup is not None:
        try:
            html = path.read_text(encoding="utf-8", errors="replace")
            soup = BeautifulSoup(html, "html.parser")
            for tag in soup(["script", "style"]):
                tag.decompose()
            return soup.get_text(separator="\n", strip=True)
        except Exception:
            try:
                raw = path.read_bytes()
                html = raw.decode("utf-8", errors="replace")
                soup = BeautifulSoup(html, "html.parser")
                for tag in soup(["script", "style"]):
                    tag.decompose()
                return soup.get_text(separator="\n", strip=True)
            except Exception:
                return ""

    if suffix in (".doc", ".docx") and extract_doc_docx is not None:
        return extract_doc_docx(str(filepath)) or ""

    if suffix == ".doc":
        return _extract_from_doc(str(filepath))

    return ""
