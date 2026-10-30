"""api/main.py — REFERENCE for Week 3 Lab Step 1.

The completed version. Wraps the W2 async pipeline behind a stable HTTP
contract (Question/Answer with field names question/content) while delegating
to the W2 pipeline internally.

Run with:
    uvicorn api.main:app --reload --port 8000

Hit with curl:
    curl -X POST http://localhost:8000/ask_batched \
         -H "Content-Type: application/json" \
         -d '{"question": "What is RAG?"}'
"""
import logging
import asyncio
import time

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from openai import BaseModel
from src.week2.pipeline.pipeline import ask_llm as _pipeline_ask_llm
from src.week2.pipeline.pipeline import Question as _PipelineQuestion
from collections import defaultdict

logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(levelname)s  %(message)s")
log = logging.getLogger(__name__)

request_counts = defaultdict(lambda: {
  "status_codes": defaultdict(int),
  "total_requests": 0,
  "total_latency": 0.0
})

# ─────────────────────────────────────────────────────────────────────────────
# Public W3 API models — locked in ADR 0002
# These are intentionally separate from the W2 internal models (which use
# `text` field names). The endpoint handlers translate between the two.
# ─────────────────────────────────────────────────────────────────────────────
class Question(BaseModel):
    """Public request shape — locked in ADR 0002."""
    question: str


class Answer(BaseModel):
    """Public response shape — locked in ADR 0002."""
    content: str
    cost_usd: float
    retries: int

app = FastAPI(
  title= "Capstone API",
  description= "Wraps the W2 async pipeline. Contract locked in ADR 0002 (W3); internals upgraded W4+.",
  version="1.0.0"
)

# ─────────────────────────────────────────────────────────────────────────────
# /ask_batched — non-streaming reference endpoint
# ─────────────────────────────────────────────────────────────────────────────
@app.post("/ask_batched", response_model=Answer)
async def ask_batched(q: Question) -> Answer:
  """Non-streaming. Returns the full Answer in a single JSON body."""
  log.info("ask batched question=%r", q.question[:80])
  pipeline_q = _PipelineQuestion(text= q.question)
  pipeline_ans = await _pipeline_ask_llm(pipeline_q)
  return Answer(
     content= pipeline_ans.text,
     cost_usd= pipeline_ans.cost_usd,
     retries= pipeline_ans.retries
  )

# ─────────────────────────────────────────────────────────────────────────────
# /health — liveness probe
# ─────────────────────────────────────────────────────────────────────────────
@app.get("/health")
async def health():
   return {"status": "ok"}


# ─────────────────────────────────────────────────────────────────────────────
# /ask — streaming endpoint (the contracted one)
# ─────────────────────────────────────────────────────────────────────────────
async def stream_answer(question_text: str):
  """Async generator yielding the answer word-by-word.

    W3 streams from FastAPI to the client; the pipeline call itself is still
    non-streaming. In W4 the LLM call becomes a real stream end-to-end — this
    generator's shape doesn't change, only what fills it.
    """
  pipeline_q = _PipelineQuestion(text= question_text)
  pipeline_ans = await _pipeline_ask_llm(pipeline_q)
  for word in pipeline_ans.text.split(" "):
     yield word + " "
     await asyncio.sleep(0.05)

@app.post("/ask")
async def ask(q: Question):
  """Streaming /ask — the contracted endpoint."""
  log.info("ask question=%r", q.question[:80])
  return StreamingResponse(
     stream_answer(q.question),
     media_type="text/plain"
  )

@app.middleware("http")
async def count_request(request, call_next):

    path = request.url.path

    # Exclude metrics endpoint from monitoring
    if path == "/metrics":
        return await call_next(request)

    start_time = time.perf_counter()

    response = await call_next(request)

    elapsed = time.perf_counter() - start_time

    # Update request statistics
    stats = request_counts[path]

    stats["total_requests"] += 1
    stats["status_codes"][str(response.status_code)] += 1
    stats["total_latency"] += elapsed

    return response


# ---------------------------------------------------------
# /metrics — endpoint to measure request counts and latency
# ---------------------------------------------------------
@app.get("/metrics")
async def metrics():

    endpoints = {}

    for path, stats in request_counts.items():

        total_requests = stats["total_requests"]
        total_latency = stats["total_latency"]

        endpoints[path] = {
            "total_requests": total_requests,
            "status_codes": dict(stats["status_codes"]),
            "total_latency_seconds": round(total_latency, 4),
            "mean_latency_seconds": round(
                total_latency / total_requests, 4
            ) if total_requests else 0
        }

    return {
        "endpoints": endpoints,
        "total_requests": sum(
            stats["total_requests"]
            for stats in request_counts.values()
        )
    }

