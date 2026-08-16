from fastapi import FastAPI, Request, HTTPException, APIRouter
from fastapi.responses import JSONResponse
from typing import Any
from webhook.jenkins_client import trigger_jenkins_job as trigger_jenkins_build

router = APIRouter()


@router.post("/")
async def root():
    return {
        "status": "running",
        "service":"github-webhook-receiver" 
        }


@router.post("/webhook")
async def webhook(request: Request):
    try:
        body = await request.body()
        # print(body)
        payload = await request.json()
        #process the payload as needed
        # print(payload)
        respository = payload.get("repository", {})
        repository_url = respository.get("clone_url")
        # print(respository)
        action = payload.get("action")
        # print(action)

        issue = payload.get("issue", {})
        # print(issue)


        # Only trigger Jenkins when a new issue is created
        if action == "opened":

            result = trigger_jenkins_build(
                issue_number=issue.get("number"),
                issue_title=issue.get("title", ""),
                issue_body=issue.get("body",""),
                repository=respository.get("full_name", ""),
                repository_url=repository_url
            )
            print(result)

            return {
                "status": "received",
                "jenkins": result,
            }

        return {
            "status": "ignored",
            "reason": f"Action '{action}' is not configured to trigger Jenkins",
        }



    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

