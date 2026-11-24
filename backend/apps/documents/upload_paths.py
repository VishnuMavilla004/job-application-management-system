
from pathlib import Path
from uuid import uuid4


def resume_upload_path(instance, filename):
    extension = Path(filename).suffix.lower()

    return (
        f"resumes/user_{instance.user_id}/"
        f"{uuid4().hex}{extension}"
    )
