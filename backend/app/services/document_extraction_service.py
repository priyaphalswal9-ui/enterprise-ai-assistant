from pathlib import Path

from docx import Document
from PyPDF2 import PdfReader


def extract_text(file_path: str, file_type: str) -> str:
    path = Path(file_path)
    extension = path.suffix.lower()

    # PDF
    if extension == ".pdf" or file_type == "application/pdf":
        reader = PdfReader(file_path)

        text_parts = []

        for page in reader.pages:
            page_text = page.extract_text()

            if page_text:
                text_parts.append(page_text)

        return "\n".join(text_parts)

    # DOCX
    if (
        extension == ".docx"
        or file_type
        == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    ):
        document = Document(file_path)

        text_parts = [
            paragraph.text
            for paragraph in document.paragraphs
            if paragraph.text.strip()
        ]

        return "\n".join(text_parts)

    # Plain-text/code files
    text_extensions = {
        ".txt",
        ".csv",
        ".json",
        ".md",
        ".py",
        ".js",
        ".jsx",
        ".ts",
        ".tsx",
        ".html",
        ".css",
        ".r",
        ".java",
        ".cpp",
        ".c",
        ".h",
        ".sql",
        ".xml",
        ".yaml",
        ".yml",
    }

    if extension in text_extensions or file_type.startswith("text/"):
        return path.read_text(
            encoding="utf-8",
            errors="ignore",
        )

    raise ValueError(
        f"Unsupported file type: {file_type}"
    )