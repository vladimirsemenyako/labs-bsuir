"""Синтаксический анализ текста на естественном языке — Лабораторная работа №3.

Использует spaCy для:
- разбора зависимостей (dependency parsing)
- визуализации деревьев зависимостей
"""

import tempfile
from pathlib import Path
from typing import Optional

# spaCy
try:
    import spacy
    from spacy import displacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False
    spacy = None
    displacy = None

# DEP relation labels (Universal Dependencies)
DEP_LABELS = {
    "ROOT": "Корень",
    "nsubj": "Подлежащее",
    "nsubj:pass": "Подлежащее (пассив)",
    "obj": "Прямое дополнение",
    "iobj": "Косвенное дополнение",
    "obl": "Обстоятельство",
    "advmod": "Обстоятельство-наречие",
    "amod": "Определение (прилаг.)",
    "det": "Детерминатив",
    "aux": "Вспомогательный глагол",
    "aux:pass": "Вспом. глагол (пассив)",
    "compound": "Составное слово",
    "fixed": "Фиксированное выражение",
    "flat": "Плоская конструкция",
    "xcomp": "Предикативное дополнение",
    "ccomp": "Дополнительная клауза",
    "advcl": "Обстоятельственная клауза",
    "acl": "Определительная клауза",
    "conj": "Сочинение",
    "cc": "Союз",
    "mark": "Маркер подчинения",
    "case": "Предлог/падеж",
    "punct": "Знак препинания",
    "appos": "Приложение",
    "nummod": "Числительное",
    "parataxis": "Паратаксис",
    "expl": "Эксплетив",
    "cop": "Связка",
    "dep": "Неопределённая зависимость",
}


class SyntacticAnalyzer:
    """Анализатор синтаксической структуры предложений."""

    def __init__(self, lang: str = "en"):
        self.lang = lang
        self._nlp = None
        self._ensure_model()

    def _ensure_model(self):
        if not SPACY_AVAILABLE:
            raise RuntimeError(
                "Установите spaCy: pip install spacy && python -m spacy download en_core_web_sm"
            )
        model = "en_core_web_sm" if self.lang == "en" else "ru_core_news_sm"
        try:
            self._nlp = spacy.load(model)
        except OSError:
            from spacy.cli import download
            download(model)
            self._nlp = spacy.load(model)

    def parse_sentences(self, text: str) -> list[dict]:
        """
        Разобрать текст на предложения и вернуть синтаксические структуры.

        Возвращает список предложений, каждое — словарь:
        - text: исходный текст предложения
        - tokens: список токенов с зависимостями
        - deps: список (idx, head_idx, dep_rel, token_text)
        """
        if not text or not text.strip():
            return []
        doc = self._nlp(text)
        result = []
        for sent in doc.sents:
            deps = []
            for token in sent:
                head_idx = token.head.i - sent.start if token.head != token else -1
                deps.append({
                    "idx": token.i - sent.start,
                    "text": token.text,
                    "lemma": token.lemma_,
                    "pos": token.pos_,
                    "dep": token.dep_,
                    "head_idx": head_idx,
                    "head_text": token.head.text if token.head != token else "ROOT",
                })
            result.append({
                "text": sent.text,
                "tokens": deps,
                "root": next((t for t in sent if t.dep_ == "ROOT"), None),
            })
        return result

    def get_dependency_table(self, parsed: list[dict]) -> list[tuple]:
        """Преобразовать результат в плоскую таблицу для отображения в GUI."""
        rows = []
        for sent in parsed:
            for t in sent["tokens"]:
                dep_label = DEP_LABELS.get(t["dep"], t["dep"])
                rows.append((
                    sent["text"][:60] + "..." if len(sent["text"]) > 60 else sent["text"],
                    t["idx"],
                    t["text"],
                    t["lemma"],
                    t["pos"],
                    t["head_text"],
                    dep_label,
                ))
        return rows

    def to_export_format(self, parsed: list[dict]) -> dict:
        """Формат для сохранения в JSON."""
        out = []
        for sent in parsed:
            out.append({
                "sentence": sent["text"],
                "dependencies": [
                    {
                        "token": t["text"],
                        "lemma": t["lemma"],
                        "pos": t["pos"],
                        "dep": t["dep"],
                        "head": t["head_text"],
                    }
                    for t in sent["tokens"]
                ],
            })
        return {"sentences": out, "lang": self.lang}

    def render_tree_html(self, text: str, output_path: Optional[str] = None) -> str:
        """
        Сгенерировать HTML с визуализацией дерева зависимостей.
        Возвращает путь к файлу.
        """
        if not text or not text.strip():
            return ""
        doc = self._nlp(text)
        html = displacy.render(
            list(doc.sents),
            style="dep",
            options={"compact": True, "distance": 100},
            page=False,
        )
        path = output_path or tempfile.mktemp(suffix=".html")
        Path(path).write_text(html, encoding="utf-8")
        return path

    @staticmethod
    def dep_label(dep: str) -> str:
        return DEP_LABELS.get(dep, dep)
