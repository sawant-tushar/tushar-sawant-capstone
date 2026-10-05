# ADR-0001: Capstone Framing — Postman Documentation Assistant

* **Status:** Draft v1
* **Date:** 2026-10-05
* **Author:** Tushar Sawant

## Context

Postman provides extensive documentation covering API requests, collections, variables, environments, authentication, scripting, testing, mock servers, and CLI usage, making it difficult for users to quickly find the precise information they need. This capstone will build a Retrieval-Augmented Generation (RAG) assistant that answers Postman-related questions using a controlled corpus of official Postman documentation and provides source citations so users can verify the answers.

## Decision — Solution Framing Canvas

| Question                     |  Answer                                                                                                                                                                                                                                             |
| ----------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Inputs**              | The user submits a natural-language question about Postman concepts, features, configuration, testing, scripting, or API workflows.                                                                                                                     |
| **Outputs**             | The system returns a concise, grounded answer with citations pointing to the relevant Postman documentation used to generate the response.                                                                                                              |
| **Tools**               | The system will use an LLM for answer generation, a document-processing and chunking pipeline, an embedding model, and a vector store/retriever for searching the selected Postman documentation corpus.                                                |
| **Memory**              | Version 1 will not retain conversation history or user-specific information between sessions; each question will be treated as an independent query.                                                                                                    |
| **Autonomy level**      | The system is a grounded Q&A assistant that retrieves information and generates answers but does not perform actions in Postman or make autonomous changes to APIs, collections, environments, or other systems.                                        |
| **Decision boundaries** | The system may answer questions when relevant information can be retrieved from the approved Postman corpus, but it must acknowledge insufficient evidence and avoid guessing when the corpus does not contain enough information to support an answer. |

## Consequences

* **Positive:**

  * Provides a focused way to find relevant information across the selected Postman documentation without manually searching multiple pages.
  * Grounding responses in an approved documentation corpus and providing citations improves answer traceability and makes the system easier to evaluate.
  * The controlled corpus provides a well-defined environment for measuring retrieval quality, answer relevance, citation accuracy, and hallucination.

* **Negative / risks:**

  * The assistant is limited by the coverage, quality, and freshness of the selected Postman documentation corpus and may not answer questions outside its scope.
  * Incorrect chunking, embeddings, retrieval, or source selection could result in incomplete or inaccurate answers even when the underlying documentation contains the correct information.
  * Maintaining citations and ensuring that generated answers remain grounded adds complexity compared with a simple LLM-based chatbot.

* **Things we'll re-visit:**

  * Retrieval strategy, chunking approach, embedding model, and confidence/relevance thresholds will be evaluated and refined in later ADRs.
  * Conversation memory, broader Postman documentation coverage, and potentially multi-turn questions will be considered after the core single-query RAG workflow is validated.
