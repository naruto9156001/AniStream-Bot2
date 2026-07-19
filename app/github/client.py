import os
import base64
import requests

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_OWNER = os.getenv("GITHUB_OWNER")
GITHUB_REPO = os.getenv("GITHUB_REPO")
GITHUB_BRANCH = os.getenv("GITHUB_BRANCH", "main")

if not GITHUB_TOKEN:
    raise ValueError("GITHUB_TOKEN not found")

API = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}"

HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28"
}


def upload_file(local_path: str,
                github_path: str,
                message: str = "Upload file"):

    with open(local_path, "rb") as f:
        content = base64.b64encode(f.read()).decode()

    url = f"{API}/contents/{github_path}"

    # Check if file already exists
    sha = None
    r = requests.get(url, headers=HEADERS)

    if r.status_code == 200:
        sha = r.json()["sha"]

    payload = {
        "message": message,
        "content": content,
        "branch": GITHUB_BRANCH
    }

    if sha:
        payload["sha"] = sha

    r = requests.put(
        url,
        headers=HEADERS,
        json=payload,
        timeout=120
    )

    r.raise_for_status()

    return r.json()


def create_folder(folder_name: str):
    """
    GitHub me empty folder nahi banta.
    .gitkeep upload karke folder create karte hain.
    """

    import tempfile

    with tempfile.NamedTemporaryFile(delete=False) as f:
        f.write(b"")
        temp = f.name

    return upload_file(
        temp,
        f"{folder_name}/.gitkeep",
        f"Create {folder_name}"
    )


def repo_info():
    r = requests.get(API, headers=HEADERS, timeout=30)
    r.raise_for_status()
    return r.json()


def list_files(path=""):

    url = f"{API}/contents/{path}"

    r = requests.get(
        url,
        headers=HEADERS,
        timeout=30
    )

    r.raise_for_status()

    return r.json()
