import httpx
import json

# Working Gemini API key (replace with your actual one)
GEMINI_API_KEY = "AIzaSyD-VceadJH51xGSKcdmHjagf6KTb-lQFi8"

def build_prompt(question: str, context_chunks: list[str]) -> str:
    context = "\n\n".join(context_chunks)
    prompt = f"""
You are an insurance claim reasoning assistant. Based on the context from the policy below, answer the user's question.

Respond strictly in this JSON format:
{{
  "decision": "Approved or Rejected",
  "amount": "e.g., 80% coverage up to 1 lakh or 'Not applicable'",
  "justification": "Explain why this decision was made",
  "clause_reference": "Summarize the clause or text used for the decision"
}}

Context from policy:
{context}

Question:
{question}
"""
    return prompt

async def ask_gemini(prompt: str) -> dict:
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": "AIzaSyD-VceadJH51xGSKcdmHjagf6KTb-lQFi8"
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=data)

    if response.status_code != 200:
        raise Exception(f"Gemini API Error: {response.text}")

    try:
        raw = response.json()["candidates"][0]["content"]["parts"][0]["text"]
        return json.loads(raw)
    except Exception:
        return {
            "decision": "Unknown",
            "amount": "Unknown",
            "justification": raw.strip(),
            "clause_reference": "Not extracted"
        }
