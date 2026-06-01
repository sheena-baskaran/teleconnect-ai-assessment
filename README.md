# TeleConnect AI Platform — Technical Delivery Lead Assessment

**Candidate**: Sheena B.
**Date**: June 2026
**Role**: Technical Delivery Lead, AI Platform

---

## Submission Checklist

| Deliverable | Part | Weight | File |
|---|---|---|---|
| Code review — issue identification | 1 | 20% | [code_review.md](code_review.md) / [PDF](code_review.pdf) |
| Prioritised remediation plan | 1 | 10% | [code_review.md §Remediation Plan](code_review.md) |
| Process observation | 1 | 10% | [code_review.md §Process Observation](code_review.md) |
| Technical design document | 2 | 40% | [technical_design.md](technical_design.md) / [PDF](technical_design.pdf) |
| Stakeholder brief (non-technical exec) | 2 | 20% | [stakeholder_brief.md](stakeholder_brief.md) / [PDF](stakeholder_brief.pdf) |
| GitHub repo with commit history | Both | — | [commits](../../commits/main) |

All written deliverables are available as both **Markdown source** and **PDF** in this repository.

---

## Markdown Source Files

| File | Description |
|---|---|
| [code_review.md](code_review.md) | Full Part 1 deliverable — 27 issues across ML, agent orchestration, and eval |
| [technical_design.md](technical_design.md) | Full Part 2 technical design — architecture, LLM selection, eval strategy, observability, rollout, risks |
| [stakeholder_brief.md](stakeholder_brief.md) | Full Part 2 stakeholder brief — written for a non-technical executive |

---

## Commit History

| Commit | Description |
|---|---|
| `chore: add inherited TeleConnect codebase (unmodified)` | Starting point — the five files as received, before any review |
| `Part 1: code review across ML, agent, and eval domains` | Issue identification, remediation plan, process observation |
| `Part 2a: technical design — on-prem deployment architecture` | Architecture, LLM selection, eval, observability, rollout, risks |
| `Part 2b: stakeholder brief — exec approval brief` | One-page executive brief for the regulated market deployment |
| `docs: add PDF exports of all three deliverables` | PDF renders of all three documents |
| `docs: add README, .gitignore, and PDF build script` | Repo documentation and supporting files |

---

## Repository Structure

```
/
├── review_codebase/          Original inherited codebase (unmodified)
│   ├── agent.py              LLM-based retention agent with tool calling
│   ├── config.py             Platform configuration
│   ├── eval_suite.py         Agent evaluation pipeline and LLM-as-judge
│   ├── model_pipeline.py     Churn model training and serving
│   └── tools.py              Tool implementations called by the agent
│
├── code_review.md            Part 1 — Code review (Markdown source)
├── code_review.pdf           Part 1 — Code review (PDF)
│
├── technical_design.md       Part 2 — Technical design document (Markdown source)
├── technical_design.pdf      Part 2 — Technical design document (PDF)
│
├── stakeholder_brief.md      Part 2 — Executive approval brief (Markdown source)
├── stakeholder_brief.pdf     Part 2 — Executive approval brief (PDF)
│
├── build_pdfs.py             Script used to generate PDFs (ReportLab Platypus)
├── README.md                 This file
└── .gitignore
```

---

## Assessment Context

**Scenario**: Inherit the TeleConnect AI platform codebase — a churn prediction model, LLM-based retention agent, and evaluation suite — identify what needs fixing, then design how to move the entire system to a sovereign on-premise environment for a government-regulated market.

**Constraints for Part 2**:
- 4× NVIDIA T4 GPUs, 128 GB RAM, no internet access from production
- No hyperscaler cloud (AWS / Azure / GCP)
- No external API calls to OpenAI, Anthropic, or other hosted LLM providers
- All customer data and model artifacts must remain within the jurisdiction
- Sub-5-second agent response time SLA

---

## Key Decisions and Findings

**Part 1 — Code Review**

Five critical issues block deployment:
- `agent.py` global `conversation_history` leaks customer data across sessions
- `eval_suite.py` `evaluate_tool_accuracy` always returns 1.0 regardless of actual tool calls
- `model_pipeline.py` LabelEncoders discarded at training — inference cannot accept real data
- `tools.py` `predict_churn` and `lookup_customer` are incompatible end-to-end
- `config.py` API key hardcoded in source

**Part 2 — Architecture**

- **LLM**: Mistral 7B Instruct v0.3 via vLLM — fits on a single T4 at INT4 GPTQ (~4.5 GB VRAM), Apache 2.0 license, OpenAI-compatible API (agent.py requires two lines changed)
- **Eval**: Local vLLM instance on GPU 2 as judge — temperature=0, few-shot calibration, rule-based supplements for determinism
- **Observability**: Prometheus + Grafana + Loki + MLflow + PostgreSQL — all self-hosted, zero egress
- **Rollout**: 8-phase plan with independent validation gates and rollback per phase

---

## Regenerate PDFs

```bash
pip install reportlab
python build_pdfs.py
```

PDFs are built with a custom ReportLab Platypus renderer. The architecture diagram in `technical_design.pdf` (Section 2.1) is a vector drawing generated programmatically, not a screenshot.
