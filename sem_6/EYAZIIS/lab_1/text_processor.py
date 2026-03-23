import re
import json
from pathlib import Path
from collections import defaultdict

try:
    from docx import Document as DocxDocument
except ImportError:
    DocxDocument = None

import nltk
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet
from nltk.collocations import BigramCollocationFinder
from nltk.metrics import BigramAssocMeasures


def _ensure_nltk_data():
    try:
        nltk.data.find("tokenizers/punkt")
    except LookupError:
        nltk.download("punkt", quiet=True)
    try:
        nltk.data.find("corpora/wordnet")
    except LookupError:
        nltk.download("wordnet", quiet=True)
        nltk.download("omw-1.4", quiet=True)
    try:
        nltk.data.find("taggers/averaged_perceptron_tagger")
    except LookupError:
        nltk.download("averaged_perceptron_tagger", quiet=True)


def get_wordnet_pos(treebank_tag):
    if treebank_tag.startswith("J"):
        return wordnet.ADJ
    if treebank_tag.startswith("V"):
        return wordnet.VERB
    if treebank_tag.startswith("N"):
        return wordnet.NOUN
    if treebank_tag.startswith("R"):
        return wordnet.ADV
    return wordnet.NOUN


def extract_text_from_file(filepath):
    """Извлечение текста из DOC или DOCX."""
    path = Path(filepath)
    suffix = path.suffix.lower()

    if suffix == ".docx" and DocxDocument is not None:
        doc = DocxDocument(filepath)
        return "\n".join(p.text for p in doc.paragraphs)

    if suffix == ".doc":
        try:
            raw = path.read_bytes()
            text = re.sub(rb"[^\x20-\x7E\n\r\t]", b" ", raw).decode("utf-8", errors="replace")
            text = re.sub(r"\s+", " ", text).strip()
            return text if len(text) > 50 else ""
        except Exception:
            return ""

    return ""


def tokenize_and_lemmatize(text, lang="english"):
    _ensure_nltk_data()
    if not text or not text.strip():
        return [], []
    tokens = word_tokenize(text.lower(), language=lang)
    words = [w for w in tokens if w.isalpha() and len(w) > 1]
    if not words:
        return [], []
    pos_tags = nltk.pos_tag(words)
    lemmatizer = WordNetLemmatizer()
    lemmas = []
    for word, tag in pos_tags:
        pos_wn = get_wordnet_pos(tag)
        lem = lemmatizer.lemmatize(word, pos=pos_wn)
        lemmas.append(lem)
    return words, lemmas


def tokenize_with_pos(text, lang="english"):
    """Токенизация с возвратом лемм и POS-тегов (Penn Treebank) для корпусного менеджера."""
    _ensure_nltk_data()
    if not text or not text.strip():
        return []
    tokens = word_tokenize(text.lower(), language=lang)
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


def extract_collocations_from_text(text, top_n=200, min_freq=2):
    _ensure_nltk_data()
    words, lemmas = tokenize_and_lemmatize(text)
    if len(lemmas) < 2:
        return []
    finder = BigramCollocationFinder.from_words(lemmas)
    finder.apply_freq_filter(min_freq)
    scored = finder.nbest(BigramAssocMeasures.pmi, top_n)
    raw_freq = finder.ngram_fd
    return [(bigram, raw_freq[bigram]) for bigram in scored]


def build_lemma_collocation_dict(text, top_collocations_per_lemma=50):
    words, lemmas = tokenize_and_lemmatize(text)
    if len(lemmas) < 2:
        return {}
    bigram_freq = defaultdict(int)
    for i in range(len(lemmas) - 1):
        a, b = lemmas[i], lemmas[i + 1]
        if a != b:
            bigram_freq[(a, b)] += 1
    lemma_partners = defaultdict(lambda: defaultdict(int))
    for (a, b), cnt in bigram_freq.items():
        lemma_partners[a][b] += cnt
        lemma_partners[b][a] += cnt
    result = {}
    for lemma in sorted(lemma_partners.keys()):
        partners = lemma_partners[lemma]
        sorted_partners = sorted(
            partners.items(),
            key=lambda x: -x[1]
        )[:top_collocations_per_lemma]
        result[lemma] = [{"word": w, "freq": c} for w, c in sorted_partners]
    return result


def load_dictionary(json_path):
    path = Path(json_path)
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_dictionary(data, json_path):
    path = Path(json_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
