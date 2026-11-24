
from pathlib import Path
from zipfile import BadZipFile, ZipFile

from django.core.exceptions import ValidationError


MAX_RESUME_SIZE = 5 * 1024 * 1024

ALLOWED_EXTENSIONS = {".pdf", ".doc", ".docx"}

PDF_SIGNATURE = b"%PDF-"
DOC_SIGNATURE = bytes.fromhex("D0CF11E0A1B11AE1")
DOCX_SIGNATURE = b"PK"


def validate_resume_file_content(uploaded_file):
    """Validate the actual content of PDF, DOC and DOCX uploads."""

    extension = Path(uploaded_file.name).suffix.lower()

    try:
        uploaded_file.seek(0)
        header = uploaded_file.read(8)
        uploaded_file.seek(0)

        if extension == ".pdf":
            if not header.startswith(PDF_SIGNATURE):
                raise ValidationError("Invalid PDF file content.")

        elif extension == ".doc":
            if header != DOC_SIGNATURE:
                raise ValidationError("Invalid DOC file content.")

        elif extension == ".docx":
            if not header.startswith(DOCX_SIGNATURE):
                raise ValidationError("Invalid DOCX file content.")

            try:
                with ZipFile(uploaded_file) as archive:
                    required_files = {
                        "[Content_Types].xml",
                        "word/document.xml",
                    }

                    if not required_files.issubset(set(archive.namelist())):
                        raise ValidationError(
                            "Invalid DOCX file structure."
                        )

            except (BadZipFile, OSError):
                raise ValidationError("Invalid DOCX file content.")

        else:
            raise ValidationError("Unsupported resume file format.")

    finally:
        uploaded_file.seek(0)


def validate_resume_file(uploaded_file):
    """Validate extension, size and actual resume file content."""

    extension = Path(uploaded_file.name).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise ValidationError(
            "Only PDF, DOC, and DOCX files are allowed."
        )

    if uploaded_file.size > MAX_RESUME_SIZE:
        raise ValidationError(
            "Resume file size cannot exceed 5 MB."
        )

    validate_resume_file_content(uploaded_file)

def validate_file_size(uploaded_file):
    """Preserve compatibility with historical migrations."""

    if uploaded_file.size > MAX_RESUME_SIZE:
        raise ValidationError(
            "Resume file size cannot exceed 5 MB."
        )
