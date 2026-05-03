import anthropic
from dotenv import load_dotenv
import chromadb
import sys
sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

client = anthropic.Anthropic()

# ---- LOAD HEDIS DOCUMENTS ----
with open("data/hedis_measures.txt", "r") as f:
    content = f.read()

chunks = content.strip().split("\n\n")
chroma_client = chromadb.Client()
collection = chroma_client.create_collection(name="hedis_docs")

for i, chunk in enumerate(chunks):
    collection.add(documents=[chunk], ids=[f"chunk_{i}"])

print("SUCCESS: HEDIS documents loaded")

# ---- SPECIALIST AGENT 1: Data Agent ----
def data_agent(question):
    """Searches HEDIS documents and returns data-driven answers"""
    print(f"\n  [Data Agent] Processing: {question}")
    
    results = collection.query(query_texts=[question], n_results=2)
    retrieved = "\n\n".join(results["documents"][0])
    
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=512,
        messages=[{
            "role": "user",
            "content": f"""You are a healthcare data specialist.
Answer this question using ONLY the provided HEDIS documentation.
Be specific and data-focused.

Documentation:
{retrieved}

Question: {question}"""
        }]
    )
    return response.content[0].text

# ---- SPECIALIST AGENT 2: Report Agent ----
def report_agent(data_findings):
    """Takes data findings and generates an executive quality report"""
    print(f"\n  [Report Agent] Generating quality report...")
    
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": f"""You are a healthcare quality reporting specialist.
Based on the following data findings, generate a concise executive summary report.
Format it professionally as if presenting to hospital leadership.

Data Findings:
{data_findings}

Generate a brief executive quality report with:
1. Key Findings
2. Quality Gaps Identified  
3. Recommended Actions (PDSA cycle suggestions)"""
        }]
    )
    return response.content[0].text

# ---- SUPERVISOR AGENT ----
def supervisor_agent(user_request):
    """Orchestrates specialist agents to fulfill complex requests"""
    print(f"\n{'='*50}")
    print(f"SUPERVISOR: Received request: {user_request}")
    
    # Step 1 - Supervisor decides what data is needed
    print("\nSUPERVISOR: Analyzing request and delegating to Data Agent...")
    
    questions = [
        "What are the eligibility criteria and exclusions for HEDIS CBP measure?",
        "What are the eligibility criteria and exclusions for HEDIS CDC diabetes measure?",
        "What follow-up requirements exist for mental health hospitalizations?"
    ]
    
    # Step 2 - Data Agent gathers all findings
    all_findings = []
    for question in questions:
        finding = data_agent(question)
        all_findings.append(f"Q: {question}\nA: {finding}")
    
    combined_findings = "\n\n---\n\n".join(all_findings)
    
    # Step 3 - Report Agent generates executive report
    print("\nSUPERVISOR: Data gathered. Delegating to Report Agent...")
    report = report_agent(combined_findings)
    
    print("\n" + "="*50)
    print("FINAL EXECUTIVE QUALITY REPORT")
    print("="*50)
    print(report)
    
    return report

# ---- RUN THE MULTI-AGENT SYSTEM ----
supervisor_agent("Generate a comprehensive HEDIS quality report for hospital leadership")