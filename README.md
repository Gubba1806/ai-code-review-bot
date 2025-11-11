# AI Code Review Bot

**What**: GitHub bot that auto-reviews Pull Requests using a GPT model.

**Stack**
- Backend: FastAPI (Python)
- AI: Azure OpenAI API (configurable model)
- GitHub API + Actions
- CI/CD: GitHub Actions (invoke external review endpoint)

## Quick start (local)

1. Copy `.env.example` to `.env` and fill `GITHUB_TOKEN` and Azure OpenAI credentials (`AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_KEY`, etc.).
2. Install dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r backend/requirements.txt
   ```
3. Run the server:
   ```bash
   uvicorn backend.main:app --reload --port 8000
   ```
4. Configure a GitHub repository secret `REVIEW_ENDPOINT` with your server URL
   (e.g. `https://your-domain.com/review`). The included GitHub workflow will POST the PR payload to that endpoint.

## Deploy
Build and push the Docker image or deploy to any provider (Render, Railway, Fly.io, AWS ECS, etc).

## Security & Notes
- Use GitHub App or finer-scoped token for production.
- Rate-limit requests to Azure OpenAI and cache large diffs.
- Consider adding owner/whitelist checks so the bot only comments on allowed repos.

## Next steps I can help with
- Make this a GitHub App with installation flow.
- Add inline comment suggestions (needs PR review endpoints).
- Add Redis caching and queueing.
