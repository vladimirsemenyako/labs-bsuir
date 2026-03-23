import os
from pymongo import MongoClient


MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "corpus_db")

client = MongoClient(MONGO_URI)
db = client[MONGO_DB_NAME]
documents_collection = db["documents"]
meta_collection = db["meta"]
lemmas_collection = db["lemmas"]

# Useful indexes for common operations in this lab.
documents_collection.create_index("title")
documents_collection.create_index("tokens.lemma")
documents_collection.create_index("tokens.word")
documents_collection.create_index("tokens.pos")

# Store corpus-level metadata, e.g. corpus name.
meta_collection.create_index("_id")

lemmas_collection.create_index("lemma", unique=True)
