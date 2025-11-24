import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from github import fetch_pr_diff, post_pr_comment
from ai import generate_review
from dotenv import load_dotenv
load_dotenv()

app = FastAPI()
@app.post("/")
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
        diff = fetch_pr_diff(pr_url, token=github_token)
        ai_review = generate_review(diff, pr_payload=payload)
        post_pr_comment(comments_url, ai_review, token=github_token)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

    return {"status": "review_posted"}
