import httpx
import json

GEMINI_API_KEY = "AIzaSyD-VceadJH51xGSKcdmHjagf6KTb-lQFi8"

async def parse_query(natural_query: str) -> dict:
    prompt = f"""
Extract the following fields from the user's input:

Fields:
- age (int)
- gender (Male/Female/Unknown)
- procedure (e.g. knee surgery, cataract)
- policy_duration_months (int)
- location (optional, e.g. Pune)

Respond in JSON format.

Input: "{natural_query}"
"""

    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent"
    headers = {"Content-Type": "application/json"}
    params = {"key": GEMINI_API_KEY}
    data = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, params=params, json=data)

    if response.status_code != 200:
        raise Exception(f"Gemini parsing error: {response.text}")

    try:
        raw = response.json()["candidates"][0]["content"]["parts"][0]["text"]
        return json.loads(raw)
    except Exception:
        return {"error": "Parsing failed", "raw": raw}
