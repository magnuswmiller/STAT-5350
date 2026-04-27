'''
rag.py

TODO Write summary here
'''

# Import Libraries
from pathlib import Path
from config import TOP_K
from llm import embed
from utils import chunk_text, cosine_similarity, extract_pdf_text

# Create in memory storage
vector_db: list[dict] = []
document_data: dict[str, int] = {}

# Ingest uploaded documents, chunk the text, embed the chunks, store in vector_db
def ingest_documents(files, embed_model_name:str) -> str:
    if not files:
        return "No files uploaded."
    
    new_files = []
    for file in files:
        path = file.name
        filename = Path(path).name

        if filename in document_data:
            continue

        try:
            full_text, num_pages = extract_pdf_text(path)
        except Exception as e:
            return f"Error reading file {filename}: {e}"
        
        document_data[filename] = {"filename": filename,
                                   "full_text": full_text,
                                   "num_pages": num_pages,}

        for chunk in chunk_text(full_text):
            if not chunk.strip():
                continue

            try:
                embedding = embed(chunk)
            except Exception as e:
                return f"Error embedding text (is Ollama running?): {e}"

            vector_db.append({"text":chunk,
                            "embedding":embedding,
                            "source": filename})
        
        new_files.append(filename)

    if not new_files:
        return "All uploaded files have been ingested."
    
    return (f"Ingested {len(new_files)} document(s): {', '.join(new_files)}\n"
            f"   Total chunks in vector DB: {len(vector_db)}\n"
            f"   Embedding model: {embed_model_name}")

# Reset button actions: clear vector database and document data
def reset() -> str:
    global vector_db, document_data
    vector_db = []
    document_data = {}
    return "All documents cleared."

# Return filenames of all ingested files
def get_document_list() -> list[str]:
    return list(document_data.keys())

# Embed user query and return the top k most relevant chunks from vector_db. Result is original chunk text and score key.
def semantic_search(query:str, k:int = TOP_K) -> list[dict]:
    if not vector_db:
        return []
    
    query_embedding = embed(query)
    scores = [(cosine_similarity(query_embedding, item["embedding"]), item) for item in vector_db]
    scores.sort(key=lambda x: x[0], reverse=True)

    return [{"score": score, **item} for score, item in scores[:k]]