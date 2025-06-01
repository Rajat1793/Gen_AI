from google import generativeai as genai
import os
from dotenv import load_dotenv
import requests
import json
import subprocess
import logging

# Load API key
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Set up logging
logging.basicConfig(filename='command_execution.log', level=logging.INFO, format='%(asctime)s - %(message)s')

# Define a whitelist of safe commands
SAFE_COMMANDS = ['pip install', 'npx create-react-app', 'ls', 'echo']

def sanitize_command(command: str):
    for safe_command in SAFE_COMMANDS:
        if command.startswith(safe_command):
            return True
    return False

def run_command(command: str):
    if not sanitize_command(command):
        raise ValueError("Unsafe command detected!")
    result = os.system(command)
    return result

# def create_react_app(project_name:str):
#     result = subprocess.run(f"npx create-react-app {project_name} --yes", shell=True)
#     logging.info(f"Output: {result.stdout}")
#     if result.stderr:
#         logging.error(f"Error: {result.stderr}")
#     return result.stdout, result.stderr

def create_react_app(project_name, use_bootstrap=False, style=None):
    try:
        result = subprocess.run(f"npx create-react-app {project_name} --yes", shell=True, capture_output=True, text=True)
        logging.info(f"Output: {result.stdout}")
        if result.stderr:
            logging.error(f"Error: {result.stderr}")
            return result.stdout, result.stderr

        os.chdir(project_name)

        if use_bootstrap:
            result = subprocess.run("npm install bootstrap", shell=True, capture_output=True, text=True)
            logging.info(f"Bootstrap install output: {result.stdout}")
            if result.stderr:
                logging.error(f"Bootstrap install error: {result.stderr}")
                return result.stdout, result.stderr

        if style == "scss":
            result = subprocess.run("npm install node-sass", shell=True, capture_output=True, text=True)
            logging.info(f"SCSS install output: {result.stdout}")
            if result.stderr:
                logging.error(f"SCSS install error: {result.stderr}")
                return result.stdout, result.stderr

        elif style == "tailwind":
            subprocess.run("npm install -D tailwindcss", shell=True, capture_output=True, text=True)
            subprocess.run("npx tailwindcss init", shell=True, capture_output=True, text=True)

            with open("tailwind.config.js", "w") as f:
                f.write("""module.exports = {
  content: ['./src/**/*.{js,jsx,ts,tsx}', './public/index.html'],
  theme: {
    extend: {},
  },
  plugins: [],
}""")

            with open("src/index.css", "w") as f:
                f.write("""@tailwind base; @tailwind components; @tailwind utilities;""")

        if use_bootstrap:
            with open("src/index.js", "a") as f:
                f.write("\nimport 'bootstrap/dist/css/bootstrap.min.css';")

        return "React app created successfully with the specified options.", None
    except Exception as e:
        logging.error(f"Exception: {str(e)}")
        return None, str(e)

            
def get_weather(city: str):
    url = f"https://wttr.in/{city}?format=%C+%t"
    response = requests.get(url, verify=False)

    if response.status_code == 200:
        return f"The weather in {city} is {response.text}."
    
    return "Something went wrong"


available_tools = {
    "get_weather": get_weather,
    "run_command": run_command,
    "create_react_app": create_react_app
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
    - "create_react_app: Takes the project name as a string and ask the user with follow up question on styling and executes the command to create a react app and returns the output after executing it.

    Example:
    User Query: What is the weather of new york?
    Output: {{ "step": "plan", "content": "The user is interseted in weather data of new york" }}
    Output: {{ "step": "plan", "content": "From the available tools I should call get_weather" }}
    Output: {{ "step": "action", "function": "get_weather", "input": "new york" }}
    Output: {{ "step": "observe", "output": "12 Degree Cel" }}
    Output: {{ "step": "output", "content": "The weather for new york seems to be 12 degrees." }}
    
    Example:
    User Query: Create a React app named 'myapp'.
    Output: { "step": "plan", "content": "User wants to create a React app named 'myapp'" }
    Output: { "step": "plan", "content": "I should ask the user about styling preferences" }
    Output: { "step": "action", "function": "create_react_app", "input": "myapp" }
    Output: { "step": "observe", "output": "React app 'myapp' is created. Do you want to add Bootstrap, SCSS, or Tailwind for styling?" }
    Output: { "step": "output", "content": "React app 'myapp' is created. Do you want to add Bootstrap, SCSS, or Tailwind for styling?" }

"""

# Initialize the model
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
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
            cleaned_text = raw_text.replace("```json", "").replace("```", "").strip()

            # Split multiple JSON blocks if present
            json_blocks = [block.strip() + "}" for block in cleaned_text.split("}") if block.strip()]
            
            for block in json_blocks:
                try:
                    parsed_response = json.loads(block)
                except json.JSONDecodeError:
                    print("❌ Invalid JSON block:", block)
                    continue

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
                        output = tool_function(**tool_input) if isinstance(tool_input, dict) else tool_function(tool_input)
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

            break  # Exit after processing all blocks

        except Exception as e:
            print("❌ Error processing response:", str(e))
            break
