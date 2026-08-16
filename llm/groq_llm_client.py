from groq import Groq
from dotenv import load_dotenv
load_dotenv()

from langchain_groq import ChatGroq

import os


class GroqLLMClient:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        self.model_id = os.getenv("GROQ_MODEL_ID")
        self.client = Groq(api_key=self.api_key)


    def generate_response(self, prompt: str,response_model):

        """
        Generate a response from the Groq LLM model.

        Args:
            prompt (str): The input prompt for the model.
            response_model: The expected response model/schema.

        Returns:
            The generated response from the model.
            """

        response = self.client.chat.completions.create(
            model=self.model_id,
            messages=[
                {"role": "user", "content": prompt}
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": response_model.__name__,
                    "schema": response_model.model_json_schema()
                }
            }
        )

        return response.choices[0].message.content


def get_llm():

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise ValueError(
            "GROQ_API_KEY is not configured"
        )

    return ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0,
        api_key=api_key,
    )


if __name__ == "__main__":
    # Example usage
    llm_client = GroqLLMClient()
    from models.user_request import user_request
    prompt = "add a new feature to the project"
    response_model = None  # Replace with your actual response model/schema
    response = llm_client.generate_response(prompt, user_request)
    print(response)