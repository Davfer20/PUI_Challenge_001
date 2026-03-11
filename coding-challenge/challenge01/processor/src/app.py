import json
import os
import re
from pathlib import Path
from typing import List, Dict, Any, Dict

from elasticsearch import Elasticsearch
from sentence_splitter import SentenceSplitter
from sentence_transformers import SentenceTransformer

ELASTICSEARCH_URL = os.getenv("ELASTICSEARCH_URL", "http://elasticsearch:9200")
INPUT_DIR = os.getenv("INPUT_DIR", "/app/input")
INDEX_NAME = os.getenv("INDEX_NAME", "documents")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

# Simple sentence embeddings model
model = SentenceTransformer(EMBEDDING_MODEL)

# Sentence Splitter
splitter = SentenceSplitter(language="en")


def create_index(es: Elasticsearch, index_name: str) -> None:
    # Create the index if it does not exist.
    if es.indices.exists(index=index_name):
        es.indices.delete(index=index_name)

    mapping = {
        "mappings": {
            "properties": {
                "doc_id": {"type": "keyword"},
                "chunk_id": {"type": "keyword"},
                "title": {"type": "text"},
                "description": {"type": "text"},
                "authors": {"type": "keyword"},
                "subjects": {"type": "keyword"},
                "language": {"type": "keyword"},
                "first_publish_year": {"type": "integer"},
                 # TODO: Complete the mapping with the required fields and types.
                "embedding": {
                    "type": "dense_vector",
                    "dims": 384,
                    "index": True
                }
            }
        }
    }

    es.indices.create(index=index_name, body=mapping)
    print(f"Created index: {index_name}")


def load_json_files(input_dir: str) -> List[Dict[str, Any]]:
    documents = []
    for path in Path(input_dir).glob("*.json"):
        with open(path, "r", encoding="utf-8") as f:
            documents.append(json.load(f))
    return documents


def split_into_chunks(text: str, max_sentences: int = 5) -> List[str]:
    # Split the text into small chunks.
    sentences = splitter.split(text)
    chunks = []

    for i in range(0, len(sentences), max_sentences):
        chunk = " ".join(sentences[i:i + max_sentences]).strip()
        if chunk:
            chunks.append(chunk)
    return chunks


def generate_embedding(text: str) -> List[float]:
    return model.encode(
        text
    ).tolist()

def clean_string(string: Any) -> str:
    text = re.sub(r'[^\x00-\x7F]+', ' ', string)
    text = re.sub(r'[-.:,!?\(\)]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def proccess_documents(document: Dict[str, Any]) -> List[Dict[str, Any]]:
    # TODO: Complete the required code to process each document:
    # Split the document into chunks
    # Generate an embedding for each chunk
    # Add the embeddings to a new document along with the remaining fields
    # Filter and replace non-ASCII characters
    # Ensure that subjects are capitalized
    doc_id = document.get("id")
    title = document.get("title", "")
    description = document.get("description", "")
    authors = document.get("authors", [])
    subjects = document.get("subjects", [])
    language = document.get("language", [])
    year = document.get("first_publish_year")

    if not doc_id or not description:
        raise ValueError("Document must contain at least 'id' and 'description'")

    clean_title = clean_string(title)
    clean_description = clean_string(description)
    clean_authors = [clean_string(a) for a in authors]
    clean_subjects = [clean_string(s).title() for s in subjects]
    clean_language = [clean_string(l) for l in language]

    chunks = split_into_chunks(clean_description)

    result = []
    for idx, chunk in enumerate(chunks):
        clean_chunk = clean_string(chunk)
        embedding = generate_embedding(clean_chunk)
        built_doc = {
            "doc_id": str(doc_id),
            "chunk_id": f"{doc_id}-{idx}",
            "title": clean_title,
            "description": clean_description,
            "authors": clean_authors,
            "subjects": clean_subjects,
            "language": clean_language,
            "first_publish_year": year,
            "content": clean_chunk,
            "embedding": embedding
        }
        result.append(built_doc)

    return result


def index_documents(es: Elasticsearch, index_name: str, docs: List[Dict[str, Any]]) -> None:
     # TODO: Index documents into Elasticsearch
    for doc in docs:
        es.index(index=index_name, id=doc["chunk_id"], document=doc)

def semantic_search(es: Elasticsearch, index_name: str, query_text: str, k: int = 3) -> Dict[str, Any]:
    query_vector = generate_embedding(query_text)

    body = {
        "knn": {
            "field": "embedding",
            "query_vector": query_vector,
            "k": k,
            "num_candidates": 10
        },
        "_source": ["doc_id", "chunk_id", "title", "content"]
    }

    return es.search(index=index_name, body=body)


def main() -> None:
    es = Elasticsearch(ELASTICSEARCH_URL)
    create_index(es, INDEX_NAME)
    documents = load_json_files(INPUT_DIR)

    if not documents:
        print("No JSON files found.")
        return

    for document in documents:
        built_docs = proccess_documents(document)
        index_documents(es, INDEX_NAME, built_docs)

    print("Semantic search: examples")

    queries = [
        "space exploration and stars",
        "science fictions and magic",
        "history of world war",
    ]

    for query in queries:
        print(f"\nQuery: {query}")
        response = semantic_search(es, INDEX_NAME, query, k=3)
        hits = response.get("hits", {}).get("hits", [])

        for hit in hits:
            source = hit.get("_source", {})
            print(
                f"doc_id={source.get('doc_id')} "
                f"title={source.get('title')} "
                f"chunks={source.get('content', '')[:120]}"
            )


if __name__ == "__main__":
    main()
