from google import generativeai as genai
import os
from dotenv import load_dotenv
import json
import re

# Load API key
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# System prompt for Chain-of-Thought reasoning
SYSTEM_PROMPT = """
You are a helpful AI assistant who solves user queries by breaking them down into logical steps.

For every input, return one of the following steps at a time:
- analyse
- think
- validate
- think
- validate
- output
- validate
- result

Each step must be returned in strict JSON format:
{ "step": "string", "content": "string" }

Only return one step per response. Wait for the next input before continuing.

Example:
Input: What is 2 + 2
Output: { "step": "analyse", "content": "The user is asking a basic arithmetic question." }

Example:
Input: What is 2 + 2 * 5 / 3
    Output: { "step": "analyse", "content": "Alight! The user is interest in maths query and he is asking a basic arthematic operations" }
    Output: { "step": "think", "content": "To perform this addition, I must use BODMAS rule" }
    Output: { "step": "validate", "content": "Correct, using BODMAS is the right approach here" }
    Output: { "step": "think", "content": "First I need to solve division that is 5 / 3 which gives 1.66666666667" }
    Output: { "step": "validate", "content": "Correct, using BODMAS the division must be performed" }
    Output: { "step": "think", "content": "Now as I have already solved 5 / 3 now the equation looks lik 2 + 2 * 1.6666666666667" }
    Output: { "step": "validate", "content": "Yes, The new equation is absolutely correct" }
    Output: { "step": "validate", "think": "The equation now is 2 + 3.33333333333" }
    and so on.....

"""

# Initialize the model
model = genai.GenerativeModel(
    model_name="gemini-2.0-flash",
    system_instruction=SYSTEM_PROMPT
)

# Start a chat session
chat = model.start_chat()

# Get user input
query = input("> ")
chat.send_message(query)

while True:
    response = chat.send_message("continue")

    # Clean and parse the JSON response
    try:
        raw_text = response.text.strip()
        cleaned_text = raw_text.strip().strip("`").replace("json", "").strip()
        parsed = json.loads(cleaned_text)
    except json.JSONDecodeError:
        print("⚠️ Could not parse response as JSON:\n", response.text)
        break

    step = parsed.get("step")
    content = parsed.get("content")

    if step == "result":
        print("🤖 Final Result:", content)
        break
    else:
        print(f"  🧠  [{step.upper()}]: {content}")
