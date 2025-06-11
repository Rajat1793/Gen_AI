from fastapi import FastAPI, Query
from .queued.connection_gemini import queue
from .queued.worker_gemini import process_query
app = FastAPI()

@app.get("/")
def root():
    return{ "status": "Server is up and running"}

@app.post("/chat")
def chat(
    query: str = Query (... , description='Chat Message')
):
    # user query ko queue mai dalna hai
    # user notified job received
    job = queue.enqueue(process_query, query)
    return {"status": "queued", "job_id": job.id}
