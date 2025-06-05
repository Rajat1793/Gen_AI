import tiktoken

enc = tiktoken.encoding_for_model("gpt-4o")
text = "Lego Castle"

tokens = enc.encode(text)
print(f"Text: {text}")
print(f"Tokens: {tokens}")
print(f"Number of tokens: {len(tokens)}")
# Decoding the tokens back to text
decoded_text = enc.decode(tokens)
print(f"Decoded text: {decoded_text}")

