import fitz  # PyMuPDF
import requests

def download_and_chunk_pdf(pdf_url: str, max_chunk_tokens: int = 500) -> list[str]:
    # Step 1: Download the PDF file
    response = requests.get(pdf_url)
    if response.status_code != 200:
        raise ValueError("Failed to download PDF.")

    with open("temp.pdf", "wb") as f:
        f.write(response.content)

    # Step 2: Extract text from each page
    doc = fitz.open("temp.pdf")
    full_text = "\n".join([page.get_text() for page in doc])
    doc.close()

    # Step 3: Chunk text into blocks of ~500 words
    words = full_text.split()
    chunks = []
    chunk = []

    for word in words:
        chunk.append(word)
        if len(chunk) >= max_chunk_tokens:
            chunks.append(" ".join(chunk))
            chunk = []

    if chunk:
        chunks.append(" ".join(chunk))

    return chunks
