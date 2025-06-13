# Generative AI
# Day 1: Intoduction to Generative AI
Welcome to Day 1 of our journey into Generative AI! This session covers foundational concepts that power large language models (LLMs) and other generative systems.

## 🔍 Topics Covered
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

## 🔍 Topics Covered
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
# Day 3: Agentic AI
## 🔍 Topics Covered
#### 🔹 Agentic AI: 
Its like creating an AI appliation on steroids which can help you create any appliaction and depoly it by using the local fucntion defined to perform specific tasks

---

# Day 4: Retrieval-Augmented Generation (RAG)

This session focused on building intelligent systems that combine large language models with external knowledge sources to enhance response accuracy and relevance.

## 🔍 Topics Covered

- **Knowledge Source**: Understanding structured and unstructured data sources used to enrich model responses.
- **Chunking**: Techniques to split large documents into manageable, semantically meaningful pieces.
- **Vector Embedding**: Converting text chunks into numerical vectors using embedding models for semantic search.
- **Vector DB**: Storing and querying embeddings efficiently using vector databases like FAISS or Pinecone.
- **User Query**: Capturing and processing user input to retrieve relevant context.
- **Retrieval**: Matching user queries with stored vectors to fetch the most relevant information for generation.

> This foundation enables building smarter, context-aware AI applications that go beyond static knowledge.

---

# Day 5: Retrieval-Augmented Generation (RAG) with Queuing System

This module demonstrates how to implement a **Retrieval-Augmented Generation (RAG)** pipeline integrated with a **queuing system** to handle multiple user queries efficiently. The RAG architecture enhances language model responses by retrieving relevant documents from a knowledge base before generating answers. The queuing system ensures scalability and orderly processing of concurrent requests.

## 🔍 Topics Covered
- **Document Retrieval**: Uses vector search to fetch relevant context from a knowledge base.
- **Answer Generation**: Combines retrieved context with a language model to generate accurate responses.
- **Queuing System**: Manages incoming requests using a task queue (e.g., RQ, Redis) for asynchronous processing.
- **Scalability**: Designed to handle high-throughput environments with multiple users.

---

# Day 6: LangGraph
LangGraph is a powerful framework designed to build stateful, multi-agent applications using language models. It extends the capabilities of LangChain by enabling developers to define dynamic, graph-based workflows where each node can represent a language model, tool, or function.

## 🚀 Purpose

LangGraph simplifies the orchestration of complex interactions between agents and tools, making it ideal for building applications like chatbots, autonomous agents, and decision-making systems.

## 🔧 Key Features

- **Graph-Based Architecture**: Define workflows as directed graphs with nodes and edges.
- **State Management**: Maintain and update state across multiple steps and agents.
- **Multi-Agent Support**: Coordinate interactions between multiple language model agents.
- **Tool Integration**: Seamlessly integrate external tools and APIs.
- **LangChain Compatibility**: Built on top of LangChain for easy adoption.

---

# Day 7: LangGraph Part 2

This module explores advanced features of LangGraph that enhance the robustness, observability, and interactivity of language model workflows.
## 🔍 Topics Covered
### 🔄 Checkpointing
Checkpointing allows workflows to persist intermediate states, enabling recovery and resumption from specific points. This is crucial for long-running or fault-tolerant applications.

### 📝 Annotation
Annotations provide metadata and insights into the execution of nodes and edges in the graph. They help in debugging, auditing, and understanding the behavior of the workflow.

### 🔁 Stream
Streaming enables real-time output from the language model, allowing users to receive partial responses as they are generated. This improves responsiveness and user experience.

### 📊 Monitor
Monitoring tools track the performance and health of LangGraph workflows. They provide visibility into execution metrics, errors, and system status, supporting maintenance and optimization.

---
