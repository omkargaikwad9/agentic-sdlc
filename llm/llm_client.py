import os
from google import genai
# import google.generativeai as gen_ai
from huggingface_hub import InferenceClient

from pydantic import BaseModel
from typing import Type

#logger
from logs.logger import get_logger

from openai import AzureOpenAI
from dotenv import load_dotenv

load_dotenv()

logger = get_logger("LLm_Client")

hug_client = InferenceClient(
    token=os.getenv("HUGGING_FACE_TOKEN")
)
# def get_llm():


#     #configur with api key

#     gen_ai.configure(
#         api_key = os.getenv("GEMINI_API_KEY")
#     )

#     model = gen_ai.get_model(
#         os.getenv("MODEL")
#     )

#     return model

# class Gemini:
#     def __init__(self):
#         self.api_key  = os.getenv("GEMINI_API_KEY")
#         self.model = os.getenv("MODEL")
#         self.client = genai.Client(
#             api_key = self.api_key
#         )

def get_llm(Text:str = "HI, can you please help me",response_model=None):

    #creating LLM
    # genrating response for the llm 
    client = genai.Client(
        api_key = os.getenv("GEMINI_API_KEY") 
    )

    try:
        
        if client:
            #generating the response from the model
            # response = client.models.generate_content(
            #     model = os.getenv("MODEL"),
            #     contents= Text,
            #     config = {
            #         "response_mime_type":"application/json",
            #         "response_schema":response_model
            #     }
            # )

            # # return response.output_text
            return client

    except Exception as e:
        raise e

client = AzureOpenAI(
        api_key= os.getenv("AZURE_API_KEY"),
        api_version=os.getenv("API_VERSION"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
        )


def get_azure_llm(prompt:str="hi HOw are you!",response_model:Type[BaseModel] = None):

    try:
        response = client.responses.create(
            model = os.getenv("MODEL_NAME"),
            input = prompt,
            text = {
                "format":{
                    "type":"json_schema",
                    "name":response_model.__name__,
                    "schema":response_model.model_json_schema()
                }
            }
        )

        return response_model.model_validate_json(
            response.text
        )

    except Exception as e:
        logger.error(f"LLm not working properly {e}")



if __name__ == "__main__":


    # model = get_llm()

    # response = model.models.generate_content(
    #     model = os.getenv("MODEL"),
    #     contents="hi")

    response = get_azure_llm()

    print(response)
    

