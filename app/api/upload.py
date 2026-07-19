from fastapi import APIRouter, UploadFile, File, Form, HTTPException
import os
import tempfile

from app.github.uploader import split_and_upload
from app.github.manifest import upload_manifest

router = APIRouter(
    prefix="/api/v1/upload",
    tags=["Upload"]
)

@router.post("/")
async def upload_episode(
    file: UploadFile = File(...),
    anime_slug: str = Form(...),
    episode: int = Form(...),
    quality: str = Form(...),
    language: str = Form(...)
):

    suffix = os.path.splitext(file.filename)[1]

    temp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)

    while True:
        chunk = await file.read(1024 * 1024)

        if not chunk:
            break

        temp.write(chunk)

    temp.close()

    try:

        result = split_and_upload(
            temp.name,
            anime_slug,
            episode,
            quality,
            language
        )

        manifest = upload_manifest(
            anime_slug,
            episode,
            quality,
            language,
            result["chunks"]
        )

        return {
            "success": True,
            "manifest": manifest
        }

    except Exception as e:
        raise HTTPException(500, str(e))

    finally:
        os.remove(temp.name)
