import os
import sys
import logging
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from github import fetch_pr_diff, post_pr_comment
from ai import generate_review
from dotenv import load_dotenv
import requests

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

load_dotenv()

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    """Verify all required environment variables are set on startup."""
    logger.info("=== Application Startup ===")
    required_vars = {
        "GITHUB_TOKEN": "GitHub API token",
        "AZURE_OPENAI_ENDPOINT": "Azure OpenAI endpoint",
        "AZURE_OPENAI_API_KEY": "Azure OpenAI API key",
    }
    
    missing_vars = []
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            logger.info(f"✓ {var} is configured")
        else:
            logger.error(f"✗ {var} is NOT configured ({description})")
            missing_vars.append(var)
    
    if missing_vars:
        error_msg = f"Missing environment variables: {', '.join(missing_vars)}"
        logger.error(error_msg)
        raise EnvironmentError(error_msg)
    
    logger.info("=== All environment variables configured ===")
    logger.info("Application is ready to handle requests")

@app.get("/health")
async def health_check():
    """Health check endpoint to verify the service is running."""
    return {"status": "healthy", "service": "ai-code-review-bot"}
async def test():
    return {"status": "ok"}
    
@app.post("/review")
async def review_pr(request: Request):
    payload = await request.json()
    # Basic validation
    pr = payload.get("pull_request")
    if not pr:
        raise HTTPException(status_code=400, detail="missing pull_request in payload")

    pr_url = pr.get("url")
    comments_url = pr.get("comments_url")
    github_token = payload.get("github_token")
    
    if not pr_url or not comments_url:
        raise HTTPException(status_code=400, detail="missing pr url or comments_url")
    
    if not github_token:
        raise HTTPException(status_code=400, detail="missing github_token")

    try:
        logger.info(f"Fetching PR diff from: {pr_url}")
        diff = fetch_pr_diff(pr_url, token=github_token)
        
        logger.info("Generating AI review")
        ai_review = generate_review(diff, pr_payload=payload)
        
        logger.info(f"Posting comment to: {comments_url}")
        post_pr_comment(comments_url, ai_review, token=github_token)
        
        logger.info("Review posted successfully")
    except requests.exceptions.Timeout as e:
        logger.error(f"Request timeout: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500, 
            content={"error": f"Request timeout: {str(e)}"}
        )
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Connection error: {str(e)}", exc_info=True)
        logger.error("Check if the backend can reach api.github.com and the Azure OpenAI endpoint")
        return JSONResponse(
            status_code=500, 
            content={"error": f"Connection error: {str(e)}"}
        )
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500, 
            content={"error": f"GitHub API error: {str(e)}"}
        )
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        import traceback
        logger.error(traceback.format_exc())
        return JSONResponse(
            status_code=500, 
            content={"error": f"Error: {str(e)}", "type": type(e).__name__}
        )

    return {"status": "review_posted"}
