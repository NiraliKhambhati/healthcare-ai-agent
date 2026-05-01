# Healthcare AI Agent 🏥

An agentic AI system for automated HEDIS measure tracking, clinical data Q&A, 
and quality reporting — built with Claude AI, RAG, ChromaDB, and Python.

## Project Overview
This project demonstrates how AI agents can automate healthcare quality analytics,
specifically targeting Canadian hospital analytics use cases.

## Tech Stack
- **Claude AI (Anthropic)** — LLM for intelligent responses
- **LangChain** — Agent framework
- **ChromaDB** — Vector database for document retrieval
- **RAG Pipeline** — Retrieval Augmented Generation
- **Python** — Core language
- **BigQuery** — Data warehouse (coming soon)
- **Streamlit** — Interactive UI (coming soon)

## Project Progress
- [x] Day 1: Claude API connected — healthcare HEDIS queries working
- [x] Day 2: RAG pipeline — AI answers from HEDIS documents using ChromaDB
- [ ] Day 3: LangChain agents
- [ ] Day 4: Multi-agent system
- [ ] Day 5: Streamlit UI + deployment

## Features
- Natural language Q&A on HEDIS quality measures
- Document-grounded answers (RAG) — no hallucinations
- Automated clinical quality reporting
- PDSA cycle insights from data

## How to Run
```bash
# Clone the repo
git clone https://github.com/NiraliKhambhati/healthcare-ai-agent.git
cd healthcare-ai-agent

# Create virtual environment
python -m venv venv
source venv/Scripts/activate  # Windows
source venv/bin/activate      # Mac/Linux

# Install dependencies
pip install anthropic langchain langchain-anthropic chromadb streamlit pypdf python-dotenv

# Add your API key
echo ANTHROPIC_API_KEY="your-key-here" > .env

# Run Day 1 - Basic API queries
python day1_test.py

# Run Day 2 - RAG Pipeline
python day2_rag.py
```

## Author
**Nirali Khambhati** — Healthcare Business Analyst | MS Health Informatics
- 5+ years healthcare analytics experience
- Skills: SQL, Python, Power BI, BigQuery, AWS QuickSight, HEDIS, HIPAA
- Building AI-powered healthcare analytics for Canadian hospital roles