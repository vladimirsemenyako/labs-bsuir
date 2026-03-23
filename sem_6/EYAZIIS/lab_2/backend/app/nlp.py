from collections import defaultdict
from typing import Any

import nltk
from nltk.corpus import wordnet
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize


POS_LABELS = {
    "CC": "Conjunction",
    "CD": "Cardinal",
    "DT": "Determiner",
    "EX": "Existential",
    "FW": "Foreign",
    "IN": "Preposition",
    "JJ": "Adjective",
    "JJR": "Adj. comparative",
    "JJS": "Adj. superlative",
    "LS": "List",
    "MD": "Modal",
    "NN": "Noun",
    "NNS": "Noun plural",
    "NNP": "Proper noun",
    "NNPS": "Proper noun plural",
    "PDT": "Predeterminer",
    "POS": "Possessive",
    "PRP": "Personal pron.",
    "PRP$": "Possessive pron.",
    "RB": "Adverb",
    "RBR": "Adv. comparative",
    "RBS": "Adv. superlative",
    "RP": "Particle",
    "SYM": "Symbol",
    "TO": "To",
    "UH": "Interjection",
    "VB": "Verb",
    "VBD": "Verb past",
    "VBG": "Verb gerund",
    "VBN": "Verb past part.",
    "VBP": "Verb non-3rd",
    "VBZ": "Verb 3rd",
    "WDT": "Wh-determiner",
    "WP": "Wh-pronoun",
    "WP$": "Possessive wh-",
    "WRB": "Wh-adverb",
}


def ensure_nltk_data() -> None:
    for path, package in (
        ("tokenizers/punkt", "punkt"),
        # Newer NLTK versions may require this extra dataset for sentence splitting.
        # If it's missing, `word_tokenize(... preserve_line=False)` can crash inside `sent_tokenize`.
        ("tokenizers/punkt_tab/english", "punkt_tab"),
        # Depending on NLTK version the tagger is stored either as:
        #  - taggers/averaged_perceptron_tagger/
        #  - taggers/averaged_perceptron_tagger_eng/
        ("taggers/averaged_perceptron_tagger", "averaged_perceptron_tagger"),
        ("taggers/averaged_perceptron_tagger_eng", "averaged_perceptron_tagger_eng"),
        ("corpora/wordnet", "wordnet"),
        ("corpora/omw-1.4", "omw-1.4"),
    ):
        try:
            nltk.data.find(path)
        except LookupError:
            nltk.download(package, quiet=True)


def get_wordnet_pos(treebank_tag: str) -> str:
    if treebank_tag.startswith("J"):
        return wordnet.ADJ
    if treebank_tag.startswith("V"):
        return wordnet.VERB
    if treebank_tag.startswith("N"):
        return wordnet.NOUN
    if treebank_tag.startswith("R"):
        return wordnet.ADV
    return wordnet.NOUN


def tokenize_with_pos(text: str, lang: str = "english") -> list[dict[str, str]]:
    ensure_nltk_data()
    if not text or not text.strip():
        return []

    # preserve_line=True avoids sentence segmentation inside `word_tokenize`
    # (prevents dependency on punkt_tab in some NLTK versions).
    tokens = word_tokenize(text.lower(), language=lang, preserve_line=True)
    words = [w for w in tokens if w.isalpha() and len(w) > 1]
    if not words:
        return []

    pos_tags = nltk.pos_tag(words)
    lemmatizer = WordNetLemmatizer()

    result = []
    for word, tag in pos_tags:
        pos_wn = get_wordnet_pos(tag)
        lemma = lemmatizer.lemmatize(word, pos=pos_wn)
        result.append({"word": word, "lemma": lemma, "pos": tag})

    return result


def search_hits(tokens: list[dict[str, str]], query: str, by: str) -> list[int]:
    query = query.strip().lower()
    if not query:
        return []

    token_key = "lemma" if by == "lemma" else "word"

    if " " not in query:
        return [i for i, token in enumerate(tokens) if token.get(token_key) == query]

    parts = query.split()
    hits: list[int] = []
    for i in range(len(tokens)):
        ok = True
        for offset, part in enumerate(parts):
            if i + offset >= len(tokens):
                ok = False
                break
            if tokens[i + offset].get(token_key) != part:
                ok = False
                break
        if ok:
            hits.append(i)
    return hits


def build_concordance(
    documents: list[dict[str, Any]],
    query: str,
    by: str = "lemma",
    context_size: int = 5,
    max_lines: int = 200,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for doc in documents:
        tokens = doc.get("tokens", [])
        for idx in search_hits(tokens, query, by):
            start = max(0, idx - context_size)
            end = min(len(tokens), idx + context_size + 1)
            rows.append(
                {
                    "left": " ".join(t["word"] for t in tokens[start:idx]),
                    "center": tokens[idx]["word"],
                    "right": " ".join(t["word"] for t in tokens[idx + 1 : end]),
                    "doc_id": str(doc.get("_id")),
                    "doc_title": doc.get("title", ""),
                }
            )
            if len(rows) >= max_lines:
                return rows
    return rows


def frequencies(
    documents: list[dict[str, Any]],
    token_field: str,
) -> list[dict[str, Any]]:
    freq = defaultdict(int)
    for doc in documents:
        for token in doc.get("tokens", []):
            value = token.get(token_field)
            if value:
                freq[value] += 1

    sorted_items = sorted(freq.items(), key=lambda item: (-item[1], item[0]))
    result = [{"item": k, "freq": v} for k, v in sorted_items]
    if token_field == "pos":
        for row in result:
            row["extra"] = POS_LABELS.get(row["item"], "")
    return result


def lemma_morphology(documents: list[dict[str, Any]], lemma: str) -> list[dict[str, Any]]:
    lemma = lemma.strip().lower()
    forms = defaultdict(lambda: defaultdict(int))

    for doc in documents:
        for token in doc.get("tokens", []):
            if token.get("lemma") != lemma:
                continue
            forms[token["word"]][token["pos"]] += 1

    rows: list[dict[str, Any]] = []
    for word in sorted(forms.keys()):
        sorted_pos = sorted(forms[word].items(), key=lambda item: (-item[1], item[0]))
        for pos, count in sorted_pos:
            rows.append(
                {
                    "word": word,
                    "pos": pos,
                    "pos_label": POS_LABELS.get(pos, pos),
                    "count": count,
                }
            )
    return rows
