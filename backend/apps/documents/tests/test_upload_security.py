
from io import BytesIO
from zipfile import ZipFile

import pytest
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.documents.validators import validate_resume_file


@pytest.mark.parametrize(
    "filename,content",
    [
        ("resume.exe", b"malicious"),
        ("resume.txt", b"plain text"),
        ("resume.pdf", b"not a real PDF"),
        ("resume.doc", b"not a real DOC"),
        ("resume.docx", b"not a real DOCX"),
    ],
)
def test_rejects_invalid_resume_files(filename, content):
    uploaded_file = SimpleUploadedFile(filename, content)

    with pytest.raises(ValidationError):
        validate_resume_file(uploaded_file)


def test_accepts_pdf_with_valid_signature():
    uploaded_file = SimpleUploadedFile(
        "resume.pdf",
        b"%PDF-1.7\nsample PDF content",
    )

    validate_resume_file(uploaded_file)


def test_accepts_doc_with_valid_signature():
    uploaded_file = SimpleUploadedFile(
        "resume.doc",
        bytes.fromhex("D0CF11E0A1B11AE1") + b"sample DOC content",
    )

    validate_resume_file(uploaded_file)



def test_accepts_valid_docx_archive():
    buffer = BytesIO()

    with ZipFile(buffer, "w") as archive:
        archive.writestr(
            "[Content_Types].xml",
            """<?xml version="1.0" encoding="UTF-8"?>
            <Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
                <Default Extension="xml" ContentType="application/xml"/>
            </Types>""",
        )

        archive.writestr(
            "word/document.xml",
            """<?xml version="1.0" encoding="UTF-8"?>
            <document>Resume content</document>""",
        )

    uploaded_file = SimpleUploadedFile(
        "resume.docx",
        buffer.getvalue(),
    )

    validate_resume_file(uploaded_file)
