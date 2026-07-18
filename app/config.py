import os
from dotenv import load_dotenv

# Load .env
load_dotenv()

# =========================
# Project Information
# =========================

APP_NAME = "AnimeSalt Backend"
APP_VERSION = "1.0.0"

# =========================
# MongoDB
# =========================

MONGODB_URI = os.getenv("MONGODB_URI")

DATABASE_NAME = os.getenv(
    "DATABASE_NAME",
    "anihub"
)

# Collections

SERIES_COLLECTION = "series"
EPISODES_COLLECTION = "episodes"
PROGRESS_COLLECTION = "progress"

# =========================
# TMDB
# =========================

TMDB_API_KEY = os.getenv("TMDB_API_KEY")

# =========================
# API
# =========================

API_PREFIX = "/api/v1"

# =========================
# Pagination
# =========================

DEFAULT_LIMIT = 20
MAX_LIMIT = 100

# =========================
# Scraper
# =========================

REQUEST_TIMEOUT = 30
USER_AGENT = (
    "AnimeSaltBackend/1.0"
)

# =========================
# Logging
# =========================

LOG_LEVEL = "INFO"
