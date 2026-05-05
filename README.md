# Healthcare AI Agent 🏥

An agentic AI system for automated HEDIS measure tracking, clinical data Q&A, 
and quality reporting — built with Claude AI, RAG, ChromaDB, and Python.

🚀 **Live Demo:** [nirali-healthcare-ai.streamlit.app](https://nirali-healthcare-ai.streamlit.app)

## Project Overview
This project demonstrates how AI agents can automate healthcare quality analytics,
specifically targeting Canadian hospital analytics use cases. Built using 100,000
synthetic patient records across HEDIS and CIHI quality measures.

## Tech Stack
- **Claude AI (Anthropic)** — LLM for intelligent responses
- **ChromaDB** — Vector database for document retrieval
- **RAG Pipeline** — Retrieval Augmented Generation
- **Multi-Agent System** — Supervisor + specialist agents
- **Python** — Core language
- **Streamlit** — Interactive web app (deployed live)
- **Plotly** — Interactive charts and dashboards
- **Pandas** — 100K patient data analysis

## Live Features
- 💬 **AI Chat** — Ask any healthcare analytics question
- 📊 **HEDIS Dashboard** — 8 measures computed from 100K patient records
- 🍁 **CIHI Canadian Indicators** — Readmission, ALC, HSMR
- 📈 **Province-level charts** — Performance by ON, BC, AB, QC
- 📄 **Executive Report Generator** — One click multi-agent quality report

## Project Progress
- [x] Day 1: Claude API connected — healthcare HEDIS queries working
- [x] Day 2: RAG pipeline — AI answers from HEDIS documents using ChromaDB
- [x] Day 3: Agentic AI — auto tool selection between RAG and general healthcare
- [x] Day 4: Multi-agent system — supervisor orchestrates data and report agents
- [x] Day 5: Streamlit web app deployed live with 100K patient dataset

## How to Run Locally
```bash
# Clone the repo
git clone https://github.com/NiraliKhambhati/healthcare-ai-agent.git
cd healthcare-ai-agent

# Create virtual environment
python -m venv venv
source venv/Scripts/activate  # Windows
source venv/bin/activate      # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Add your API key
echo ANTHROPIC_API_KEY="your-key-here" > .env

# Run the app
streamlit run app.py
```

## Author
**Nirali Khambhati** — Healthcare Business Analyst | MS Health Informatics
- 5+ years healthcare analytics experience (Elevance Health, Independence Blue Cross)
- Skills: SQL, Python, Power BI, BigQuery, AWS QuickSight, HEDIS, HIPAA, Claude AI
- 🍁 Targeting Canadian hospital analytics roles
- 🔗 [Live App](https://nirali-healthcare-ai.streamlit.app) | [GitHub](https://github.com/NiraliKhambhati)