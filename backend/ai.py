import os
import logging
from openai import AzureOpenAI
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Azure OpenAI configuration
load_dotenv()
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")

logger.info(f"Azure OpenAI Endpoint configured: {bool(AZURE_OPENAI_ENDPOINT)}")
logger.info(f"Azure OpenAI API Key configured: {bool(AZURE_OPENAI_API_KEY)}")

if not AZURE_OPENAI_ENDPOINT:
    error_msg = "AZURE_OPENAI_ENDPOINT environment variable is required"
    logger.error(error_msg)
    raise EnvironmentError(error_msg)
if not AZURE_OPENAI_API_KEY:
    error_msg = "AZURE_OPENAI_API_KEY environment variable is required"
    logger.error(error_msg)
    raise EnvironmentError(error_msg)

try:
    # Initialize Azure OpenAI client
    client = AzureOpenAI(
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
        api_key=AZURE_OPENAI_API_KEY,
        api_version=AZURE_OPENAI_API_VERSION
    )
    logger.info("Azure OpenAI client initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Azure OpenAI client: {str(e)}")
    raise

SYSTEM_PROMPT = """You are an expert senior software engineer. Given a git diff for a pull request,
produce a clear, structured code review covering:
1) Summary of changes
2) High priority issues (bugs, security)
3) Code-style / maintainability suggestions
4) Performance concerns
5) Small concrete suggested fixes or code examples
6) A short checklist for the author with details"""

def generate_review(diff: str, pr_payload: dict = None) -> str:
    # Build a concise prompt that includes PR title + body if available
    pr_title = ""
    pr_body = ""
    if pr_payload:
        pr = pr_payload.get("pull_request", {})
        pr_title = pr.get("title", "")
        pr_body = pr.get("body", "")

    user_prompt = f"""PR Title: {pr_title}
PR Body: {pr_body}

Diff:
{diff}

Provide the review as markdown, with headings and bullet points."""

    try:
        logger.info(f"Generating review using model: {os.getenv('AZURE_OPENAI_MODEL', 'gpt-4o-mini')}")
        response = client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_MODEL", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=1200,
            temperature=0.1
        )
        logger.info("Review generated successfully")
        # Azure OpenAI client returns choices with message content
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Failed to generate review: {str(e)}", exc_info=True)
        raise
