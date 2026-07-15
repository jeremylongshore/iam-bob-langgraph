# iam-bob-langgraph

> **Intent Agent Model (IAM)** — *not* Identity and Access Management.  
> Bob is the **reference implementation family** for IAM. These repos are different **runtimes** of the same model, not separate products.
>
> | Repo | Runtime | Status |
> |------|---------|--------|
> | [`iam-bob-adk`](https://github.com/jeremylongshore/iam-bob-adk) | Google ADK | Historical V1 |
> | [`iam-bob-pydantic`](https://github.com/jeremylongshore/iam-bob-pydantic) | Pydantic AI + LiteLLM (BYOK, MCP) | Historical V2 |
> | [`iam-bob-langgraph`](https://github.com/jeremylongshore/iam-bob-langgraph) | LangGraph | **Reserved (this repo — not built)** |
> | [`iam-bob-intendant`](https://github.com/jeremylongshore/iam-bob-intendant) | Operational worker (AGP-composed) | Live automation |

## Status

**Name reserved for IAM V3.** No implementation yet. Do not treat this as a shipped product.

When built, this will be a reference implementation of the Intent Agent Model using
[LangGraph](https://github.com/langchain-ai/langgraph).

## See also

- [iam-bob-adk](https://github.com/jeremylongshore/iam-bob-adk) — V1 (Google ADK)
- [iam-bob-pydantic](https://github.com/jeremylongshore/iam-bob-pydantic) — V2 (Pydantic AI)
- [iam-bob-intendant](https://github.com/jeremylongshore/iam-bob-intendant) — operational worker
