'''
# Lists:
from typing import List
# Entity discovery, shows how model "understands" structured data:
from pydantic import BaseModel
# OpenAI client:
from openai import OpenAI
'''

'''
class EntitiesModel(BaseModel):
    attributes: List[str]
    colors: List[str]
    animals: List[str]
'''

def stream(thisOS: object) -> str:

    '''
    Streaming mode implementation using OpenAI's streaming capabilities.
    This function demonstrates how to handle streaming responses from the API.
    '''

    # Example of streaming with structured output:
    '''
    with thisOS.client.responses.stream(
        model=thisOS.model,
        input=[
            {"role": "system", "content": "Extract entities from the input text"},
            {
                "role": "user",
                "content": "The quick brown fox jumps over the lazy dog with piercing blue eyes",
            }
        ],
        text_format=EntitiesModel,
    ) as stream:
        for event in stream:
            if event.type == "response.refusal.delta":
                print(event.delta, end="")
            elif event.type == "response.output_text.delta":
                print(event.delta, end="")
            elif event.type == "response.error":
                print(event.error, end="")
            elif event.type == "response.completed":
                print("Completed")
                # print(event.response.output)
    final_response = stream.get_final_response()
    return final_response
    '''