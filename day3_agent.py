import anthropic
from dotenv import load_dotenv
import chromadb
import sys
sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

client = anthropic.Anthropic()

# ---- STEP 1: Load HEDIS documents into ChromaDB (same as Day 2) ----
with open("data/hedis_measures.txt", "r") as f:
    content = f.read()

chunks = content.strip().split("\n\n")
chroma_client = chromadb.Client()
collection = chroma_client.create_collection(name="hedis_docs")

for i, chunk in enumerate(chunks):
    collection.add(documents=[chunk], ids=[f"chunk_{i}"])

print("SUCCESS: HEDIS documents loaded into ChromaDB")

# ---- STEP 2: Define tools for the agent ----
tools = [
    {
        "name": "search_hedis_documents",
        "description": "Search HEDIS measure specifications to answer questions about eligibility criteria, exclusions, thresholds, and measure definitions. Use this when the question is specifically about HEDIS measures.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query to find relevant HEDIS information"
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "answer_general_healthcare",
        "description": "Answer general healthcare analytics questions that are not specifically about HEDIS measure definitions. Use this for questions about hospital operations, readmissions, quality improvement, etc.",
        "input_schema": {
            "type": "object",
            "properties": {
                "question": {
                    "type": "string",
                    "description": "The general healthcare question to answer"
                }
            },
            "required": ["question"]
        }
    }
]

# ---- STEP 3: Tool execution function ----
def execute_tool(tool_name, tool_input):
    if tool_name == "search_hedis_documents":
        results = collection.query(
            query_texts=[tool_input["query"]],
            n_results=2
        )
        retrieved = "\n\n".join(results["documents"][0])
        return f"Found in HEDIS documents:\n{retrieved}"
    
    elif tool_name == "answer_general_healthcare":
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=512,
            messages=[
                {
                    "role": "user",
                    "content": f"You are a healthcare analytics expert. Answer briefly: {tool_input['question']}"
                }
            ]
        )
        return response.content[0].text

# ---- STEP 4: Agent function ----
def run_agent(user_question):
    print(f"\n{'='*50}")
    print(f"Question: {user_question}")
    
    messages = [{"role": "user", "content": user_question}]
    
    # Agent decides which tool to use
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        tools=tools,
        messages=messages
    )
    
    # Check if agent wants to use a tool
    if response.stop_reason == "tool_use":
        tool_use = next(b for b in response.content if b.type == "tool_use")
        tool_name = tool_use.name
        tool_input = tool_use.input
        
        print(f"Agent chose tool: {tool_name}")
        
        # Execute the tool
        tool_result = execute_tool(tool_name, tool_input)
        
        # Send result back to agent for final answer
        messages = [
            {"role": "user", "content": user_question},
            {"role": "assistant", "content": response.content},
            {
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": tool_use.id,
                        "content": tool_result
                    }
                ]
            }
        ]
        
        final_response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            tools=tools,
            messages=messages
        )
        
        print(f"Answer: {final_response.content[0].text}")
    else:
        print(f"Answer: {response.content[0].text}")

# ---- STEP 5: Test the agent with different questions ----
questions = [
    "What are the eligibility criteria for the HEDIS CBP measure?",
    "What are the top causes of hospital readmissions?",
    "Which patients are excluded from the asthma measure?",
    "How does PDSA cycle work in quality improvement?"
]

for question in questions:
    run_agent(question)