import os
import requests
from dotenv import load_dotenv
# GitHub configuration
load_dotenv()

def get_github_headers(token: str = None) -> dict:
    """Create GitHub API headers with authentication token."""
    github_token = token or os.getenv("GITHUB_TOKEN")
    
    if not github_token:
        raise EnvironmentError("GITHUB_TOKEN environment variable is required")
    
    return {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json"
    }

def fetch_pr_diff(pr_url: str, token: str = None) -> str:
    diff_headers = get_github_headers(token)
    # request diff format
    diff_headers["Accept"] = "application/vnd.github.v3.diff"
    resp = requests.get(pr_url, headers=diff_headers, timeout=30)
    resp.raise_for_status()
    return resp.text

def post_pr_comment(comments_url: str, comment: str, token: str = None) -> None:
    headers = get_github_headers(token)
    body = {"body": comment}
    resp = requests.post(comments_url, headers=headers, json=body, timeout=30)
    resp.raise_for_status()
