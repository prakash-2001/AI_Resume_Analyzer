from PyPDF2 import PdfReader


def extract_text_from_pdf(file) -> str:
    """Extract text from an uploaded PDF file."""
    if hasattr(file, "seek"):
        file.seek(0)

    reader = PdfReader(file)
    page_texts = []

    for page in reader.pages:
        text = page.extract_text()
        if text:
            page_texts.append(text.strip())

    return "\n\n".join(page_texts)
