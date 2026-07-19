import os
import math
import tempfile
import hashlib

from app.github.client import upload_file

CHUNK_SIZE = int(os.getenv("CHUNK_SIZE_MB", "5")) * 1024 * 1024


def md5(file_path):
    h = hashlib.md5()

    with open(file_path, "rb") as f:
        while True:
            data = f.read(8192)

            if not data:
                break

            h.update(data)

    return h.hexdigest()


def split_and_upload(
    video_path: str,
    anime_slug: str,
    episode: int,
    quality: str,
    language: str
):

    total_size = os.path.getsize(video_path)

    total_chunks = math.ceil(
        total_size / CHUNK_SIZE
    )

    uploaded = []

    with open(video_path, "rb") as source:

        for chunk in range(total_chunks):

            data = source.read(CHUNK_SIZE)

            temp = tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".chunk"
            )

            temp.write(data)
            temp.close()

            filename = (
                f"{chunk+1:04d}.chunk"
            )

            github_path = (
                f"{anime_slug}/"
                f"{episode}/"
                f"{quality}/"
                f"{language}/"
                f"{filename}"
            )

            upload_file(
                temp.name,
                github_path,
                f"{anime_slug} EP{episode} {filename}"
            )

            uploaded.append(
                {
                    "index": chunk + 1,
                    "file": filename,
                    "size": len(data),
                    "md5": md5(temp.name),
                    "path": github_path
                }
            )

            os.remove(temp.name)

    return {
        "anime": anime_slug,
        "episode": episode,
        "quality": quality,
        "language": language,
        "chunk_size": CHUNK_SIZE,
        "total_chunks": total_chunks,
        "chunks": uploaded
    }
