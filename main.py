from fastapi import FastAPI

from webhook.github_webhook import router as github_router


app = FastAPI(
    title="GitHub Webhook Receiver",
    description="Receives GitHub webhook events",
    version="1.0.0"
)

app.include_router(
    github_router,
    prefix="/github",
    tags=["GitHub"]
)