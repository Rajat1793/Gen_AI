from google import genai

client = genai.Client(api_key="Your Key")

result = client.models.embed_content(
        model="gemini-embedding-exp-03-07",
        contents="Lego Castle")

print(result.embeddings)