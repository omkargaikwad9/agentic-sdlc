from utils.travers import scan_repository, get_project_metadata
from llm.groq_llm_client import GroqLLMClient , get_llm
from prompts.repo_analysis_prompt import repo_prompt
from graph.graph import build_graph
from langchain_core.messages import HumanMessage

from dotenv import load_dotenv
load_dotenv()

groq_client = GroqLLMClient()
llm = get_llm()



def run_agent(
        repository_path: str,
        issue_number:int,
        issue_title: str,
        issue_body: str
):

    graph = build_graph(repository_path)
    # metadata = get_project_metadata(repository_path)

    # repsoitory_structure = scan_repository(repository_path)

    initial_state = {
    "messages": [
        HumanMessage(content=repo_prompt)
    ],
    "repository_path": repository_path,
    "issue_number": issue_number,
    "issue_title": issue_title,
    "issue_body": issue_body,
    }


    result = graph.invoke(
        initial_state
        )
    


    return result



if __name__ == "__main__":

    result = run_agent(
        repository_path=".",
        issue_number= 25,

        issue_title="Add login API",

        issue_body="""
Create a POST /login endpoint.

The endpoint should accept a username
and password and authenticate the user
using the existing authentication service.

Add appropriate tests.
""",
    )

    print("\n\n========== FINAL AGENT RESPONSE ==========\n")

    final_message = result["messages"][-1]

    print(final_message.content)