import os
import logging
import requests
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

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
    """Fetch the diff for a pull request."""
    diff_headers = get_github_headers(token)
    # request diff format
    diff_headers["Accept"] = "application/vnd.github.v3.diff"
    
    logger.info(f"Fetching PR diff from URL: {pr_url}")
    try:
        resp = requests.get(pr_url, headers=diff_headers, timeout=30)
        resp.raise_for_status()
        return resp.text
    except requests.exceptions.Timeout:
        logger.error(f"Timeout fetching PR diff from {pr_url}")
        raise
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Connection error fetching PR diff from {pr_url}: {str(e)}")
        raise
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error fetching PR diff: {resp.status_code} - {resp.text}")
        raise

def post_pr_comment(comments_url: str, comment: str, token: str = None) -> None:
    """Post a comment to a pull request."""
    headers = get_github_headers(token)
    body = {"body": comment}
    
    logger.info(f"Posting comment to URL: {comments_url}")
    try:
        resp = requests.post(comments_url, headers=headers, json=body, timeout=30)
        resp.raise_for_status()
    except requests.exceptions.Timeout:
        logger.error(f"Timeout posting comment to {comments_url}")
        raise
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Connection error posting comment to {comments_url}: {str(e)}")
        raise
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error posting comment: {resp.status_code} - {resp.text}")
        raise
