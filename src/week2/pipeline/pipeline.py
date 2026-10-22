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

from src.week2.pipeline.fake_llm import Question, Answer, fake_ask_llm  
from src.week2.pipeline.settings import Settings, RunSummary
from .logging_config import get_logger

import csv
from pathlib import Path

log = get_logger()

# ─────────────────────────────────────────────────────────────────────────────
# LLM client setup — branches on Settings.use_fake at module-load time
# ─────────────────────────────────────────────────────────────────────────────

_settings_for_import = Settings()
if _settings_for_import.use_fake:
  from fake_llm import Question, Answer, FakeLLMError, fake_ask_llm
else:
  from dotenv import load_dotenv
  from openai import AsyncOpenAI
  from pydantic import BaseModel

  load_dotenv
  _client = AsyncOpenAI()

  class Question(BaseModel):
    text: str

  class Answer(BaseModel):
    question: str
    text: str
    cost_usd: float
    retries: int = 0  

# ─────────────────────────────────────────────────────────────────────────────
# CSV loader
# ─────────────────────────────────────────────────────────────────────────────
def load_questions(path: str | Path = "src/week2/data/questions.csv") -> list[Question]:
  with open(path, newline="", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))
  return [Question(text= q["text"]) for q in rows if q.get("text")]


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

async def run_batch(
    questions: list[Question], 
    fail_rate: float = 0.0) -> list[Answer]:
  """Fire all questions in parallel, via async `gather`"""
  tasks = [ask_llm_with_retry(q, fail_rate= fail_rate) for q in questions]
  return await asyncio.gather(*tasks)

async def run_in_batches(
    questions: list[Question], 
    batch_size = 5, 
    fail_rate = 0.00
  ) -> list[Answer]:
    """Fire questions in chunks of `batch_size`, with a 100 ms pause between batches.""" 
    out: list[Answer] = []
    for i in range(0, len(questions), batch_size):
      chunk = questions[i: i+ batch_size]
      log.info(f"batch { i // batch_size + 1} : {len(chunk)} questions")
      batch_answers = await asyncio.gather(
        *(ask_llm_with_retry(q, fail_rate=fail_rate) for q in chunk)
      )
      out.extend(batch_answers)
      await asyncio.sleep(0.1)
    return out


class JSONFormatter(logging.Formatter):
  def format(self, record: logging.LogRecord) -> str:
    """Format a log record as JSON."""
    return json.dumps({
      "time": time.time(),
      "level": record.levelname,
      "message": record.getMessage()
    })

# log = logging.getLogger("pipeline")
# log.setLevel(logging.INFO)
# _handler = logging.StreamHandler()
# _handler.setFormatter(JSONFormatter())
# log.addHandler(_handler)

# ─────────────────────────────────────────────────────────────────────────────
# Run summariser
# ─────────────────────────────────────────────────────────────────────────────
def summarise_run(
    answers: list[Answer],
    *,
    started_at: float,
    elapsed: float,
    fail_rate: float,
    use_fake: bool
) -> RunSummary:
  """Roll a list of Answers + wall-clock data into a RunSummary."""
  return RunSummary(
    started_at= started_at,
    elapsed_seconds= elapsed,
    n_questions= len(answers),
    n_succeeded= len(answers),
    n_retries_total= sum(a.retries for a in answers),
    total_cost_usd= sum(a.cost_usd for a in answers),
    fail_rate= fail_rate,
    use_fake= use_fake
  )

# ─────────────────────────────────────────────────────────────────────────────
# Entrypoint
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
  settings = Settings()
  log.info(f"config: {settings.model_dump(mode='json')}")

  #import sys

  #fail_rate = float(sys.argv[1]) if len(sys.argv) > 1 else 0.0

  # sample = [
  #   Question(text="What is RAG in one sentence?"),
  #   Question(text="Name three uses of vector databases."),
  #   Question(text="Why might an LLM hallucinate?"),
  # ]

  #[log.info(f"asked: {question.text}") for question in sample]
  #answers = asyncio.run(run_batch(sample, fail_rate=settings.fail_rate))
  
  questions = load_questions(settings.questions_csv)
  log.info(f"loaded {len(questions)} questions")
  
  started = time.time()
  answers = asyncio.run(
    run_in_batches(
      questions, 
      batch_size= settings.batch_size, 
      fail_rate= settings.fail_rate
    )
  )
  elapsed = time.time() - started

  summary = summarise_run(
    answers,
    started_at = started,
    elapsed    = elapsed,
    fail_rate  = settings.fail_rate,
    use_fake   = settings.use_fake,
  )
  log.info(f"summary: {summary.model_dump_json()}")

  # Write the structured artefact
  settings.results_json.write_text(
    json.dumps({
      "summary": summary.model_dump(mode="json"),
      "answers": [a.model_dump() for a in answers]
    }, indent=2),
    encoding="utf-8",
  )
  print(f"wrote {len(answers)} answers to {settings.results_json} in {elapsed:.2f}s ")


  # print(f"\n{len(answers)} answers in {elapsed: .2f} seconds)\n")
  # for a in answers:
  #   print(f"- {a.text[:80]}")

  