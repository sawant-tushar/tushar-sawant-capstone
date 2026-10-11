"""pipeline.py — Week 2 reference with run_batch + run_batch_stream.

This is the working solution for the W2 activity: adds `run_batch_stream`
alongside the existing `run_batch`. Both use the same `fake_ask_llm`
underneath, but `run_batch_stream` uses `asyncio.as_completed` so
answers print in completion order.
"""

from __future__ import annotations
import asyncio
import random
from dataclasses import dataclass
import time

@dataclass
class Question:
    text: str

@dataclass
class Answer:
    text: str

# ─── Fake LLM (replace with real one in production) ─────────────────────
class TransientError(Exception):
    """Simulate a transient error from the LLM API."""
    pass

async def fake_ask_llm(q: Question, fail_rate: float = 0.0) -> Answer:
    """Simulate an async LLM call. Sleep for random 0.3-1.5s, may fail"""
    if random.random() < fail_rate:
        await asyncio.sleep(0.1)
        raise TransientError(f"Simulated transient error for question: {q.text}")
    await asyncio.sleep(random.uniform(0.3, 1.5))
    return Answer(text=f"Simulated answer for: {q.text[:40]}")

async def ask_llm_with_retry(q: Question, tries: int = 3, fail_rate: float = 0.0, max_attempts: int = 3) -> Answer:
    """Wraps fake_ask_llm with 1s/2s/4s backoff on transient failures."""
    for attempt in range(max_attempts):
        try:
            return await fake_ask_llm(q, fail_rate=fail_rate)
        except TransientError as e:
            if attempt == max_attempts - 1:
                raise
            backoff_seconds = 2 ** attempt
            await asyncio.sleep(backoff_seconds) # 1, 2, 4 seconds
    raise RuntimeError("Unreachable")

# ─── run_batch — the lab pattern (gather, returns in input order) ───────
async def run_batch(questions: list[Question], fail_rate: float = 0.0) -> list[Answer]:
    tasks = [ask_llm_with_retry(q, fail_rate=fail_rate) for q in questions]
    return await asyncio.gather(*tasks)

# ─── run_batch_stream — the W2 activity pattern (as_completed) ──────────
async def run_batch_stream(questions: list[Question], fail_rate: float = 0.0) -> list[Answer]:
    """Streams: prints each answer as it arrives, returns in completion order.

    Use this when you want to start processing as results stream in,
    or to see which calls are slow vs fast. Don't use this when input
    order matters in the returned list.
    """
    tasks = [ask_llm_with_retry(q, fail_rate=fail_rate) for q in questions]
    results: list[Answer] = []
    for task in asyncio.as_completed(tasks):
        answer = await task
        print(f"  ✓  {answer.text[:60]}...")
        results.append(answer)
    return results

async def run_batch_stream_with_semaphore(questions: list[Question], fail_rate: float = 0.0, semaphore_limit: int = 3) -> list[Answer]:
    """Streams: prints each answer as it arrives, returns in completion order.

    Use this when you want to start processing as results stream in,
    or to see which calls are slow vs fast. Don't use this when input
    order matters in the returned list.
    """
    semaphore = asyncio.Semaphore(semaphore_limit)
    started = time.time()
      
    async def limited_ask_llm(q: Question) -> Answer:
        async with semaphore:
            return await ask_llm_with_retry(q, fail_rate=fail_rate)

    tasks = [limited_ask_llm(q) for q in questions]
    results: list[Answer] = []
    for task in asyncio.as_completed(tasks):
        answer = await task
        print(f"  ✓  {answer.text[:60]}...")
        results.append(answer)

    elapsed = time.time() - started
    print(f"\nAll tasks completed in {elapsed:.2f} seconds.")
    return results

# ─── __main__ — switch between the two for the activity ─────────────────
if __name__ == "__main__":
    import sys

    fail_rate = float(sys.argv[1]) if len(sys.argv) > 1 else 0.0
    sample_questions = [Question(text=t) for t in [
        "What is RAG in one sentence?",
        "Name three uses of vector databases.",
        "Why might an LLM hallucinate?",
        "Explain async and await in plain language.",
        "What is the difference between a chatbot and an agent?",
    ]]
    print(f"\nrun batch stream with fail_rate={fail_rate}\n")
    #answers = asyncio.run(run_batch(sample_questions, fail_rate=fail_rate))
    #answers = asyncio.run(run_batch_stream(sample_questions, fail_rate=fail_rate))
    answers = asyncio.run(run_batch_stream_with_semaphore(sample_questions, fail_rate=fail_rate))
    print(f"\nreturned {len(answers)} answers")