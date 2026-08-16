from llm.llm_client import get_llm
import google.generativeai as genai
from models.user_request import user_request
model = get_llm()

import json


def convert_dict(request:str):
    """
    convert this request into the 
    {action}
    {description}
    as dict
    """

    prompt = f"""
    you are the great assistant to know about the code 
    {request}
    please check the request and follow the folloint instruntion

    1.check the request
    2. what are action that needed in the request in one word
    3. and the description that need to understand for the agent what to do exactily """

    if isinstance(request, str):
        try:
            #string send to LLM
            response = model.generate_content(
                contents=prompt.format(request = request),
                generation_config=genai.GenerationConfig(
                    response_mime_type = "application/json",
                    response_schema = user_request
                )
            )

            return json.loads(response.text)

        except Exception as e:
            raise e

    return None



if __name__ == "__main__":

    text = "add the table in the database name user"

    response = convert_dict(text)
    print(response)