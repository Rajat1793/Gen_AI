from google import generativeai as genai
import os
from dotenv import load_dotenv

# Load API key
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Improved few-shot system prompt
system_prompt = """
You are an AI expert in Python. You only answer Python-related questions.
If someone asks anything else, you roast them humorously.

Here are some examples of how you respond:

User: How to make a Tea?
Assistant: What makes you think i can do that

User: How to write a function in python?
Assistant: def fn_name(x: int) -> int:\n    pass  # Logic of the function

"""

# Initialize the model
model = genai.GenerativeModel(
    model_name="gemini-2.0-flash",
    system_instruction=system_prompt
)

# Start a chat session
chat = model.start_chat()

# Simulate a 5-turn conversation
chat.send_message("Hi, I'm Rajat")
chat.send_message("Help me how to make tea without milk?")
response = chat.send_message("Why 75% attendance is necessary in college?")
# response = chat.send_message("How to use lambda functions in Python?")
# chat.send_message("What's the best IDE for Python?")
# response = chat.send_message("How to handle exceptions in Python?")

# Print the final response
print(response.text)
