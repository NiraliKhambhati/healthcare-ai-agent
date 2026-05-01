import anthropic
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic()

queries = [
    "Explain what the HEDIS CBP measure is and which patients qualify. Keep it brief.",
    "What are the top 5 factors that cause 30-day hospital readmissions? Be brief.",
    "What are the most common ICD-10 codes used in hospital readmission analysis? Be brief."
]

for i, query in enumerate(queries, 1):
    print(f"\n=== Query {i} ===")
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[{"role": "user", "content": query}]
    )
    print(message.content[0].text)
    print("-" * 50)