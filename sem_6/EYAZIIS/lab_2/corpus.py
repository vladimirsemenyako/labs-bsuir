# -*- coding: utf-8 -*-
"""Корпус текстов: хранение, индексация, поиск, конкорданс, частотные характеристики (вариант 21 — английский, музыка)."""
import json
from pathlib import Path
from collections import defaultdict

import sys
_eyaziis = Path(__file__).resolve().parent.parent
if str(_eyaziis) not in sys.path:
    sys.path.insert(0, str(_eyaziis))

from lab_1.text_processor import tokenize_with_pos


# Краткие названия частей речи (Penn Treebank -> читаемый вид)
POS_LABELS = {
    "CC": "Conjunction", "CD": "Cardinal", "DT": "Determiner", "EX": "Existential",
    "FW": "Foreign", "IN": "Preposition", "JJ": "Adjective", "JJR": "Adj. comparative",
    "JJS": "Adj. superlative", "LS": "List", "MD": "Modal", "NN": "Noun", "NNS": "Noun plural",
    "NNP": "Proper noun", "NNPS": "Proper noun plural", "PDT": "Predeterminer",
    "POS": "Possessive", "PRP": "Personal pron.", "PRP$": "Possessive pron.",
    "RB": "Adverb", "RBR": "Adv. comparative", "RBS": "Adv. superlative",
    "RP": "Particle", "SYM": "Symbol", "TO": "To", "UH": "Interjection",
    "VB": "Verb", "VBD": "Verb past", "VBG": "Verb gerund", "VBN": "Verb past part.",
    "VBP": "Verb non-3rd", "VBZ": "Verb 3rd", "WDT": "Wh-determiner",
    "WP": "Wh-pronoun", "WP$": "Possessive wh-", "WRB": "Wh-adverb",
}


class Corpus:
    """Корпус текстов с морфологической разметкой и поиском."""

    def __init__(self, name="Music Corpus (Variant 21)"):
        self.name = name
        self.documents = []   # list of {id, filepath, title, author, year, source, text, tokens}
        self._word_index = defaultdict(list)   # word_form -> [(doc_idx, token_idx)]
        self._lemma_index = defaultdict(list)
        self._pos_index = defaultdict(list)
        self._next_doc_id = 1

    def add_document(self, filepath, text, title=None, author=None, year=None, source=None, lang="english"):
        """Добавить документ в корпус. text — извлечённый текст."""
        if not text or len(text.strip()) < 5:
            return False
        doc_id = self._next_doc_id
        self._next_doc_id += 1
        path = Path(filepath)
        tokens = tokenize_with_pos(text, lang=lang)
        if not tokens:
            return False
        doc = {
            "id": doc_id,
            "filepath": str(path.absolute()),
            "title": title or path.stem,
            "author": author or "",
            "year": year or "",
            "source": source or "",
            "text": text,
            "tokens": tokens,
        }
        doc_idx = len(self.documents)
        self.documents.append(doc)
        for i, t in enumerate(tokens):
            self._word_index[t["word"]].append((doc_idx, i))
            self._lemma_index[t["lemma"]].append((doc_idx, i))
            self._pos_index[t["pos"]].append((doc_idx, i))
        return True

    def remove_document(self, doc_index):
        """Удалить документ по индексу в списке."""
        if doc_index < 0 or doc_index >= len(self.documents):
            return False
        doc = self.documents[doc_index]
        # Перестроить индексы без этого документа
        new_docs = [d for i, d in enumerate(self.documents) if i != doc_index]
        self.documents = new_docs
        self._rebuild_indexes()
        return True

    def _rebuild_indexes(self):
        self._word_index = defaultdict(list)
        self._lemma_index = defaultdict(list)
        self._pos_index = defaultdict(list)
        for doc_idx, doc in enumerate(self.documents):
            for i, t in enumerate(doc["tokens"]):
                self._word_index[t["word"]].append((doc_idx, i))
                self._lemma_index[t["lemma"]].append((doc_idx, i))
                self._pos_index[t["pos"]].append((doc_idx, i))

    def search(self, query, by="lemma", doc_indices=None):
        """Поиск: query — слово/фраза (лемма или словоформа), by in ('lemma','word'). Возвращает список (doc_idx, token_idx)."""
        query = query.strip().lower()
        if not query:
            return []
        if " " in query:
            # Фраза: ищем по первому слову, потом проверяем контекст
            words = query.split()
            first = words[0]
            index = self._lemma_index if by == "lemma" else self._word_index
            candidates = index.get(first, [])
            result = []
            for doc_idx, token_idx in candidates:
                if doc_indices is not None and doc_idx not in doc_indices:
                    continue
                doc = self.documents[doc_idx]
                toks = doc["tokens"]
                match = True
                for k, w in enumerate(words):
                    pos = token_idx + k
                    if pos >= len(toks):
                        match = False
                        break
                    tw = toks[pos]["lemma"] if by == "lemma" else toks[pos]["word"]
                    if tw != w:
                        match = False
                        break
                if match:
                    result.append((doc_idx, token_idx))
            return result
        index = self._lemma_index if by == "lemma" else self._word_index
        hits = index.get(query, [])
        if doc_indices is not None:
            hits = [(d, i) for d, i in hits if d in doc_indices]
        return hits

    def get_concordance(self, query, by="lemma", context_size=5, doc_indices=None, max_lines=200):
        """Конкорданс: контексты вхождений query (слева и справа context_size слов)."""
        hits = self.search(query, by=by, doc_indices=doc_indices)
        lines = []
        for doc_idx, token_idx in hits[:max_lines]:
            doc = self.documents[doc_idx]
            toks = doc["tokens"]
            start = max(0, token_idx - context_size)
            end = min(len(toks), token_idx + context_size + 1)
            left = " ".join(t["word"] for t in toks[start:token_idx])
            right = " ".join(t["word"] for t in toks[token_idx + 1:end])
            center = toks[token_idx]["word"]
            title = doc.get("title", "")
            lines.append({
                "left": left,
                "center": center,
                "right": right,
                "doc_title": title,
                "doc_idx": doc_idx,
            })
        return lines

    def get_word_form_frequencies(self, doc_indices=None):
        """Частоты словоформ по корпусу."""
        freq = defaultdict(int)
        docs = self.documents
        if doc_indices is not None:
            docs = [self.documents[i] for i in doc_indices if 0 <= i < len(self.documents)]
        for doc in docs:
            for t in doc["tokens"]:
                freq[t["word"]] += 1
        return dict(sorted(freq.items(), key=lambda x: -x[1]))

    def get_lemma_frequencies(self, doc_indices=None):
        """Частоты лемм."""
        freq = defaultdict(int)
        docs = self.documents
        if doc_indices is not None:
            docs = [self.documents[i] for i in doc_indices if 0 <= i < len(self.documents)]
        for doc in docs:
            for t in doc["tokens"]:
                freq[t["lemma"]] += 1
        return dict(sorted(freq.items(), key=lambda x: -x[1]))

    def get_pos_frequencies(self, doc_indices=None):
        """Частоты грамматических категорий (POS)."""
        freq = defaultdict(int)
        docs = self.documents
        if doc_indices is not None:
            docs = [self.documents[i] for i in doc_indices if 0 <= i < len(self.documents)]
        for doc in docs:
            for t in doc["tokens"]:
                freq[t["pos"]] += 1
        return dict(sorted(freq.items(), key=lambda x: -x[1]))

    def get_morphology_for_lemma(self, lemma, doc_indices=None):
        """Морфологические характеристики леммы: словоформы и POS."""
        lemma = lemma.strip().lower()
        forms = defaultdict(lambda: defaultdict(int))  # word -> pos -> count
        hits = self._lemma_index.get(lemma, [])
        for doc_idx, token_idx in hits:
            if doc_indices is not None and doc_idx not in doc_indices:
                continue
            t = self.documents[doc_idx]["tokens"][token_idx]
            forms[t["word"]][t["pos"]] += 1
        result = []
        for word in sorted(forms.keys()):
            for pos, cnt in sorted(forms[word].items(), key=lambda x: -x[1]):
                result.append({"word": word, "pos": pos, "pos_label": POS_LABELS.get(pos, pos), "count": cnt})
        return result

    def get_document_metadata(self, doc_index):
        """Метаданные документа (библиографические, типологические)."""
        if 0 <= doc_index < len(self.documents):
            d = self.documents[doc_index]
            return {
                "title": d.get("title", ""),
                "author": d.get("author", ""),
                "year": d.get("year", ""),
                "source": d.get("source", ""),
                "filepath": d.get("filepath", ""),
                "tokens_count": len(d.get("tokens", [])),
            }
        return None

    def save(self, filepath):
        """Сохранить корпус в JSON (без полного текста в целях размера — только токены и метаданные)."""
        data = {
            "name": self.name,
            "next_doc_id": self._next_doc_id,
            "documents": [
                {
                    "id": d["id"],
                    "filepath": d["filepath"],
                    "title": d["title"],
                    "author": d.get("author", ""),
                    "year": d.get("year", ""),
                    "source": d.get("source", ""),
                    "text": d.get("text", ""),
                    "tokens": d["tokens"],
                }
                for d in self.documents
            ],
        }
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True

    def load(self, filepath):
        """Загрузить корпус из JSON."""
        path = Path(filepath)
        if not path.exists():
            return False
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.name = data.get("name", self.name)
        self._next_doc_id = data.get("next_doc_id", 1)
        self.documents = data.get("documents", [])
        self._rebuild_indexes()
        return True
