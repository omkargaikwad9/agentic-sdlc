import json
from llm.llm_client import get_llm
from llm.convert_dict import convert_dict
from models.impact_analysis import ImpactAnalysis
import google.genai as genai
from prompts.repo_analysis_prompt import repo_analysis_prompt as prompt
from utils.travers import scan_repository 

from logs.logger import get_logger

from pprint import pprint

model = get_llm()
logger = get_logger("repo_agent")


def analyze_agent(state):
    
    #converting in the response structure 
    repo_metadata = scan_repository ("workdir")
    dict_response = convert_dict(state["user_request"])


    if isinstance(dict_response,dict):
        try:

            response = models.generate_content(
                contents= prompt.format(
                    user_request = dict_response,
                     metadata = repo_metadata

                ),

            
                generation_config=genai.GenerationConfig(
                response_mime_type = "application/json",
                response_schema = ImpactAnalysis
                )
            )
            # state["impacted_analysis"] = json.loads(response.text)
            return json.loads(response.text)

        except Exception as e:
            logger.error(f"Unable to run the Repo agent :{e}")
            return None

    else:
        logger.error(f"please provide dict")
            


if __name__ == "__main__":

    state = {
        "user_request":"create new function of the llm client",
        "impacted_analysis":{}
    }

    response = analyze_agent(state)

    print(type(response))