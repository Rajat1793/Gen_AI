from .server_gemini import app
# from .server_openai import app
import uvicorn
from dotenv import load_dotenv

load_dotenv()

def main():
    uvicorn.run(app, port=8000, host="0.0.0.0")

main()