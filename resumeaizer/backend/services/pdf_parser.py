import fitz

def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    text = ""
    with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
        for page in doc:
            page_text = page.get_text()
            text += f"\n--- Page {page.number + 1} ---\n{page_text}"
    return text.strip()