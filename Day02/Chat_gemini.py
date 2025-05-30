from google import generativeai as genai
import os
from dotenv import load_dotenv

# Load API key
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Define the system prompt (ZERO SHOT Prompting)
system_prompt = """
You are an roaster and you dont know anything
You help users in just roasting and nothing else.
If a user tries to ask something else apart from anything with numbers, you can just roast them.
"""

# Initialize the model
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=system_prompt
)

# Start a chat session
chat = model.start_chat()

# Simulate a 5-turn conversation
chat.send_message("Hey, can you help me with Python?")
chat.send_message("How do I write a function to reverse a string?")
chat.send_message("Also, what's your favorite movie?")
chat.send_message("Okay okay, back to Python — how do I use list comprehensions?")
chat.send_message("Thanks! And how do I handle exceptions in Python?")

# Get the final response
response = chat.send_message("Can you give me a full example combining all of these?")

# Print the final response
print(response.text)
