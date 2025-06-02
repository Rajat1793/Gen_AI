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


available_tools = {
    "run_command": run_command,
    "create_folder": create_folder,
    "write_file": write_file,
    "run_server": run_server,
}

SYSTEM_PROMPT = """
You are an AI developer assistant. When returning JSON that includes code (especially in the 'content' field), 
ensure all strings are properly escaped. Use \\n for newlines and \\" for quotes inside strings. 
Wrap the entire JSON block in triple backticks with 'json' for clarity.

---
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

Follow the steps as described below and there should be just one follow up question from the user

1. Think
    - Think about the request
    - Break the task into sub parts for easy and fast processing
    - Point out how you will perform the task in points before processing

2. Perform_task
    - Use the tools listed to perform the task
    - Provide the exact command to the tool as it will be check if command is safe to run or not

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

Always respond using **valid JSON** in this format:

```json
{
  "step": "think" | "perform_task" | "analyse" | "repeat" | "Output",
  "content": "appropriate reasons of what is been done",
  "tool": "tool_name",          // only if any tool been used in perform_task step
  "input": "tool input here"    // only if any tool been used in perform_task step
}
```
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

# Initialize the model
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=SYSTEM_PROMPT,
    generation_config={
        "temperature": 0.5 # You can adjust this value (0.0 to 1.0+)
}

)

# Start conversation
chat = model.start_chat()
chat.send_message(SYSTEM_PROMPT)


exit_chat = False
print("👋 Welcome to AI World, Type 'exit' to end the chat.\n")
print("I can create any Full-Stack App, I'm still learning so might go wrong as well...")
while not exit_chat:
    query = input("\n User > ")
    if query.lower() == "exit":
        print("🤖: Goodbye!")
        exit_chat = True
        break
    
    chat.send_message(query)

    while True:
        response = chat.last.text
        try:
            raw_text = response.strip()

            # Try to parse the response as a single JSON object
            parsed_response = json.loads(raw_text)

            step = parsed_response.get("step")

            if step == "think":
                print(f"🧠: {parsed_response.get('content')}")
                chat.send_message("acknowledged")

            elif step == "perform_task":
                tool_name = parsed_response.get("tool")
                tool_input = parsed_response.get("input")
                print(f"🛠️: Calling Tool: {tool_name} with input {tool_input}")

                if tool_name in available_tools:
                    tool_function = available_tools[tool_name]
                    output = tool_function(**tool_input) if isinstance(tool_input, dict) else tool_function(tool_input)
                    print(f"🔍 Tool Output: {output}")
                    chat.send_message(json.dumps({ "step": "observe", "output": output }))
                else:
                    print(f"❌ Unknown tool: {tool_name}")
                    chat.send_message(json.dumps({ "step": "observe", "output": f"Tool '{tool_name}' is not available." }))

            elif step == "analyse":
                print(f"👁️ Analysis: {parsed_response.get('content')}")

            elif step == "output":
                print(f"🤖 Output: {parsed_response.get('content')}")
                while True:
                    follow_up = input("🛠️ Do you want to make any more changes? (yes/no): ").strip().lower()
                    if follow_up in ["no", "n", "i'm okay", "i am okay", "done", "finished", "exit"]:
                        print("🎉 Project finalized. Exiting.")
                        exit_chat = True
                        break
                    elif follow_up in ["yes", "y", "sure", "okay", "ok"]:
                        print("🔁 Okay, what else would you like to modify or add?")
                        next_change = input("📬 User > ").strip()
                        chat.send_message(next_change)
                        break
                    else:
                        print("❓ Please answer 'yes' or 'no'.")
            else:
                print(f"❓ Unknown step: {step}")
        except Exception as e:
            print("❌ Error processing response:", str(e))
