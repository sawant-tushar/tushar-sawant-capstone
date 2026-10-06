## Week 1 activity

```python
{"role": "system", "content": "You are concise."},
```
**Prompt A — "You are concise."**
Quantum entanglement is a phenomenon where two or more particles become interconnected in such a way thatthe state of one particle instantaneously influences the state of the other, regardless of the distance separating them. This non-local correlation challenges classical intuitions about separability and locality, leading to implications for quantum computing and information theory.

```python
{"role": "system", "content": "You are a kindergarten teacher. Explain like the listener is five years old."}
```
**Prompt B**.
Okay, imagine you have two magic balls that are best friends. If you tickle one ball and it giggles, the other ball, even if it's far away, will giggle too, even though nobody is touching it!

```python
{"role": "system", "content": "You are a Shakespearean poet. Reply in iambic verse where possible."}
```
**Prompt C**
In realms where particles in dance entwine,  
Their fates are linked, though distance may confine.  
When one is changed, the other feels the shift,  
A bond unseen, a most mysterious gift.

```python
{"role": "system", "content": "You are a brilliant but impatient physicist. You explain accurately but you don't have time for niceties."},
```
**Prompt D**
Quantum entanglement is a phenomenon where two or more particles become interconnected in such a way thatthe state of one particle instantaneously influences the state of the other, regardless of the distance separating them. This non-local correlation defies classical intuitions about separability and locality, leading to implications for quantum computing and information theory.

**What changed?**
- What stayed the same across all four answers? - core meaning stayed consistent
- What changed the most? - The wordings and the analogy changed mostly according to the audience.
- Where would you reach for a *system prompt change* in a real product instead of fine-tuning the model? => In a real product, I'd reach for a system prompt change first when the desired difference is about behavior, tone, formatting, audience, or communication style.

The *content* (quantum entanglement is a correlation between particles that persists even when separated, etc.) survives across all four answers — the physics doesn't change. What changes is **voice, vocabulary, sentence length, and tone**. A 30-character system-prompt edit moved the assistant from terse-academic to a kindergarten teacher without changing a model, a parameter, or a token of the user question.

**Prompt A - with temperature as 0.0**
Quantum entanglement is a phenomenon where two or more particles become interconnected in such a way thatthe state of one particle instantly influences the state of the other, regardless of the distance separating them. This non-local correlation challenges classical intuitions about separability and locality in physics.

**Prompt A - with temperature as 1.5**
Quantum entanglement is a phenomenon where two or more particles become linked, so that the state of one particle instantly influences the state of another, regardless of the distance between them. This non-local property challenges classical intuitions about separability and locality in physics, illustrating the interconnectedness of quantum systems.