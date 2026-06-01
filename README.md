# TeleConnect AI Platform — Technical Delivery Lead Assessment

**Candidate**: Sheena B.
**Date**: June 2026
**Role**: Technical Delivery Lead, AI Platform

---

## What This Is

This repository is my submission for the TeleConnect Technical Delivery Lead assessment. The task was to inherit a codebase spanning traditional ML, agent orchestration, and LLM evaluation; identify what matters; then design how to move the system to an air-gapped, on-premise environment and get a non-technical executive to sign off on the plan.

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
├── code_review.md            Part 1 — Code review deliverable
├── technical_design.md       Part 2 — Technical design document
├── stakeholder_brief.md      Part 2 — Executive approval brief
│
├── code_review.pdf           PDF version of code review
├── technical_design.pdf      PDF version of technical design
├── stakeholder_brief.pdf     PDF version of stakeholder brief
│
└── build_pdfs.py             Script used to generate PDFs (ReportLab)
```

---

## Deliverables

| Document | Part | Weight | Description |
|---|---|---|---|
| `code_review.md` | 1 | 40% | Issue identification (27 issues across all three domains), prioritised two-sprint remediation plan, and process observation |
| `technical_design.md` | 2 | 40% | On-prem architecture, LLM selection and hosting, eval strategy in closed environment, observability stack, phased rollout with rollback, risks and open questions |
| `stakeholder_brief.md` | 2 | 20% | One-page exec brief: what is being built, key tradeoffs in business terms, risks, and what the executive is being asked to approve |

PDFs are provided alongside each Markdown file. Content is identical.

---

## Part 1 Summary — Code Review

Reviewed five files across three domains. Found 5 critical issues that block deployment, 8 high-severity issues that cause incorrect results in production, and several medium/low items tracked as debt.

The most significant issues:
- **agent.py**: Global `conversation_history` leaks customer data across sessions (privacy violation)
- **eval_suite.py**: `evaluate_tool_accuracy` always returns 1.0 — the team believes they have 100% tool accuracy when the metric is completely fabricated
- **model_pipeline.py + tools.py**: LabelEncoders discarded at training time, never saved. Serving pipeline cannot accept real customer data.
- **tools.py**: `get_retention_offers` ignores its `risk_tier` parameter and returns all offers unconditionally

Remediation is scoped to two engineering sprints before the on-prem migration.

---

## Part 2 Summary — On-Prem Architecture

**Constraint**: Government-regulated market. No hyperscaler cloud (AWS/Azure/GCP). All data must remain in-jurisdiction. No external API calls. Hardware: 4× NVIDIA T4 GPUs, 128 GB RAM.

**Key decisions**:
- **LLM**: Mistral 7B Instruct v0.3 via vLLM — fits on a single T4 at INT4 quantization (4.5 GB VRAM), Apache 2.0 licensed, exposes an OpenAI-compatible API (agent.py needs two lines changed)
- **Eval in air-gapped environment**: Local vLLM instance on GPU 2 as judge; temperature=0 for deterministic scoring; few-shot calibration examples; supplemented with rule-based checks
- **Observability**: Prometheus + Grafana + Loki + MLflow + PostgreSQL — all self-hosted, zero egress
- **Rollout**: 8-phase plan with independent validation gates and rollback per phase

---

## Assumptions

- Hardware specified in the assessment (4× T4, 128 GB RAM) is the deployment target
- The regulatory requirement is strictly data residency — no additional constraints on open-source software supply chain
- The local LLM can be updated during planned maintenance windows without full deployment pipeline approval
- An existing ML engineer can be partially allocated to this market for ongoing maintenance

---

## PDF Generation

PDFs were built using a custom ReportLab Platypus renderer (`build_pdfs.py`). The architecture diagram in `technical_design.pdf` (Section 2.1) is a vector drawing, not a screenshot.

To regenerate:
```bash
pip install reportlab
python build_pdfs.py
```
