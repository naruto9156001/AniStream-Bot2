import json
import tempfile
from datetime import datetime

from app.github.client import upload_file


def upload_manifest(
    anime_slug: str,
    episode: int,
    quality: str,
    language: str,
    chunks: list
):

    manifest = {
        "version": "1.0",
        "anime_slug": anime_slug,
        "episode": episode,
        "quality": quality,
        "language": language,
        "created_at": datetime.utcnow().isoformat(),
        "total_chunks": len(chunks),
        "total_size": sum(
            c["size"] for c in chunks
        ),
        "chunks": chunks
    }

    temp = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".json",
        mode="w",
        encoding="utf-8"
    )

    json.dump(
        manifest,
        temp,
        indent=4,
        ensure_ascii=False
    )

    temp.close()

    github_path = (
        f"{anime_slug}/"
        f"{episode}/"
        f"{quality}/"
        f"{language}/manifest.json"
    )

    upload_file(
        temp.name,
        github_path,
        f"{anime_slug} Episode {episode} Manifest"
    )

    return manifest
