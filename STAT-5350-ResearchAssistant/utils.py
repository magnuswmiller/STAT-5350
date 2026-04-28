'''
utils.py

Pure utility functions with no app state: text chunking, cosine similarity, PDF text extraction, APA citation
formatting, and bibliography PDF generation.
'''

# Import libraries
import os
import math
import re
import tempfile
import pypdf
from fpdf import FPDF

# Text chunking
def chunk_text(text:str, chunk_size:int=500, overlap:int=100) -> list[str]:
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunks.append(" ".join(words[start:end]))
        start += chunk_size - overlap
    return chunks

# Cosine similarity calculation
def cosine_similarity(v1:list[float], v2:list[float]) -> float:
    dot = sum(a * b for a, b in zip(v1, v2))
    n1 = math.sqrt(sum(a * a for a in v1))
    n2 = math.sqrt(sum(b * b for b in v2))
    return dot/(n1 * n2) if n1 and n2 else 0.0

# PDF text extraction routine. Returns full text and page count
def extract_pdf_text(file_path:str) -> tuple[str, int]:
    reader = pypdf.PdfReader(file_path)
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n\n".join(p.strip() for p in pages), len(reader.pages)

# Citatation formatting for APA 7th edition
def format_apa(citation_data: dict, fallback_filename: str) -> str:
    authors = citation_data.get("authors") or []
    title = citation_data.get("title") or fallback_filename
    year = citation_data.get("year") or "n.d."
    source = citation_data.get("source")
    volume = citation_data.get("volume")
    issue = citation_data.get("issue")
    pages = citation_data.get("pages")
    url = citation_data.get("url")

    if not authors:
        author_str = "Unknown Author"
    elif len(authors) == 1:
        author_str = authors[0]
    elif len(authors) <= 20:
        author_str = ", ".join(authors[:-1]) + ", & " + authors[-1]
    else:
        author_str = ", ".join(authors[:19]) + ", ... " + authors[-1]

    citation = f"{author_str} ({year}). {title}."
    if source:
        citation += f" *{source}*"
        if volume:
            citation += f", *{volume}*"
            if issue:
                citation += f"({issue})"
        if pages:
            citation += f", {pages}"
        citation += "."
    if url:
        citation += f" {url}"
    return citation

# Build bibliography pdf from citations
def build_bibliography(citations:list[str]) -> str:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_margins(25, 25, 25)
    
    # Header
    pdf.set_font("Times", "B", 16)
    pdf.cell(0, 12, "Works Cited", ln=True, align="C")

    # Body
    pdf.set_font("Times", "", size=12)
    for citation in citations:
        clean_citation = citation.replace("*", "")
        pdf.multi_cell(0, 7, clean_citation, border=0)
        pdf.ln(4)
    
    # Write file
    out_path = os.path.join(tempfile.gettempdir(), "bibliography.pdf")
    pdf.output(out_path)

    return out_path
