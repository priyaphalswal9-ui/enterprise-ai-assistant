from pathlib import Path

from pypdf import PdfReader
from docx import Document as DocxDocument


def extract_text_from_pdf(file_path: str) -> str:
    reader = PdfReader(file_path)

    pages = []

    for page in reader.pages:
        text = page.extract_text(
            extraction_mode="layout"
        )

        if text:
            pages.append(text)

    return "\n\n".join(pages)


def extract_text_from_txt(file_path: str) -> str:
    with open(
        file_path,
        "r",
        encoding="utf-8",
    ) as file:
        return file.read()


def extract_text_from_docx(file_path: str) -> str:
    document = DocxDocument(file_path)

    extracted_text = []

    for paragraph in document.paragraphs:
        text = paragraph.text.strip()

        if text:
            extracted_text.append(text)

    return "\n".join(extracted_text)


def extract_text(
    file_path: str,
    file_type: str,
) -> str:

    extension = Path(
        file_path
    ).suffix.lower()

    if extension == ".pdf":
        return extract_text_from_pdf(
            file_path
        )

    if extension == ".txt":
        return extract_text_from_txt(
            file_path
        )

    if extension == ".docx":
        return extract_text_from_docx(
            file_path
        )

    raise ValueError(
        f"Unsupported file type: {file_type}"
    )