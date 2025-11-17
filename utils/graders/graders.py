import os
import requests
from typing import Any
from openai import OpenAI # ensure you have openai package installed


'''
# Grade function for a specific grader type
{
    "type": "python",
    "source": "def grade(sample, item):\n    return 1.0",
    "image_tag": "2025-05-08"
}
'''

'''
# Expected structure of 'item' and 'sample' dictionaries:
{
    "choices": [...],
    "output_text": "...",
    "output_json": {},
    "output_tools": [...],
    "output_audio": {}
}
'''

'''
# Input grading context example:
{
    "reference_answer": "...",
    "my_key": {...}
}
'''

"""
# Grade function implementation
def grade(sample: dict[str, Any], item: dict[str, Any]) -> float:
    # your logic here
    return 1.0
"""

# get the API key from environment
api_key = os.environ["OPENAI_API_KEY"]
headers = {"Authorization": f"Bearer {api_key}"}

grading_function = """
from rapidfuzz import fuzz, utils

def grade(sample, item) -> float:
    output_text = sample["output_text"]
    reference_answer = item["reference_answer"]
    return fuzz.WRatio(output_text, reference_answer, processor=utils.default_process) / 100.0
"""

# define a dummy grader for illustration purposes
grader = {
    "type": "python",
    "source": grading_function
}

# validate the grader
payload = {"grader": grader}
response = requests.post(
    "https://api.openai.com/v1/fine_tuning/alpha/graders/validate",
    json=payload,
    headers=headers
)
print(f"The request returned the following HTTP code: {response.status_code}")
print("validate request_id:", response.headers["x-request-id"])
print("validate response:", response.text)

# run the grader with a test reference and sample
payload = {
  "grader": grader,
  "item": {
     "reference_answer": "fuzzy wuzzy had no hair"
  },
  "model_sample": "fuzzy wuzzy was a bear"
}
response = requests.post(
    "https://api.openai.com/v1/fine_tuning/alpha/graders/run",
    json=payload,
    headers=headers
)
print(f"The request returned the following HTTP code: {response.status_code}")
print("run request_id:", response.headers["x-request-id"])
print("run response:", response.text)

client = OpenAI()

instructions = """
You are an expert in categorizing IT support tickets. Given the support
ticket below, categorize the request into one of "Hardware", "Software",
or "Other". Respond with only one of those words.
"""

ticket = "My monitor won't turn on - help!"

response = client.responses.create(
    model="gpt-4.1",
    input=[
        {"role": "developer", "content": instructions},
        {"role": "user", "content": ticket},
    ],
)

payload = {
  "grader": grader,
  "item": {
     "reference_answer": "Hardware"
  },
  "model_sample": response.output_text
}

print(response.output_text)
response = requests.post(
    "https://api.openai.com/v1/fine_tuning/alpha/graders/run",
    json=payload,
    headers=headers
)
print(f"The request returned the following HTTP code: {response.status_code}")
print("run request_id:", response.headers["x-request-id"]) 
print("run response:", response.text)
if response.status_code == 200:
    current_grade = response.json().get("reward")
    print("Grade:", current_grade)  
    if (current_grade is not None) and (current_grade < 0.5):
        print("The model's response was not satisfactory.")
    else:
        print("\n\nThe model's response was satisfactory.\n")
        if current_grade is not None and current_grade >= 0.95:
            print("--No, actually, the model's response was fucking fantastic.\n")