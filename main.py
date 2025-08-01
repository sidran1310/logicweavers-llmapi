from fastapi import FastAPI, Request, Header, HTTPException
from pydantic import BaseModel
from rag_pipeline.pdf_chunker import download_and_chunk_pdf
from rag_pipeline.retriever import get_top_chunks
from rag_pipeline.gemini_handler import build_prompt, ask_gemini
from rag_pipeline.query_parser import parse_query
import asyncio

app = FastAPI()

EXPECTED_API_KEY = "qwerty"

class HackRxRequest(BaseModel):
    documents: str
    questions: list[str]

@app.post("/hackrx/run")
async def hackrx_run(request: HackRxRequest, authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    token = authorization.split("Bearer ")[-1]
    if token != EXPECTED_API_KEY:
        raise HTTPException(status_code=403, detail="Unauthorized")

    try:
        chunks = download_and_chunk_pdf(request.documents)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"PDF processing failed: {str(e)}")

    results = []

    for question in request.questions:
        parsed = await parse_query(question)
        structured_question = f"""
        User details:
        - Age: {parsed.get("age")}
        - Gender: {parsed.get("gender")}
        - Procedure: {parsed.get("procedure")}
        - Policy Duration: {parsed.get("policy_duration_months")} months
        - Location: {parsed.get("location")}

        Question: Is this procedure covered under the policy?
        """

        top_chunks = get_top_chunks(chunks, structured_question)
        prompt = build_prompt(structured_question, top_chunks)

        try:
            gemini_result = await ask_gemini(prompt)
        except Exception as e:
            gemini_result = {
                "decision": "Unknown",
                "amount": "Unknown",
                "justification": str(e),
                "clause_reference": "N/A"
            }

        results.append({
            "original_question": question,
            "parsed_details": parsed,
            "decision": gemini_result.get("decision"),
            "amount": gemini_result.get("amount"),
            "justification": gemini_result.get("justification"),
            "clause_reference": gemini_result.get("clause_reference"),
            "reference_chunks": top_chunks
        })

    return {"answers": results}
