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
role="user"



#structure it
from pydantic import BaseModel
class Ticket(BaseModel):
    name: str
    issue: str
    email: str
schema= Ticket.model_json_schema()

response_format = {
    "type": "json_object"
}

system_prompt = f"""
Extract the personal information from the text and strictly follow the given schema and return the output in json format. 
{schema}
""" 
message_system = {
    "role": "system",
    "content": system_prompt
}
text="Hello, my name is Mrudul. I have an iphone which is not working properly. My address is Delhi, India. My email is mrudul@example.com. my phone number is 12345565. I have a bank account in HDFC bank and my account number is 1234567890. Please help me to fix my iphone. my date of birth is 01/01/1990."

prompt=f"""
This is a customer ticket. Please extract the following information from the text:
{text}
"""

message= {
    "role": role,
    "content": prompt
}

messages = [message_system, message]

response = client.chat.completions.create(model=model, messages=messages, response_format=response_format )


answers = response.choices[0].message.content
print(answers)

#isko padhte kasie hai
import json
raw_json = answers
data_file=json.loads(raw_json)
ticket = Ticket(**data_file)

print(ticket.name)
print(ticket.issue)
print(ticket.email)