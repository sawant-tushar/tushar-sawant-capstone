## Week 2 activity

### The reflection

**Q1:** *"What's lost if the process restarts?"*

> The entire `request_counts` dict lives in memory. Kill the process,
> the counts go to zero. A real metrics system (Prometheus, StatsD)
> persists outside the process — usually by scraping or pushing
> values to a durable store.

**Q2:** *"Under heavy concurrency, would two simultaneous requests to
`/health` always result in the counter going from N to N+2?"*

> Not guaranteed. Two coroutines could both read the same value of
> `count`, both compute `count + 1`, both write that — losing one
> increment. Python's GIL makes this unlikely in single-process
> uvicorn but doesn't *guarantee* it; with multiple workers or
> heavy CPU concurrency, you'd see lost counts. Real systems use
> atomic counters (`threading.Lock`, `Redis INCR`, etc.).


## What to look for in submissions

**Strong signals:**
- Middleware is registered with `@app.middleware("http")`
- Counter dict initialised correctly (with `.get(path, 0) + 1`)
- `/metrics` returns the dict + a `total` (showing they sum the
  values, not just dump the dict)
- Reflection explicitly names both limitations (persistence +
  atomicity)

**Weak signals:**
- Decorator on every endpoint instead of middleware (defeats the
  separate-concern point)
- Counter on each endpoint manually (same issue)
- Reflection that only notes "it works" without identifying the
  trade-offs

**Common mistakes:**
- Forgets `await call_next(request)` — every endpoint returns None
  because the middleware doesn't pass through
- Uses a list instead of dict — can't query per-path counts
- `/metrics` excludes itself from the counter without justification
  (this is *defensible* but should be a deliberate choice, not an
  accident)
  

## Output
`/metrics` response look like this:
{
  "endpoints":
  {
    "/health":{"total_requests":2,"status_codes":{"200":2},"total_latency_seconds":0.0018,"mean_latency_seconds":0.0009},
    "/ask_batched":{"total_requests":5,"status_codes":{"422":4,"200":1},"total_latency_seconds":0.3956,"mean_latency_seconds":0.0791},
    "/ask":{"total_requests":1,"status_codes":{"200":1},"total_latency_seconds":0.0039,"mean_latency_seconds":0.0039}
  },
  "total_requests":8
}