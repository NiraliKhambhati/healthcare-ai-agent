import anthropic
from dotenv import load_dotenv
import chromadb
import streamlit as st
import sys

load_dotenv()

# ---- PAGE CONFIG ----
st.set_page_config(
    page_title="Healthcare AI Agent",
    page_icon="🏥",
    layout="wide"
)

# ---- LOAD HEDIS DOCUMENTS ----
@st.cache_resource
def load_hedis_db():
    with open("data/hedis_measures.txt", "r") as f:
        content = f.read()
    chunks = content.strip().split("\n\n")
    chroma_client = chromadb.Client()
    collection = chroma_client.create_collection(name="hedis_docs")
    for i, chunk in enumerate(chunks):
        collection.add(documents=[chunk], ids=[f"chunk_{i}"])
    return collection

collection = load_hedis_db()
client = anthropic.Anthropic()

# ---- AGENT FUNCTIONS ----
def data_agent(question):
    results = collection.query(query_texts=[question], n_results=2)
    retrieved = "\n\n".join(results["documents"][0])
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=512,
        messages=[{
            "role": "user",
            "content": f"""You are a healthcare data specialist.
Answer using ONLY the provided HEDIS documentation.

Documentation:
{retrieved}

Question: {question}"""
        }]
    )
    return response.content[0].text

def general_agent(question):
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=512,
        messages=[{
            "role": "user",
            "content": f"You are a healthcare analytics expert. Answer briefly: {question}"
        }]
    )
    return response.content[0].text

def report_agent():
    questions = [
        "What are the eligibility criteria and exclusions for HEDIS CBP measure?",
        "What are the eligibility criteria and exclusions for HEDIS CDC diabetes measure?",
        "What follow-up requirements exist for mental health hospitalizations?"
    ]
    all_findings = []
    for q in questions:
        finding = data_agent(q)
        all_findings.append(f"Q: {q}\nA: {finding}")
    
    combined = "\n\n---\n\n".join(all_findings)
    
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": f"""Generate a professional executive quality report for hospital leadership.

Data Findings:
{combined}

Include:
1. Key Findings
2. Quality Gaps Identified
3. Recommended PDSA Actions"""
        }]
    )
    return response.content[0].text

# ---- SIDEBAR ----
st.sidebar.title("Healthcare AI Agent")
st.sidebar.markdown("Powered by **Claude AI + RAG**")
page = st.sidebar.radio("Navigate", ["Chat", "HEDIS Dashboard", "Generate Report"])

# ---- PAGE 1: CHAT ----
if page == "Chat":
    st.title("Healthcare AI Chat")
    st.markdown("Ask any healthcare analytics question — powered by Claude AI")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Ask a healthcare question..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                hedis_keywords = ["hedis", "cbp", "cdc", "fuh", "amr", "measure", "eligibility", "exclusion"]
                if any(word in prompt.lower() for word in hedis_keywords):
                    response = data_agent(prompt)
                else:
                    response = general_agent(prompt)
            st.markdown(response)
        
        st.session_state.messages.append({"role": "assistant", "content": response})

# ---- PAGE 2: HEDIS DASHBOARD ----
elif page == "HEDIS Dashboard":
    import pandas as pd
    import plotly.express as px

    st.title("HEDIS & CIHI Quality Dashboard")
    st.markdown("Live stats calculated from 100,000 synthetic patient records")

    df = pd.read_csv("data/patient_data.csv")

    # ---- SIDEBAR FILTERS ----
    st.sidebar.markdown("---")
    st.sidebar.subheader("Filters")
    province_filter = st.sidebar.multiselect(
        "Province", options=sorted(df["province"].unique()),
        default=sorted(df["province"].unique())
    )
    df = df[df["province"].isin(province_filter)]

    # ---- CALCULATE STATS ----
    cbp_eligible = df[df["has_hypertension"] & ~df["in_hospice"] & df["bp_controlled"].notna()]
    cbp_rate = cbp_eligible["bp_controlled"].mean() * 100

    cdc_eligible = df[df["has_diabetes"] & ~df["in_hospice"] & df["hba1c_controlled"].notna()]
    cdc_rate = cdc_eligible["hba1c_controlled"].mean() * 100
    hba1c_poor_rate = cdc_eligible["hba1c_poor_control"].mean() * 100

    amr_eligible = df[df["has_asthma"] & df["amr_compliant"].notna()]
    amr_rate = amr_eligible["amr_compliant"].mean() * 100

    fuh_eligible = df[df["had_mental_health_admission"] & df["followup_7day"].notna()]
    fuh_7day_rate = fuh_eligible["followup_7day"].mean() * 100
    fuh_30day_rate = fuh_eligible["followup_30day"].mean() * 100

    bcs_eligible = df[df["eligible_mammogram"] & df["had_mammogram"].notna()]
    bcs_rate = bcs_eligible["had_mammogram"].mean() * 100

    col_eligible = df[df["eligible_colonoscopy"] & df["had_colonoscopy"].notna()]
    col_rate = col_eligible["had_colonoscopy"].mean() * 100

    admitted = df[df["was_admitted"] & df["readmitted_30day"].notna()]
    readmission_rate = admitted["readmitted_30day"].mean() * 100
    alc_rate = df[df["was_admitted"]]["alc_flag"].mean() * 100

    # ---- HEDIS METRICS ----
    st.subheader("HEDIS Quality Measures")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("CBP Control Rate", f"{cbp_rate:.1f}%", f"{cbp_rate-70:.1f}% vs target")
    col2.metric("Diabetes HbA1c", f"{cdc_rate:.1f}%", f"{cdc_rate-60:.1f}% vs target")
    col3.metric("HbA1c Poor Control", f"{hba1c_poor_rate:.1f}%", f"{20-hba1c_poor_rate:.1f}% vs target")
    col4.metric("AMR Asthma", f"{amr_rate:.1f}%", f"{amr_rate-50:.1f}% vs target")

    col5, col6, col7, col8 = st.columns(4)
    col5.metric("FUH 7-day", f"{fuh_7day_rate:.1f}%", f"{fuh_7day_rate-55:.1f}% vs target")
    col6.metric("FUH 30-day", f"{fuh_30day_rate:.1f}%", f"{fuh_30day_rate-65:.1f}% vs target")
    col7.metric("Breast Cancer Screening", f"{bcs_rate:.1f}%", f"{bcs_rate-65:.1f}% vs target")
    col8.metric("Colorectal Screening", f"{col_rate:.1f}%", f"{col_rate-60:.1f}% vs target")

    st.divider()

    # ---- CIHI METRICS ----
    st.subheader("CIHI Canadian Hospital Indicators")
    col9, col10, col11 = st.columns(3)
    col9.metric("30-day Readmission Rate", f"{readmission_rate:.1f}%", f"{8.5-readmission_rate:.1f}% vs 8.5% avg")
    col10.metric("ALC Rate", f"{alc_rate:.1f}%", f"{15-alc_rate:.1f}% vs 15% target")
    col11.metric("Total Patients", f"{len(df):,}", "synthetic dataset")

    st.divider()

    # ---- PROVINCE CHART ----
    st.subheader("CBP Control Rate by Province")
    prov_stats = []
    for prov in sorted(df["province"].unique()):
        prov_df = df[df["province"] == prov]
        prov_cbp = prov_df[prov_df["has_hypertension"] & prov_df["bp_controlled"].notna()]["bp_controlled"].mean() * 100
        prov_cdc = prov_df[prov_df["has_diabetes"] & prov_df["hba1c_controlled"].notna()]["hba1c_controlled"].mean() * 100
        prov_read = prov_df[prov_df["was_admitted"] & prov_df["readmitted_30day"].notna()]["readmitted_30day"].mean() * 100
        prov_stats.append({"Province": prov, "CBP Rate": round(prov_cbp, 1), "Diabetes Rate": round(prov_cdc, 1), "Readmission Rate": round(prov_read, 1)})

    prov_df_stats = pd.DataFrame(prov_stats)

    fig1 = px.bar(prov_df_stats, x="Province", y="CBP Rate",
                  color="CBP Rate", color_continuous_scale="Blues",
                  title="Blood Pressure Control Rate by Province")
    st.plotly_chart(fig1, use_container_width=True)

    fig2 = px.bar(prov_df_stats, x="Province", y="Readmission Rate",
                  color="Readmission Rate", color_continuous_scale="Reds",
                  title="30-day Readmission Rate by Province")
    st.plotly_chart(fig2, use_container_width=True)

    st.divider()

    # ---- AGE GROUP ANALYSIS ----
    st.subheader("Readmission Rate by Age Group")
    df["age_group"] = pd.cut(df["age"], bins=[18,35,50,65,75,85],
                              labels=["18-35","36-50","51-65","66-75","76-85"])
    age_read = df[df["was_admitted"] & df["readmitted_30day"].notna()].groupby("age_group", observed=True)["readmitted_30day"].mean().reset_index()
    age_read["readmitted_30day"] = (age_read["readmitted_30day"] * 100).round(1)
    fig3 = px.line(age_read, x="age_group", y="readmitted_30day",
                   title="Readmission Rate by Age Group", markers=True)
    st.plotly_chart(fig3, use_container_width=True)

    st.divider()

    # ---- RAW DATA ----
    st.subheader("Patient Data Sample")
    st.dataframe(df.head(100))

# ---- PAGE 3: GENERATE REPORT ----
elif page == "Generate Report":
    st.title("Executive Quality Report Generator")
    st.markdown("Generate a professional HEDIS quality report for hospital leadership")

    if st.button("Generate Report", type="primary"):
        with st.spinner("Multi-agent system generating report..."):
            report = report_agent()
        st.markdown(report)
        st.download_button(
            label="Download Report",
            data=report,
            file_name="hedis_quality_report.txt",
            mime="text/plain"
        )