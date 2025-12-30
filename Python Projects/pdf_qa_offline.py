"""
pdf_qa_offline.py
Offline PDF Q&A:
- Extracts text from PDF
- Chunks text (overlap)
- Builds embeddings with sentence-transformers locally
- Uses FAISS for nearest-neighbor retrieval
- Interactive CLI: ask questions -> shows top-k matching passages
No external API required.
"""

import sys
from pathlib import Path
from typing import List, Tuple
import math
import pdfplumber
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
from tqdm import tqdm

# ---------- Config ----------
EMBED_MODEL_NAME = "all-MiniLM-L6-v2"  # compact and fast
CHUNK_SIZE = 800          # characters per chunk
CHUNK_OVERLAP = 150       # overlap between chunks
TOP_K = 5                 # how many passages to return for each query

# ---------- Helpers ----------
def extract_text_from_pdf(pdf_path: Path) -> str:
    text_parts = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            txt = page.extract_text()
            if txt:
                text_parts.append(txt)
    return "\n\n".join(text_parts)

def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[Tuple[str,int,int]]:
    """
    Returns list of tuples: (chunk_text, start_char, end_char)
    """
    chunks = []
    start = 0
    text_len = len(text)
    while start < text_len:
        end = min(start + chunk_size, text_len)
        chunk = text[start:end]
        # If possible, extend to nearest sentence end for readability
        # but keep simple to avoid heavy NLP.
        chunks.append((chunk.strip(), start, end))
        if end == text_len:
            break
        start = max(end - overlap, end) - (0)  # ensure progress
    return chunks

def build_embeddings(model, chunks: List[str]) -> np.ndarray:
    # sentence-transformers returns numpy arrays
    embeddings = model.encode(chunks, show_progress_bar=True, convert_to_numpy=True, normalize_embeddings=True)
    return embeddings.astype('float32')

def create_faiss_index(embeddings: np.ndarray):
    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)  # cosine via normalized vectors (use inner product)
    index.add(embeddings)
    return index

def retrieve(index, query_emb: np.ndarray, top_k: int):
    D, I = index.search(query_emb, top_k)
    return I[0], D[0]

# ---------- Main ----------
def main(pdf_file: str):
    pdf_path = Path(pdf_file)
    if not pdf_path.exists():
        print("File not found:", pdf_path)
        return

    print("Extracting text from PDF...")
    text = extract_text_from_pdf(pdf_path)
    if not text.strip():
        print("No text found in PDF.")
        return

    print("Chunking text...")
    chunks_meta = chunk_text(text)
    chunks = [c[0] for c in chunks_meta]
    print(f"Created {len(chunks)} chunks.")

    print("Loading embedding model (this may take a moment)...")
    model = SentenceTransformer(EMBED_MODEL_NAME)

    print("Building embeddings...")
    embeddings = build_embeddings(model, chunks)

    print("Creating FAISS index...")
    index = create_faiss_index(embeddings)

    print("\nReady. Ask questions about the PDF. Type 'exit' or 'quit' to stop.\n")

    while True:
        q = input("Q> ").strip()
        if not q:
            continue
        if q.lower() in ("exit", "quit"):
            break

        q_emb = model.encode([q], convert_to_numpy=True, normalize_embeddings=True).astype('float32')
        ids, scores = retrieve(index, q_emb, TOP_K)

        print(f"\nTop {TOP_K} relevant passages (score = cosine approx):\n")
        for rank, (i, sc) in enumerate(zip(ids, scores), start=1):
            chunk_text, s, e = chunks_meta[i]
            snippet = chunk_text.replace("\n", " ").strip()
            snippet = (snippet[:400] + "…") if len(snippet) > 400 else snippet
            print(f"[{rank}] score={sc:.4f}\n{s}-{e} → {snippet}\n")

        print("-" * 80)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python pdf_qa_offline.py path/to/document.pdf")
    else:
        main(sys.argv[1])
