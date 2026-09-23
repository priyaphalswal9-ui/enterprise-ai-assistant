import re


def clean_text(text: str) -> str:
    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    # Remove excessive spaces while preserving line structure.
    text = re.sub(
        r"[ \t]+",
        " ",
        text,
    )

    # Remove excessive blank lines.
    text = re.sub(
        r"\n{3,}",
        "\n\n",
        text,
    )

    return text.strip()


def chunk_text(
    text: str,
    chunk_size: int = 1600,
    overlap: int = 250,
) -> list[str]:

    text = clean_text(text)

    if not text:
        return []

    lines = [
        line.strip()
        for line in text.split("\n")
        if line.strip()
    ]

    chunks = []
    current_lines = []
    current_length = 0

    def save_chunk():
        if not current_lines:
            return

        chunk = "\n".join(
            current_lines
        ).strip()

        if chunk:
            chunks.append(chunk)

    for line in lines:

        # Detect common question / section boundaries.
        is_new_section = bool(
            re.match(
                r"^(Q\s*\d+|Q\s*\d+\s*[\.\):]|"
                r"QUESTION\s+\d+|"
                r"UNIT\s+[IVX]+|"
                r"SECTION\s+[A-Z])",
                line,
                re.IGNORECASE,
            )
        )

        # If a new question starts, finish the
        # previous question as a complete chunk.
        if (
            is_new_section
            and current_lines
        ):
            save_chunk()

            # Keep a small amount of context,
            # but do not carry the entire previous chunk.
            overlap_lines = []

            overlap_length = 0

            for previous_line in reversed(
                current_lines
            ):
                if (
                    overlap_length
                    + len(previous_line)
                    > overlap
                ):
                    break

                overlap_lines.insert(
                    0,
                    previous_line,
                )

                overlap_length += (
                    len(previous_line) + 1
                )

            current_lines = overlap_lines

            current_length = sum(
                len(item) + 1
                for item in current_lines
            )

        # If the current chunk becomes too large,
        # split at a line boundary rather than
        # cutting the middle of a sentence/equation.
        if (
            current_lines
            and current_length
            + len(line)
            + 1
            > chunk_size
        ):
            save_chunk()

            overlap_lines = []
            overlap_length = 0

            for previous_line in reversed(
                current_lines
            ):
                if (
                    overlap_length
                    + len(previous_line)
                    > overlap
                ):
                    break

                overlap_lines.insert(
                    0,
                    previous_line,
                )

                overlap_length += (
                    len(previous_line) + 1
                )

            current_lines = overlap_lines

            current_length = sum(
                len(item) + 1
                for item in current_lines
            )

        current_lines.append(line)

        current_length += (
            len(line) + 1
        )

    save_chunk()

    return chunks