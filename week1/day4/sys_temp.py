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
prompt="Suggest a good name for my new clothing company."


#SYSTEM
message_system = {
    "role": "system",
    "content": "you are my brand manager who suggests name for my new company. Suggest only one name and give a one line answer"
}


message= {
    "role": role,
    "content": prompt
}


messages = [message_system, message]
#Temperature by default is 0 means safe
response = client.chat.completions.create(model=model, messages=messages, temperature=2)
#print(response)

print("##########################################################################")

answers = response.choices[0].message.content
print(answers)