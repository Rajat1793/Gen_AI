# Generative AI
# Day 1: Intoduction to Generative AI
Welcome to Day 1 of our journey into Generative AI! This session covers foundational concepts that power large language models (LLMs) and other generative systems.

## Topics Covered
### 🔹 Tokenization
Breaking down text into smaller units (tokens) such as words, subwords, or characters to prepare it for processing by AI models.

### 🔹 Vector Embedding
Transforming tokens into numerical vectors that capture semantic meaning, enabling models to understand relationships between words.

### 🔹 Positional Encoding
Adding information about the position of tokens in a sequence, allowing models to understand word order in input data.

### 🔹 Self-Attention (Single Head Attention)
A mechanism that allows the model to weigh the importance of different words in a sequence when encoding a particular word.

### 🔹 Multi-Head Attention
An extension of self-attention that uses multiple attention heads to capture different types of relationships between words simultaneously.

## 🧠 Two Phases of LLMs

### 1. Training
- Involves feeding large datasets into the model.
- Uses **backpropagation** to adjust weights and improve accuracy.
- The goal is to learn language patterns and representations.

### 2. Inference
- The model is used to generate predictions or outputs.
- No learning occurs; it applies what was learned during training.

---

# Day 2: Hello World

## Topics Covered
### 🔹 GIGO (Garbage In, Garbage Out): 
The quality of AI output depends entirely on the quality of your input.

### 🔹 Prompting Technique: 
The way you interact with AI determines how well it understands and responds.

### 🔹 Prompting Styles:
#### Alpaca Prompt: 
    A simple instruction-based format used to guide the AI clearly.
#### ChatML: 
    A chat-style format using roles like system, user, and assistant for structured conversations.
#### INST Format: 
    A structured prompt format with labeled sections like Instruction, Input, and Response.

### 🔹 System Prompting Techniques:
#### Zero-Shot Prompting: 
    Ask the AI a task directly without giving any examples.
#### Few-Shot Prompting: 
    Provide a few examples before asking the AI to generate a similar response.
#### Chain-of-Thought (CoT) Prompting: 
    Encourage the AI to explain its reasoning step-by-step.
#### Self-Consistency Prompting:
    Run multiple reasoning paths and choose the most consistent answer.
#### Persona-Based Prompting: 
    Guide the AI with a specific personality or role using few-shot examples.

---