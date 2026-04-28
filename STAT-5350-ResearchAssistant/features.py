'''
features.py

Implements the core user-facing features of the Research Paper Assistant: document Q&A, summarization,
citation extraction, and bibliography generation.
'''

# Importing Libraries
import re
import json
import rag
from llm import llm_chat
from utils import format_apa, build_bibliography

# Retrieves relevant chunks from documents and uses those chunks to answer question using llm. Appends exchange to chat history.
def answer_question(question:str, history:list) -> tuple[str, list]:
    if not rag.vector_db:
        reply = "No documents ingested yet. Please upload some PDFs first."
        history.append({"role": "user",      "content": question})
        history.append({"role": "assistant", "content": reply})
        return "", history
    
    results = rag.semantic_search(question)
    context = "\n\n---\n\n".join(f"[Source: {r['source']} | Score: {r['score']:.3f}]\n{r['text']}" for r in results)
    system = ("You are a research assistant. Answer the user's question using ONLY the "
              "provided context from the uploaded documents. Be specific and cite the source "
              "filename when possible. If the answer is not in the context, say so clearly.")
    user = f"Context:\n{context}\n\nQuestion:\n{question}"

    try:
        answer = llm_chat(system, user)
    except Exception as e:
        answer = f"LLM error (is Ollama running?): {e}"
    
    sources = list(dict.fromkeys(r["source"] for r in results))
    answer += f"\n\n*Sources: {', '.join(sources)}*"
 
    history.append({"role": "user",      "content": question})
    history.append({"role": "assistant", "content": answer})
    return "", history

# Generate structured summary (Title, Author, Date, Summary) for a single document
def summarize_document(filename:str) -> str:
    if filename not in rag.document_data:
        return f"'{filename}' not found. Please upload and ingest it first."
 
    # Cap at 3000 words to stay within model context limits
    preview = " ".join(rag.document_data[filename]["full_text"].split()[:1000])
 
    system = ("You are a research assistant. Given the text of an academic document, "
              "extract and return a structured summary with these exact fields:\n\n"
              "Title: <title of the document>\n"
              "Author(s): <author name(s) or 'Unknown'>\n"
              "Date: <publication or creation date, or 'Unknown'>\n"
              "Summary: <a 3-5 sentence abstract-style summary of the document's main contributions>\n\n"
              "Be concise and accurate. Only use information present in the text.")
    try:
        result = llm_chat(system, f"Document text:\n\n{preview}")
    except Exception as e:
        return f"LLM error: {e}"
 
    return f"**Summary — {filename}**\n\n{result}"

# Generate and concatenate summaries for every ingested document
def summarize_all() -> str:
    if not rag.document_data:
        return "No documents ingested yet."
    summaries = [summarize_document(name) for name in rag.document_data]
    return "\n\n---\n\n".join(summaries)

# Ask the LLM to extract structured citation metadata from a single document. Returns dict or None on failure.
def _extract_citation(filename:str) -> dict | None:
    preview = " ".join(rag.document_data[filename]["full_text"].split()[:500])
 
    system = ("You are a research librarian. Extract citation metadata from the document text "
          "and return ONLY a JSON object with these keys:\n"
          '  "authors": list of author names as strings,\n'
          '  "year": publication year as a string (or "n.d." if unknown),\n'
          '  "title": full title of the document,\n'
          '  "source": journal or conference name (or null),\n'
          '  "volume": journal volume number as a string (or null),\n'
          '  "issue": journal issue number as a string (or null),\n'
          '  "pages": page range as a string e.g. "123-145" (or null),\n'
          '  "url": URL or DOI if present in the text (or null)\n\n'
          "Return ONLY the JSON. No explanation. No markdown.")
    try:
        raw = llm_chat(system, f"Document text:\n\n{preview}")
        raw = re.sub(r"```json|```", "", raw).strip()
        return json.loads(raw)
    except Exception:
        return None

# Extract APA citations for all ingested documents, sort alphabetically, and export as markdown and PDF
def create_bibliography() -> tuple[str, str | None]:
    if not rag.document_data:
        return "No documents ingested yet.", None

    apa_lines = []
    failed = []
    for filename in rag.document_data:
        print(f"Extracting citation for: {filename}")
        meta = _extract_citation(filename)
        print(f"Citation result: {meta}")
        if meta:
            apa_lines.append(format_apa(meta, filename))
        else:
            failed.append(filename)
            apa_lines.append(f"[Could not extract citation for: {filename}]")

    apa_lines.sort()
    text_output = "**References**\n\n" + "\n\n".join(apa_lines)

    if failed:
        text_output += f"\n\nCitation extraction failed for: {', '.join(failed)}"

    print("Building PDF...")
    try:
        pdf_path = build_bibliography(apa_lines)
        print(f"PDF built at: {pdf_path}")
    except Exception as e:
        return text_output + f"\n\nPDF generation error: {e}", None

    print("Returning results...")
    return text_output, pdf_path
# def create_bibliography() -> tuple[str, str | None]:
#     if not rag.document_data:
#         return "No documents ingested yet.", None
 
#     apa_lines = []
#     failed = []
#     for filename in rag.document_data:
#         meta = _extract_citation(filename)
#         if meta:
#             apa_lines.append(format_apa(meta, filename))
#         else:
#             failed.append(filename)
#             apa_lines.append(f"[Could not extract citation for: {filename}]")
 
#     apa_lines.sort()
#     text_output = "**References**\n\n" + "\n\n".join(apa_lines)
 
#     if failed:
#         text_output += f"\n\nCitation extraction failed for: {', '.join(failed)}"
 
#     try:
#         pdf_path = build_bibliography(apa_lines)
#     except Exception as e:
#         return text_output + f"\n\nPDF generation error: {e}", None
 
#     return text_output, pdf_path
