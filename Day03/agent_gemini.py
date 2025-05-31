from google import generativeai as genai
import os
from dotenv import load_dotenv
import requests
import json

# Load API key
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def run_command(cmd: str):
    result = os.system(cmd)
    return result

def get_weather(city: str):
    url = f"https://wttr.in/{city}?format=%C+%t"
    response = requests.get(url, verify=False)

    if response.status_code == 200:
        return f"The weather in {city} is {response.text}."
    
    return "Something went wrong"


available_tools = {
    "get_weather": get_weather,
    "run_command": run_command
}

SYSTEM_PROMPT = """
You are an helpfull AI Assistant who is specialized in resolving user query.
    You work on start, plan, action, observe mode.

    For the given user query and available tools, plan the step by step execution, based on the planning,
    select the relevant tool from the available tool. and based on the tool selection you perform an action to call the tool.

    Wait for the observation and based on the observation from the tool call resolve the user query.

    Rules:
    - Follow the Output JSON Format.
    - Always perform one step at a time and wait for next input
    - Carefully analyse the user query

    Output JSON Format:
    {{
        "step": "string",
        "content": "string",
        "function": "The name of function if the step is action",
        "input": "The input parameter for the function",
    }}

    Available Tools:
    - "get_weather": Takes a city name as an input and returns the current weather for the city
    - "run_command": Takes linux command as a string and executes the command and returns the output after executing it.

    Example:
    User Query: What is the weather of new york?
    Output: {{ "step": "plan", "content": "The user is interseted in weather data of new york" }}
    Output: {{ "step": "plan", "content": "From the available tools I should call get_weather" }}
    Output: {{ "step": "action", "function": "get_weather", "input": "new york" }}
    Output: {{ "step": "observe", "output": "12 Degree Cel" }}
    Output: {{ "step": "output", "content": "The weather for new york seems to be 12 degrees." }}
"""

# Initialize the model
model = genai.GenerativeModel(
    model_name="gemini-2.0-flash",
    system_instruction=SYSTEM_PROMPT
)

# Start conversation
chat = model.start_chat()
chat.send_message(SYSTEM_PROMPT)


exit_chat = False
print("👋 Welcome to AI World, Type 'exit' to end the chat.\n")
while not exit_chat:
    query = input("> ")
    if query.lower() == "exit":
        print("🤖: Goodbye!")
        exit_chat = True
        break
    
    chat.send_message(query)

    while True:
        response = chat.last.text
        try:
            raw_text = response.strip()
            cleaned_text = raw_text.strip().strip("`").replace("json", "").strip()
            parsed_response = json.loads(cleaned_text)
        except json.JSONDecodeError:
            cleaned_text = cleaned_text.replace("\n", "").replace("'", '"')
            try:
                parsed_response = json.loads(cleaned_text)
            except:
                print("❌ Still invalid JSON:", response)
                break
            
        step = parsed_response.get("step")

        if step == "plan":
            print(f"🧠: {parsed_response.get('content')}")
            chat.send_message("acknowledged")
            continue

        if step == "action":
            tool_name = parsed_response.get("function")
            tool_input = parsed_response.get("input")
            print(f"🛠️: Calling Tool: {tool_name} with input {tool_input}")
            
            if tool_name in available_tools:
                tool_function = available_tools[tool_name]
                output = tool_function(tool_input)  # This should return a string
                print(f"🔍 Tool Output: {output}")
                chat.send_message(json.dumps({ "step": "observe", "output": output }))
                continue
            
            else:
                print(f"❌ Unknown tool: {tool_name}")
                chat.send_message(json.dumps({ "step": "observe", "output": f"Tool '{tool_name}' is not available." }))
                break

        if step == "output":
            print(f"🤖: {parsed_response.get('content')}")
            break
