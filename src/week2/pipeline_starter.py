"""pipeline.py — Week 2 hands-on starter.

The pieces:

    Step 2 — async def ask_llm                 (one call)
    Step 3 — ask_llm_with_retry                (exponential backoff)
    Step 4 — run_batch with asyncio.gather     (parallel fan-out)
    Step 5 — JSON-formatted structured logging
"""

from __future__ import annotations
import asyncio
import json
import logging
import time

from fake_llm import Question, Answer, fake_ask_llm, FakeLLMError

# ---------- Step 2: one async call ----------
async def ask_llm(q: Question, fail_rate: float = 0.0) -> Answer:
  """One call. Live demo: fake. Lab: real AsyncOpenAI (same signature)."""
  answer = await fake_ask_llm(q, fail_rate=fail_rate)
  logging.info(json.dumps({"event": "asked", "question": q.text[:40]}))
  return answer

async def ask_llm_with_retry(
    q: Question,
    tries: int = 3,
    fail_rate: float = 0.0
) -> Answer:
  """Retry up to ``tries`` times. Wait 1 s, 2 s, 4 s between attempts."""
  for attempt in range(tries):
    try:
      answer = await ask_llm(q, fail_rate=fail_rate)
      answer.retries = attempt
      return answer
    except Exception as exc:
      if attempt == tries - 1:
        raise
      logging.warning(json.dumps({"event": "retry", "attempt": attempt, "question": q.text[:40], "error": str(exc)}))
      await asyncio.sleep(2 ** attempt)  # 1, 2, 4, ... seconds   

async def run_batch(questions: list[Question], fail_rate: float = 0.0) -> list[Answer]:
  """Fire all questions in parallel, via async `gather`"""
  tasks = [ask_llm_with_retry(q, fail_rate= fail_rate) for q in questions]
  return await asyncio.gather(*tasks)

class JSONFormatter(logging.Formatter):
  def format(self, record: logging.LogRecord) -> str:
    """Format a log record as JSON."""
    return json.dumps({
      "time": time.time(),
      "level": record.levelname,
      "message": record.getMessage()
    })

log = logging.getLogger("pipeline")
log.setLevel(logging.INFO)
_handler = logging.StreamHandler()
_handler.setFormatter(JSONFormatter())
log.addHandler(_handler)

#------main -------#
if __name__ == "__main__":
  import sys

  fail_rate = float(sys.argv[1]) if len(sys.argv) > 1 else 0.0
  sample = [
    Question(text="What is RAG in one sentence?"),
    Question(text="Name three uses of vector databases."),
    Question(text="Why might an LLM hallucinate?"),
  ]
  started = time.time()
  answers = asyncio.run(run_batch(sample, fail_rate=fail_rate))
  elapsed = time.time() - started
  print(f"\n{len(answers)} answers in {elapsed: .2f} seconds)\n")
  for a in answers:
    print(f"- {a.text[:80]}")

  