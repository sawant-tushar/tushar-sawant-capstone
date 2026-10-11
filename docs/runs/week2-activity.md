## Week 2 activity

**Gather vs as_completed**
What did `as_completed` make visible that `gather` hides?
> `gather` returns all results in input order at the moment the
> slowest call finishes. `as_completed` shows me the actual finish
> order, so I can see which calls are slow and which are fast.

when would you reach for `gather`, and when for `as_completed`?
> `gather` when I need all results before continuing (most pipelines,
> including the W2 lab). `as_completed` when I want to start
> processing as results stream in — streaming-to-UI, early stopping
> on first match, or surfacing the fastest answer.

## What we noticed

When you ran with `fail_rate=0.4`, the questions that needed a retry arrived **after** the others — sometimes seconds later — even though they were submitted at the same time. With `gather`, you couldn't have *seen* this: gather returns everything in one batch, in input order, when the slowest call finishes. With `as_completed`, the slowest call is visibly the slowest, and the fastest is visibly the fastest.

This is the engineering question: **when do you want the order, and when do you want the speed?**

- Use **`gather`** when you need all results before doing the next thing (90% of pipelines — including the W2 lab).
- Use **`as_completed`** when you want to start *processing* as results stream in, or to bail early on a first match (e.g., search ranking, "stop on first good answer", streaming-to-UI).

## What I observed

- `as_completed` made the **order of completion visible**. With
  `fail_rate=0.4`, the two answers that retried arrived last —
  several seconds after the others — proving the retry backoff was
  real, not just folklore. `gather` would have hidden this completely
  by returning everything in one batch at the end.
- I'd use **`gather`** when I need all results before doing the next
  thing (most pipelines, including the W2 lab itself — the
  aggregation step needs all 5 answers). I'd use **`as_completed`**
  when I want to stream results to a UI as they arrive, or to bail
  early when the first acceptable answer comes back (e.g., search
  ranking where any decent hit is enough).
