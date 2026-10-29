# RAG API Stress and Robustness Test Report

## Finding 1 — Malformed JSON

Four malformed or invalid JSON inputs were tested against the FastAPI endpoint to evaluate request validation and error handling. The HTTP response codes observed were: 

# Case 1 — empty body #
curl -i -X POST http://localhost:8000/ask \ -H "Content-Type: application/json" \ -d '{}'
Output - **HTTP/1.1 422 Unprocessable Content**, 

# Case 2 — wrong field name (typo)
curl -i -X POST http://localhost:8000/ask \ -H "Content-Type: application/json" \ -d '{"q": "What is the leave policy?"}'
Output - **HTTP/1.1 422 Unprocessable Content**, 

# Case 3 — wrong type (int instead of str)curl -i -X POST http://localhost:8000/ask \ -H "Content-Type: application/json" \ -d '{"question": 42}'
Output - **HTTP/1.1 422 Unprocessable Content**, 

# Case 4 — malformed JSON (missing closing brace)curl -i -X POST http://localhost:8000/ask \ -H "Content-Type: application/json" \ -d '{"question": "What is the leave policy?"'
Output - **HTTP/1.1 422 Unprocessable Content**, 
error : "Expecting property name enclosed in double quotes"

Requests rejected during JSON parsing or request validation should be distinguished from requests that reached the endpoint handler. This test helps establish whether invalid requests are handled safely without causing unexpected application errors.

## Finding 2 — 5000-Character Question

A question containing 5,000 characters was submitted to the API. The total wall time observed was 6 seconds. The API did not encounter a token limit, based on the response and application logs. Streaming worked, and the response was completed successfully. This test evaluates how the API handles unusually long questions, including processing latency, model input limits, and response delivery behaviour.

## Finding 3 — Disconnect Mid-Stream

A client disconnect was simulated using `curl` with `--max-time 1` while the API was processing or streaming a response. The server logged Operation timed out after 1011 milliseconds with 52 bytes received. After the client disconnected, the `/health` endpoint continued to respond successfully. This test checks whether a disconnected client is handled cleanly and whether the interruption affects the availability of the API for subsequent requests. The observed logs should also establish whether streaming or background processing continued after the client disconnected.

## Finding 4 — 50 Parallel Requests

The stress test was executed with 50 total requests and a concurrency limit of 10 using `python scripts/stress_test.py --requests 50 --concurrent 10`. The API completed all  successful requests out of 50 requests. The observed p50 latency was 1.70 seconds, the p95 latency was 2.36 seconds, and the effective throughput was 5.30 requests per second. SQLite captured all 50 request entries, based on a comparison between the test results and database records. These measurements provide an indication of the API's response latency, throughput, error rate, and persistence reliability under concurrent load.

Total wall time:   9.43s
Successes:         50 / 50
Effective req/s:   5.30

Latency (successful requests):
  min:   1.05s
  p50:   1.70s
  p95:   2.36s
  max:   2.58s

## Known Limits / Follow-ups

- **Token-limit handling:** Add or verify input-length validation, token counting, and clear error responses for questions that exceed the model's context limit.
- **SQLite write contention:** Verify that concurrent requests do not cause database locking, dropped records, or incomplete writes. Consider transaction handling, a busy timeout, or a different persistence approach if contention becomes significant.
- **Cost tracking:** Record estimated or actual model usage and cost per request where provider usage data is available, including appropriate handling of failed requests.
- **Streaming disconnects:** Confirm that client disconnections release resources and that cancellation is propagated appropriately.
- **Observability:** Retain request IDs, HTTP status codes, latency measurements, and relevant error logs to make failures easier to investigate.
