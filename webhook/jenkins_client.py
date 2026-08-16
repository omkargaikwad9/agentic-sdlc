import os
import requests

from dotenv import load_dotenv
load_dotenv()

JENKINS_URL = os.getenv("JENKINS_URL")
JENKINS_USER = os.getenv("JENKINS_USER")
JENKINS_API_TOKEN = os.getenv("JENKINS_API_TOKEN")
JENKINS_JOB = os.getenv("JENKINS_JOB")



def trigger_jenkins_job(issue_number, issue_title, repository, issue_body,repository_url):

    """
    Trigger a Jenkins job with the provided issue details.

    Args:
        issue_number (int): The number of the GitHub issue.
        issue_title (str): The title of the GitHub issue.
        repository (str): The repository name where the issue was created.
        issue_body (str): The body content of the GitHub issue.

    Returns:
        bool: True if the job was triggered successfully, False otherwise.
    """

    jenkins_url = f"{JENKINS_URL}/job/{JENKINS_JOB}/buildWithParameters"

    params = {
        "ISSUE_NUMBER": issue_number,
        "ISSUE_TITLE": issue_title,
        "REPOSITORY": repository,
        "ISSUE_BODY": issue_body,
        "REPOSITORY_URL": repository_url
    }
    response = requests.post(jenkins_url, params=params, auth=(JENKINS_USER, JENKINS_API_TOKEN))
    
    response.raise_for_status()  # Raise an error for bad responses

    return{
        "status_code": response.status_code,
        "message": "Jenkins job triggered successfully"
    }