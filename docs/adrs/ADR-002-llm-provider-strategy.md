# ADR-002: LLM Provider Strategy

**Date:** 2026-05-03  
**Scope:** Content generation and adaptation  
**Research Phase:** BFS completed; DFS on Azure OpenAI deployment pending  
**Status:** Accepted

## Context

The pipeline requires an LLM for two distinct tasks:
1. **Content adaptation:** Transform scraped MathIsFun HTML into age-appropriate, culturally localized lesson text (~2K–4K tokens).
2. **Question generation:** Produce 40 structured MCQs per topic with explanations (~6K–12K tokens).

Total cost per topic: ~16K tokens. At scale (hundreds of topics), provider selection directly impacts TCO and latency.

## Decision

Design a **provider-agnostic LLM client** with three backends:
1. **Primary:** OpenAI GPT-4o-mini (best cost/quality ratio for our token volumes).
2. **Secondary:** Azure OpenAI (enterprise compliance, credits available).
3. **Tertiary:** Grok/xAI (fallback, currently credit-limited).

Provider selection via `LLM_PROVIDER` env var; client initialized at runtime.

## Consequences

**Positive:**
- GPT-4o-mini at ~$0.15/M input + $0.60/M output tokens is cost-optimal for structured generation [^1].
- Azure endpoint provides data residency and SLA guarantees for production.
- Abstraction allows A/B testing providers without code changes.

**Negative:**
- Azure deployment naming differs from model names; requires `AzureOpenAI` client class.
- Grok API key hit credit exhaustion during testing; unreliable as primary.

## Alternatives Considered

| Alternative | Rejected Because |
|-------------|-----------------|
| Local LLM (Llama 3, Mistral) | Hardware requirements exceed VM capacity; 70B model needs 40GB+ VRAM |
| Claude 3 Opus | 10x cost of GPT-4o-mini for marginal quality improvement on structured JSON tasks |
| Single-provider lock-in | Violates Resource Strategist persona; no failover if provider degrades |

## References

[^1]: OpenAI Pricing. https://openai.com/api/pricing/ (accessed 2026-05-03).
