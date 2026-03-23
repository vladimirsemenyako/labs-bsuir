from datetime import datetime, UTC
import tempfile
from typing import Any, Literal
import math

from pathlib import Path

from bson import ObjectId
from fastapi import FastAPI, File, Form, HTTPException, Query, UploadFile
from pydantic import BaseModel, Field

from app.db import documents_collection, lemmas_collection, meta_collection
from app.nlp import POS_LABELS, build_concordance, frequencies, lemma_morphology, tokenize_with_pos
from app.text_extractor import extract_text_from_file


app = FastAPI(title="EYAZIIS Lab 2 API", version="1.0.0")


class DocumentCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    text: str = Field(min_length=5)
    author: str = ""
    year: str = ""
    source: str = ""


def _parse_doc_ids(doc_ids: str | None) -> list[ObjectId] | None:
    """doc_ids: comma-separated Mongo ObjectIds, or None => all documents."""
    if doc_ids is None:
        return None
    doc_ids = doc_ids.strip()
    if not doc_ids:
        return None

    parts = [p.strip() for p in doc_ids.split(",") if p.strip()]
    if not parts:
        return None
    ids: list[ObjectId] = []
    for p in parts:
        if not ObjectId.is_valid(p):
            raise HTTPException(status_code=400, detail=f"Invalid document id: {p}")
        ids.append(ObjectId(p))
    return ids


def _fetch_documents(doc_ids: str | None, *, projection: dict[str, Any]) -> list[dict[str, Any]]:
    ids = _parse_doc_ids(doc_ids)
    if ids is None:
        cursor = documents_collection.find({}, projection)
    else:
        cursor = documents_collection.find({"_id": {"$in": ids}}, projection)
    return list(cursor)


@app.get("/documents/{doc_id}")
def get_document(doc_id: str) -> dict[str, Any]:
    if not ObjectId.is_valid(doc_id):
        raise HTTPException(status_code=400, detail="Invalid document id.")
    doc = documents_collection.find_one(
        {"_id": ObjectId(doc_id)},
        {"tokens": 0},  # we return full text for the desktop-equivalent "double click"
    )
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")
    doc["id"] = str(doc["_id"])
    doc.pop("_id", None)
    return doc


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/pos-labels")
def get_pos_labels() -> dict[str, dict[str, str]]:
    return {"pos_labels": POS_LABELS}


@app.get("/documents")
def list_documents(
    page: int | None = Query(default=None, ge=1),
    page_size: int | None = Query(default=None, ge=1, le=100),
) -> Any:
    # Backward compatibility:
    # - Old frontend called `/documents` without pagination params and expected an array response.
    # - New frontend uses pagination and expects `{items, page, ...}`.
    if page is None and page_size is None:
        docs: list[dict[str, Any]] = []
        cursor = documents_collection.find({}, {"tokens": 0, "text": 0}).sort("created_at", -1).limit(5000)
        for doc in cursor:
            docs.append(
                {
                    "id": str(doc["_id"]),
                    "title": doc.get("title", ""),
                    "author": doc.get("author", ""),
                    "year": doc.get("year", ""),
                    "source": doc.get("source", ""),
                    "tokens_count": doc.get("tokens_count", 0),
                    "created_at": doc.get("created_at"),
                }
            )
        # Returning list will satisfy older JS renderer.
        return docs  # type: ignore[return-value]

    page = page or 1
    page_size = page_size or 20

    total = documents_collection.count_documents({})
    total_pages = max(1, math.ceil(total / page_size))
    page = min(page, total_pages)

    # Сумма токенов по всем документам корпуса
    agg = list(documents_collection.aggregate([{"$group": {"_id": None, "total_tokens": {"$sum": "$tokens_count"}}}]))
    total_tokens = int(agg[0]["total_tokens"]) if agg else 0

    skip = (page - 1) * page_size

    items: list[dict[str, Any]] = []
    cursor = documents_collection.find({}, {"tokens": 0, "text": 0}).sort("created_at", -1).skip(skip).limit(page_size)
    for doc in cursor:
        items.append(
            {
                "id": str(doc["_id"]),
                "title": doc.get("title", ""),
                "author": doc.get("author", ""),
                "year": doc.get("year", ""),
                "source": doc.get("source", ""),
                "tokens_count": doc.get("tokens_count", 0),
                "created_at": doc.get("created_at"),
            }
        )

    return {
        "items": items,
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": total_pages,
        "total_tokens": total_tokens,
    }


@app.post("/documents")
def create_document(payload: DocumentCreate) -> dict[str, str]:
    tokens = tokenize_with_pos(payload.text, lang="english")
    if not tokens:
        raise HTTPException(status_code=400, detail="Could not tokenize text.")

    result = documents_collection.insert_one(
        {
            "title": payload.title.strip(),
            "author": payload.author.strip(),
            "year": payload.year.strip(),
            "source": payload.source.strip(),
            "text": payload.text,
            "tokens": tokens,
            "tokens_count": len(tokens),
            "created_at": datetime.now(UTC).isoformat(),
        }
    )
    return {"id": str(result.inserted_id)}


@app.post("/documents/upload")
async def upload_documents(
    files: list[UploadFile] = File(...),
    author: str = Form(""),
    year: str = Form(""),
    source: str = Form(""),
    lang: str = Form("english"),
) -> dict[str, Any]:
    """Загрузка нескольких файлов (как в desktop-версии)."""
    inserted: list[str] = []
    skipped: list[str] = []

    allowed = {".txt", ".rtf", ".pdf", ".doc", ".docx"}
    for f in files:
        filename = (f.filename or "").strip()
        suffix = Path(filename).suffix.lower() if filename else ""
        if suffix not in allowed:
            skipped.append(filename)
            continue

        raw = await f.read()
        if not raw:
            skipped.append(filename)
            continue

        with tempfile.NamedTemporaryFile(suffix=suffix, delete=True) as tmp:
            tmp.write(raw)
            tmp.flush()
            text = extract_text_from_file(tmp.name)

        if not text or len(text.strip()) < 5:
            skipped.append(filename)
            continue

        tokens = tokenize_with_pos(text, lang=lang)
        if not tokens:
            skipped.append(filename)
            continue

        result = documents_collection.insert_one(
            {
                "title": Path(filename).stem or filename,
                "author": author.strip(),
                "year": year.strip(),
                "source": source.strip(),
                # На web у нас нет абсолютного пути пользователя, поэтому храним только имя файла.
                "filepath": filename,
                "text": text,
                "tokens": tokens,
                "tokens_count": len(tokens),
                "created_at": datetime.now(UTC).isoformat(),
            }
        )
        inserted.append(str(result.inserted_id))

    return {"inserted": inserted, "skipped": skipped}


@app.delete("/documents/{doc_id}")
def delete_document(doc_id: str) -> dict[str, str]:
    if not ObjectId.is_valid(doc_id):
        raise HTTPException(status_code=400, detail="Invalid document id.")
    result = documents_collection.delete_one({"_id": ObjectId(doc_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Document not found.")
    return {"status": "deleted"}


class LemmaCreate(BaseModel):
    lemma: str = Field(min_length=1, max_length=200)
    description: str = Field(default="", max_length=1000)


class LemmaUpdate(BaseModel):
    lemma: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=1000)


@app.get("/lemmas")
def list_lemmas() -> list[dict[str, Any]]:
    """Список пользовательских лемм (добавленных вручную)."""
    items = []
    for doc in lemmas_collection.find({}).sort("lemma", 1):
        items.append({
            "id": str(doc["_id"]),
            "lemma": doc.get("lemma", ""),
            "description": doc.get("description", ""),
            "created_at": doc.get("created_at"),
        })
    return items


@app.post("/lemmas")
def create_lemma(payload: LemmaCreate) -> dict[str, str]:
    lemma_str = payload.lemma.strip().lower()
    if lemmas_collection.find_one({"lemma": lemma_str}):
        raise HTTPException(status_code=400, detail="Такая лемма уже есть в списке.")
    result = lemmas_collection.insert_one(
        {
            "lemma": lemma_str,
            "description": (payload.description or "").strip(),
            "created_at": datetime.now(UTC).isoformat(),
        }
    )
    return {"id": str(result.inserted_id)}


@app.get("/lemmas/{lemma_id}")
def get_lemma(lemma_id: str) -> dict[str, Any]:
    if not ObjectId.is_valid(lemma_id):
        raise HTTPException(status_code=400, detail="Invalid lemma id.")
    doc = lemmas_collection.find_one({"_id": ObjectId(lemma_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Lemma not found.")
    return {
        "id": str(doc["_id"]),
        "lemma": doc.get("lemma", ""),
        "description": doc.get("description", ""),
        "created_at": doc.get("created_at"),
    }


@app.put("/lemmas/{lemma_id}")
def update_lemma(lemma_id: str, payload: LemmaUpdate) -> dict[str, str]:
    if not ObjectId.is_valid(lemma_id):
        raise HTTPException(status_code=400, detail="Invalid lemma id.")
    update_data: dict[str, Any] = {}
    if payload.lemma is not None:
        lemma_str = payload.lemma.strip().lower()
        if lemmas_collection.find_one({"lemma": lemma_str, "_id": {"$ne": ObjectId(lemma_id)}}):
            raise HTTPException(status_code=400, detail="Лемма с таким значением уже есть.")
        update_data["lemma"] = lemma_str
    if payload.description is not None:
        update_data["description"] = payload.description.strip()
    if not update_data:
        return {"status": "ok"}
    result = lemmas_collection.update_one({"_id": ObjectId(lemma_id)}, {"$set": update_data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Lemma not found.")
    return {"status": "updated"}


@app.delete("/lemmas/{lemma_id}")
def delete_lemma(lemma_id: str) -> dict[str, str]:
    if not ObjectId.is_valid(lemma_id):
        raise HTTPException(status_code=400, detail="Invalid lemma id.")
    result = lemmas_collection.delete_one({"_id": ObjectId(lemma_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Lemma not found.")
    return {"status": "deleted"}


@app.delete("/corpus/lemmas/{lemma:path}")
def remove_lemma_from_corpus(lemma: str) -> dict[str, Any]:
    """Удалить все вхождения леммы из токенов всех документов. Лемма больше не попадает в итоговый корпус."""
    lemma_str = lemma.strip().lower()
    if not lemma_str:
        raise HTTPException(status_code=400, detail="Lemma is empty.")
    updated = 0
    for doc in documents_collection.find({}, {"_id": 1, "tokens": 1}):
        tokens = doc.get("tokens", [])
        new_tokens = [t for t in tokens if (t.get("lemma") or "").lower() != lemma_str]
        if len(new_tokens) != len(tokens):
            documents_collection.update_one(
                {"_id": doc["_id"]},
                {"$set": {"tokens": new_tokens, "tokens_count": len(new_tokens)}},
            )
            updated += 1
    return {"status": "deleted", "documents_updated": updated}


@app.get("/search")
def search(
    query: str = Query(min_length=1),
    by: Literal["lemma", "word"] = "lemma",
    doc_ids: str | None = Query(default=None, description="Comma-separated ids for filtering"),
    context_size: int = Query(default=5, ge=1, le=20),
    max_lines: int = Query(default=200, ge=1, le=10000),
    page: int | None = Query(default=None, ge=1),
    page_size: int | None = Query(default=None, ge=1, le=500),
) -> Any:
    docs = _fetch_documents(doc_ids, projection={"title": 1, "tokens": 1})
    fetch_limit = max_lines if (page is None or page_size is None) else max(max_lines, 5000)
    rows = build_concordance(docs, query=query, by=by, context_size=context_size, max_lines=fetch_limit)
    if page is None or page_size is None:
        return rows
    total = len(rows)
    total_pages = max(1, math.ceil(total / page_size))
    page = min(page, total_pages)
    start = (page - 1) * page_size
    items = rows[start : start + page_size]
    return {"items": items, "page": page, "page_size": page_size, "total": total, "total_pages": total_pages}


@app.get("/frequencies")
def get_frequencies(
    kind: Literal["word", "lemma", "pos"] = "lemma",
    doc_ids: str | None = Query(default=None, description="Comma-separated ids for filtering"),
    limit: int = Query(default=500, ge=1, le=5000),
    page: int | None = Query(default=None, ge=1),
    page_size: int | None = Query(default=None, ge=1, le=500),
) -> Any:
    field_map = {"word": "word", "lemma": "lemma", "pos": "pos"}
    docs = _fetch_documents(doc_ids, projection={"tokens": 1})
    result = frequencies(docs, field_map[kind])
    if kind == "lemma":
        # Добавляем пользовательские леммы, которых ещё нет в корпусе (частота 0)
        corpus_items = {r["item"] for r in result}
        for doc in lemmas_collection.find({}, {"lemma": 1}):
            lem = (doc.get("lemma") or "").strip().lower()
            if lem and lem not in corpus_items:
                result.append({"item": lem, "freq": 0, "extra": "добавлена пользователем"})
                corpus_items.add(lem)
        result.sort(key=lambda r: (-r["freq"], r["item"]))
    if page is None or page_size is None:
        return result[:limit]
    total = len(result)
    total_pages = max(1, math.ceil(total / page_size))
    page = min(page, total_pages)
    start = (page - 1) * page_size
    items = result[start : start + page_size]
    return {"items": items, "page": page, "page_size": page_size, "total": total, "total_pages": total_pages}


@app.get("/morphology/{lemma}")
def get_morphology(
    lemma: str,
    doc_ids: str | None = Query(default=None, description="Comma-separated ids for filtering"),
    page: int | None = Query(default=None, ge=1),
    page_size: int | None = Query(default=None, ge=1, le=200),
) -> Any:
    docs = _fetch_documents(doc_ids, projection={"tokens": 1})
    result = lemma_morphology(docs, lemma)
    if page is None or page_size is None:
        return result
    total = len(result)
    total_pages = max(1, math.ceil(total / page_size))
    page = min(page, total_pages)
    start = (page - 1) * page_size
    items = result[start : start + page_size]
    return {"items": items, "page": page, "page_size": page_size, "total": total, "total_pages": total_pages}


class CorpusImport(BaseModel):
    replace: bool = True
    name: str | None = None
    documents: list[dict[str, Any]] = Field(default_factory=list)


@app.get("/corpus/export")
def export_corpus() -> dict[str, Any]:
    meta = meta_collection.find_one({"_id": "eyaziis_lab2_corpus"})
    corpus_name = (meta or {}).get("name") or "Music Corpus (Variant 21)"
    docs = list(documents_collection.find({}, {"tokens": 1, "text": 1, "title": 1, "author": 1, "year": 1, "source": 1, "filepath": 1}))

    exported_docs = []
    for d in docs:
        tokens = d.get("tokens", [])
        exported_docs.append(
            {
                "id": str(d.get("_id")),
                "filepath": d.get("filepath", ""),
                "title": d.get("title", ""),
                "author": d.get("author", ""),
                "year": d.get("year", ""),
                "source": d.get("source", ""),
                "text": d.get("text", ""),
                "tokens": tokens,
            }
        )

    return {
        "name": corpus_name,
        "next_doc_id": len(exported_docs) + 1,
        "documents": exported_docs,
    }


@app.post("/corpus/import")
def import_corpus(payload: CorpusImport) -> dict[str, Any]:
    if payload.replace:
        documents_collection.delete_many({})

    inserted = 0
    for d in payload.documents:
        title = (d.get("title") or "").strip()
        text = d.get("text") or ""
        author = (d.get("author") or "").strip()
        year = (d.get("year") or "").strip()
        source = (d.get("source") or "").strip()
        filepath = d.get("filepath") or ""
        tokens = d.get("tokens") or []

        if not title:
            # Fallback: попробуем использовать filename/stem или first token.
            title = Path(filepath).stem if filepath else "Imported document"

        # Если токены не пришли в payload, пересчитаем их из текста.
        if not tokens:
            tokens = tokenize_with_pos(text, lang="english")

        if not text or len(str(text).strip()) < 5 or not tokens:
            continue

        documents_collection.insert_one(
            {
                "title": title,
                "author": author,
                "year": year,
                "source": source,
                "filepath": filepath,
                "text": text,
                "tokens": tokens,
                "tokens_count": len(tokens),
                "created_at": datetime.now(UTC).isoformat(),
            }
        )
        inserted += 1

    if payload.name:
        meta_collection.update_one(
            {"_id": "eyaziis_lab2_corpus"},
            {"$set": {"name": payload.name}},
            upsert=True,
        )

    return {"inserted": inserted}
