from dotenv import load_dotenv
from datetime import datetime
import google.generativeai as genai
import json, os, re, subprocess
import requests

load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.0-flash-lite")

SAFE_COMMANDS = ['pip install', 'npx create-react-app', 'ls', 'echo','npm start','npm start', 'cd', 'npm install','npm run build']

def sanitize_command(command: str):
    for safe_command in SAFE_COMMANDS:
        if command.startswith(safe_command):
            return True
    return False

def run_command(command):
    try:
        if not sanitize_command(command):
            raise ValueError("Unsafe command detected!")
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.stdout + result.stderr
    except Exception as e:
        return f"Command failed: {e}"

def create_folder(folder_name):
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
        return f"Folder '{folder_name}' created successfully."
    else:
        return f"Folder '{folder_name}' already exists."

def write_file(data):
    try:
        if isinstance(data, dict):
            path = data.get("path")
            content = data.get("content")
            if not path or not content:
                return "Invalid input: 'path' and 'content' are required."
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            return f"File written: {path}"
        else:
            return "Input must be a dictionary with 'path' and 'content'."
    except Exception as e:
        return f"Error writing file: {e}"
    
def run_server(command):
    try:
        subprocess.Popen(command, shell=True)
        return f"Server started with: {command}"
    except Exception as e:
        return f"Error starting server: {e}"
    
def extract_json_objects(text):
    json_objects = re.findall(r'\{.*?\}', text, re.DOTALL)
    return [json.loads(obj) for obj in json_objects if obj.strip().startswith('{')]

available_tools = {
    "run_command": run_command,
    "create_folder": create_folder,
    "write_file": write_file,
    "run_server": run_server,
}


SYSTEM_PROMPT = """
You are a helpful AI Assistant who is specialized in resolving user queries.
You are an AI developer assistant. Your main task is to generate the code for any tool user has asked to create and in which programming language is been told to make it in
You should always return the out of any step in pure json format

Objective:
    Build or rewite the existing application based on the existing tools just by using the terminal. User can provide the context in multiple language like english, hindi or combination of both.
    Example:
        - Create a todo app in React
        - Create a full stack weather project
        - Add login and logout functionality to TODO app

Steps to be followed:
    - Create folders/files
    - Write logic code into the files and folder created
    - Install all the dependencies using the run command
    - Modify the existing code based on requirements
    - Once done also start the sever for hosting
    - Support follow up question from user 

---

Chain of Thought (COT):

Follow the steps as described below and there should be just one follow up question at a time from the user

1. Think
    - Think about the request
    - Break the task into sub parts for easy and fast processing
    - Point out how you will perform the task in points before processing

2. Perform_task
    - Use the tools listed to perform the task
    - Provide the exact command to the tool as it will be check if command is safe to run or not
    - Perform just task at a time

3. Analyse
    - Analyse all the previous steps taken 
    - Make necessary changes if its required
    - Apologies the user with message i'm still learning please apologize me if something goes wrong

4. Repeat
    - Keep repeating the steps untill task is completed

5. Output
    - Check if the app is successfully build or task is completed
    - Summary of all steps taken
    - Check if user has more requirements

---

Tools Available to perform the task

Use the below tools in `Perform_task` step only:

- `run_command(command: str)` -> Run terminal commands (eg: 'pip install', 'npx create-react-app', 'ls', 'echo')
- `create_folder(path: str)` -> Create folders or directories
- `write_file({ path: str, content: str })` -> Write code into files
- `run_server(command: str)` -> Start dev servers (eg: 'npm start')

---

Changes to existing code:

If a user asks to make changes to a specific part of a project:

1. Use `run_command("ls")` to list files/directories.
2. `cd` into the relevant folder.
3. Read and understand the target files.
4. Use `write_file` to update or add new files.
5. Re-run the server to verify changes.

---

Output format:
Strictly respond using **valid JSON** in below format no other format is accepted

{
  "step": "think" | "perform_task" | "analyse" | "repeat" | "Output",
  "content": "appropriate reasons of what is been done",
  "tool": "tool_name",          // only if any tool been used in perform_task step
  "input": "tool input here"    // only if any tool been used in perform_task step
}

---

Eamples:
 
User: Create a todo app in React
agent: {
  "step": "think",
  "content": "To create a todo app in React, I need to set up a new React project, add a TodoList component, and run the dev server."
}
agent: {
  "step": "perform_task",
  "tool": "run_command",
  "input": "npx create-react-app todo-app"
}
agent: {
  "step": "analyse",
  "content": "React app successfully."
}
agent:{
  "step": "perform_task",
  "tool": "run_command",
  "input": "cd todo-app && npm install"
}
agent:{
  "step": "perform_task",
  "tool": "write_file",
  "input": {
    "path": "todo-app/src/TodoList.js",
    "content": "import React from 'react';\n\nfunction TodoList() {\n  return <div>Todo List</div>;\n}\n\nexport default TodoList;"
  }
}
agent:{
  "step": "analyse",
  "content": "Component created. Now adding it to App.js."
}

agent:{
  "step": "perform_task",
  "tool": "write_file",
  "input": {
    "path": "todo-app/src/App.js",
    "content": "import React from 'react';\nimport TodoList from './TodoList';\n\nfunction App() {\n  return (\n    <div className=\"App\">\n      <h1>Todo App</h1>\n      <TodoList />\n    </div>\n  );\n}\n\nexport default App;"
  }
}

agent:{
  "step": "perform_task",
  "tool": "run_server",
  "input": "cd todo-app && npm start"
}

agent: {
  "step": "output",
  "content": "React todo app created and running at http://localhost:3000. Want to add more features?"
}

---

Rules:
Never skip any step and perform the task in order ("think" - "perform_task" - "analyse" - "repeat" - "Output")
Use only one tool at a time
Show all steps in planning with reasoning
Before modify the code check if files and folder exist with ls and cd commands
Respond only in valid JSON format—no extra comments or markdown.
Dont assume structure; inspect it first unless creating from scratch.

Summary
Function as a highly capable agent who can:
Start and build full projects
Support iterative feature development
Understand and modify codebases
Keep servers running

"""

messages = [ { "role": "user", "parts": [SYSTEM_PROMPT] } ]

exit_chat = False
while not exit_chat:
    query = input("User > ")
    if query.lower() == "exit":
        print("🤖: Goodbye!")
        exit_chat = True
        break
    
    while True:
        messages.append({ "role": "user", "parts": [query] })

        while True:
            response = model.generate_content(messages)
            if not response.candidates or not response.candidates[0].content.parts:
                print("⚠️ Gemini returned no content.")
                continue

            content = response.candidates[0].content.parts[0].text
            print('Printing the content before pasrsing: ',content)
            try:
                print("🔍 Trying to extract JSON...")
                parsed_responses = extract_json_objects(content)
                print("✅ Successfully parsed JSON.")
            except Exception as e:
                print("❌ Could not parse response as JSON.")
                print("Error:", e)
                break

            for parsed_response in parsed_responses:
                messages.append({ "role": "model", "parts": [json.dumps(parsed_response)] })

                if parsed_response.get("step") == "think":
                    print(f"🧠: {parsed_response.get('content')}")
                    continue

                if parsed_response.get("step") == "perform_task":
                    tool_name = parsed_response.get("tool")
                    tool_input = parsed_response.get("input")

                    print(f"🛠️: Calling Tool: {tool_name} with input {tool_input}")

                    # if tool_name in available_tools:
                    #     output = available_tools
                    #     messages.append({ "role": "user", "parts": [json.dumps({ "step": "analyse", "output": str(output) })] })
                    #     continue
                    if tool_name in available_tools:
                        tool_function = available_tools[tool_name]
                        output = tool_function(**tool_input) if isinstance(tool_input, dict) else tool_function(tool_input)
                        print(f"🔍 Tool Output: {output}")
                        messages.append({ "role": "user", "parts": [json.dumps({ "step": "observe", "output": str(output) })] })
                    else:
                        print(f"❌ Unknown tool: {tool_name}")
                        messages.append({ "role": "user", "parts": [json.dumps({ "step": "observe", "output": f"Tool '{tool_name}' is not available." })] })
                if parsed_response.get("step") == "output":
                    print(f"🤖: {parsed_response.get('content')}")
                    break