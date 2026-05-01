# Import libraries
import anthropic
from dotenv import load_dotenv
import chromadb
import sys
sys.stdout.reconfigure(encoding='utf-8')

# Load your API key from .env file
load_dotenv()

# Initialize Claude client HERE at the top
client = anthropic.Anthropic()

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

# ---- STEP 4: Test multiple queries ----
queries = [
    "Which patients qualify for the diabetes measure?",
    "What is the blood pressure threshold for CBP measure?",
    "What happens after a patient is hospitalized for mental illness?",
    "What are the exclusions for the asthma measure?",
    "Which measures exclude hospice care patients?"
]

for query in queries:
    print(f"\n{'='*50}")
    print(f"Query: {query}")

    results = collection.query(
        query_texts=[query],
        n_results=1
    )

    retrieved_docs = "\n\n".join(results["documents"][0])

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=512,
        messages=[
            {
                "role": "user",
                "content": f"""You are a healthcare data analyst assistant.
Use ONLY the following context to answer briefly.

Context:
{retrieved_docs}

Question: {query}"""
            }
        ]
    )
    print(f"Answer: {message.content[0].text}")