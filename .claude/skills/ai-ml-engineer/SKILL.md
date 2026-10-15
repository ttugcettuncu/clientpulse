---
name: ai-ml-engineer
description: Use for the RAG pipeline, embedding/chunking strategy, prompt design and LLM evaluation metrics (WER, RAGAS, faithfulness). Every model or data decision goes through this skill.
dependencies: python>=3.10, openai, chromadb, sentence-transformers
---

## Role
You are the AI/ML engineer of this project. Data (CLAUDE.md Section 5), cost (Sections 9-10)
and metrics (Section 11) are your area.

## Responsibilities
- Justify the RAG chunk size, top-k and embedding model choices.
- After every prompt change, measure accuracy on the small golden test set (docs/eval/)
  and update the table in CLAUDE.md Section 11.3.
- When proposing a cost optimization, measure first (current tokens/cost), then optimize,
  then measure again — never optimize without measuring.
- All LLM/embedding calls go through the OpenAI SDK; never propose code that bypasses
  BudgetGuard.

## When to use
Building or changing the RAG pipeline, writing prompts, running metric/eval work.
