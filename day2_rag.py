# Import libraries
import anthropic
from dotenv import load_dotenv
import chromadb
import sys
sys.stdout.reconfigure(encoding='utf-8')

# Load your API key from .env file
load_dotenv()

# ---- STEP 1: Read the document ----
with open("data/hedis_measures.txt", "r") as f:
    content = f.read()

# ---- STEP 2: Split into chunks ----
chunks = content.strip().split("\n\n")

# ---- STEP 3: Store in ChromaDB ----
chroma_client = chromadb.Client()
collection = chroma_client.create_collection(name="hedis_docs")

for i, chunk in enumerate(chunks):
    collection.add(
        documents=[chunk],
        ids=[f"chunk_{i}"]
    )

print(f"SUCCESS: Loaded {len(chunks)} HEDIS measure chunks into ChromaDB")

# ---- STEP 4: Search the document ----
query = "Which patients qualify for the diabetes measure?"

results = collection.query(
    query_texts=[query],
    n_results=2
)

retrieved_docs = "\n\n".join(results["documents"][0])
print(f"\nQuery: {query}")
print(f"\nRetrieved from document:\n{retrieved_docs}")

# ---- STEP 5: Send to Claude with context ----
client = anthropic.Anthropic()

message = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    messages=[
        {
            "role": "user",
            "content": f"""You are a healthcare data analyst assistant.
Use ONLY the following document context to answer the question.

Context:
{retrieved_docs}

Question: {query}

Answer based only on the context provided."""
        }
    ]
)

print(f"\nClaude's answer:\n{message.content[0].text}")
