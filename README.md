# Capstone — Knowledge Assistant

A 30-week build of a Q&A assistant over a small document corpus, completed as part of
the *Agentic AI & RAG Engineering* programme.

## Corpus

My capstone corpus: Postman official documentation (12 documents covering API requests, responses, collections, variables, environments, authentication, scripting, API testing, collection execution, mock servers and Postman CLI). Source: https://learning.postman.com/docs/

## Structure

- `src/` — application code
- `docs/adr/` — Architecture Decision Records (one per major design choice)
- `docs/runs/` — saved LLM outputs for evidence and reference

## Week 1

- [x] Set up repo + secrets discipline
- [ ] Build `hello_llm.py` (Lab Step 2)
- [ ] Write ADR v1 (Lab Step 3)

## Expected scaffold:

tushar-sawant-capstone/
├── .gitignore
├── README.md
├── docs/
│   ├── adr/
│   │   └── .gitkeep
│   └── runs/
│       └── .gitkeep
└── src/
    └── .gitkeep