import os
import requests
from dotenv import load_dotenv
# GitHub configuration
load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

if not GITHUB_TOKEN:
    raise EnvironmentError("GITHUB_TOKEN environment variable is required")

headers = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

def fetch_pr_diff(pr_url: str) -> str:
    diff_headers = headers.copy()
    # request diff format
    diff_headers["Accept"] = "application/vnd.github.v3.diff"
    resp = requests.get(pr_url, headers=diff_headers, timeout=30)
    resp.raise_for_status()
    return resp.text

def post_pr_comment(comments_url: str, comment: str) -> None:
    body = {"body": comment}
    resp = requests.post(comments_url, headers=headers, json=body, timeout=30)
    resp.raise_for_status()
