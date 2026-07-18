from pymongo import MongoClient
from pymongo.server_api import ServerApi
from app.config import (
    MONGODB_URI,
    DATABASE_NAME,
    SERIES_COLLECTION,
    EPISODES_COLLECTION,
    PROGRESS_COLLECTION
)

if not MONGODB_URI:
    raise ValueError(
        "MONGODB_URI not found in environment variables."
    )

client = MongoClient(
    MONGODB_URI,
    server_api=ServerApi("1")
)

db = client[DATABASE_NAME]

series = db[SERIES_COLLECTION]
episodes = db[EPISODES_COLLECTION]
progress = db[PROGRESS_COLLECTION]


def init_database():
    """
    Create indexes if they don't exist.
    Safe to call every startup.
    """

    series.create_index(
        "slug",
        unique=True
    )

    episodes.create_index(
        [
            ("anime_slug", 1),
            ("episode", 1)
        ],
        unique=True
    )

    episodes.create_index("episode_id")

    progress.create_index(
        "anime_slug",
        unique=True
    )

    print("✅ MongoDB Connected")
