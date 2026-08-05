import os
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
my_api_key = os.getenv("GROQ_API_KEY")

if not my_api_key:
    raise ValueError("API key not found.")

client = Groq(api_key=my_api_key)

model="llama-3.3-70b-versatile"

def llm_ans(prompt):
    message = {
        "role": "user",
        "content": prompt
    }
    messages = [message]
    response = client.chat.completions.create(model=model, messages=messages)
    answer = response.choices[0].message.content
    return answer

bad_prompt = """
#ROLE:
You are a support assistant at a mobile/laptop company
#TASK
You have to classify the issue in a category.
#CONSTRAINTS
- You should only classify the issue in a category.
- the category should be one of the following: billing, technical, account, return

#OUTPUT FORMAT
- The output should be a single word representing the category in the constraints.
#EXAMPLE (one shot)
For example, if the user complaint is "I was charged twice for my last purchase", the output should be:
billing
for example, if the user complaint is "I can't log into my account", the output should be:
account
for example, if the user complaint is "I want to return my laptop", the output should be:
return

#FALLBACK
If the user complaint does not fall into any of the above categories mentioned in the constraints, then the output should be OTHERS.

This is user complaint:
I have an exam tomorrow.
"""

print(llm_ans(bad_prompt))
