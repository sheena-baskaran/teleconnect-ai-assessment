# AI Platform Deployment — Approval Brief

**To**: VP of Operations
**From**: Technical Delivery Lead, AI Platform
**Date**: June 2026

---

We need your approval to deploy the AI retention platform in the new regulated market. The core constraint is straightforward: this jurisdiction does not permit customer data to leave the country, and it prohibits use of cloud providers like AWS, Azure, and GCP. We have to run everything ourselves, on hardware we own, inside the jurisdiction. This brief explains what we have decided, what the main tradeoff is, what risks we are carrying, and what we need from you.

---

## The Constraint

The regulations are not ambiguous. All customer data, all AI processing, and all infrastructure must be physically within the country at all times. Cloud providers replicate data across regions as a fundamental part of how they operate — no contractual arrangement changes that. On-premise is the only compliant path.

The three components of the platform — the churn prediction model, the retention agent, and the monitoring system — all need to move. The model and monitoring infrastructure port cleanly. The significant change is the agent.

---

## What We Are Building

We will install four AI processing servers (NVIDIA T4 GPUs, specified in the infrastructure plan) with 128 GB of memory in a local data facility. Once live, the system works the same way as our cloud deployment from a representative's perspective: they ask for a churn assessment, they get a recommendation, it arrives in under five seconds.

What changes is where the computation happens and which AI model drives it.

---

## The Tradeoff That Needs Your Attention

Our retention agent currently calls OpenAI's GPT-4 over the internet. That is not possible in an air-gapped environment. We will replace it with Mistral 7B, an open-source model that runs entirely on our local hardware — no external API calls, no licensing fees, no vendor dependency.

Mistral 7B handles structured, sequential tasks reliably. Most retention interactions fall into that category: look up the customer, assess churn risk, recommend an offer. For those cases, we expect it to perform well.

Where it falls short compared to GPT-4 is ambiguous or complex situations — an unusual account history, a customer who is negotiating rather than just at risk, cases that require reading between the lines. Those interactions will escalate to a supervisor more often than they do today. We are building that escalation path explicitly into the system, and representatives will be briefed on it before launch. Over the first 90 days we will tune the model's instructions using real interaction data from this market, which should close most of the gap.

| Situation | GPT-4 (current) | Mistral 7B (new market) |
|---|---|---|
| Standard churn risk, clear offer to make | Confident recommendation | Confident recommendation |
| Complex account history or edge case | Handles the nuance | More likely to escalate to supervisor |
| Customer negotiating, intent unclear | Reasons through it | May require human judgement |

The open-source model also eliminates ongoing per-query API fees, which compounds positively as query volume grows.

---

## Monitoring

SaaS monitoring tools route operational data to external cloud systems, which is not permitted here. We will run Grafana, Prometheus, and Loki — open-source tools that are self-hosted and widely used in regulated sectors including financial services. The team will have full real-time visibility into system health, model quality, and agent behaviour, all within the jurisdiction.

---

## Risks

**AI quality in the early weeks.** Representatives will see the agent escalate more often than they are used to. We have planned for this: escalation workflows are built in, reps will be briefed before launch, and we will review quality weekly. If quality is still insufficient at the 90-day mark, we have the option to fine-tune the model on local interaction data using the same hardware already in place. That decision will be made based on real data.

**Hardware procurement timeline.** Servers of this specification take time to procure. The longer approval takes, the tighter the launch window becomes. We will initiate procurement within 48 hours of your sign-off. Software development starts immediately in parallel, so no engineering time is wasted while the hardware is in transit.

**Undiscovered air-gapped dependencies.** Occasionally a software component has an internet dependency that only surfaces when you actually cut the network — a licence check, a driver that phones home. We use a phased rollout with validation gates between each stage so that any blocker in one phase doesn't stall the others. We have built contingency time into the schedule.

---

## What We Need From You

| Decision | What Is Needed |
|---|---|
| Capital expenditure | Purchase of 4x NVIDIA T4 GPU servers plus installation. Cost to be confirmed by procurement — this is a capital investment, not an operational expense, and has no recurring per-query fees once installed. Needs to be initiated promptly to protect the launch window. |
| Engineering timeline | 8 weeks post-hardware arrival. Weeks 1-2: infrastructure setup. Weeks 3-5: AI model and service deployment. Weeks 6-7: load testing. Week 8: production cutover. Software work starts immediately on approval. |
| Expectation setting | The agent will require more human supervision during the first 90 days. Representatives and supervisors need to be briefed before launch. This is a managed ramp, not a permanent capability gap. |
| Ongoing staffing | Approximately half a full-time ML engineer to maintain model quality, respond to monitoring alerts, and manage quarterly retraining as local interaction data accumulates. |

---

## How We Know It Is Working

By end of Month 2 post-launch: every representative gets an AI response in under 5 seconds, zero customer data has left the jurisdiction (we monitor this continuously with immediate alerts on any outbound data), and churn prediction accuracy has been validated against our existing market baseline on a held-out set. Any quality regression is surfaced to the team within 24 hours through on-premise dashboards.

---

## Common Questions

**Can we use the cloud with a special compliance agreement?**
No. The requirement is that data must not leave the jurisdiction, not merely that it must be handled carefully. Cloud providers replicate data across regions at the infrastructure level — contracts don't change the underlying architecture.

**What if the AI quality is still not good enough after 90 days?**
The same hardware runs both inference and, if needed, fine-tuning. We can train the model on local interaction data to adapt it specifically to this market's customer patterns. The 90-day monitoring period gives us the data to make that call with evidence rather than guesswork.

**What if the hardware fails?**
One of the four GPUs is reserved as a failover. If the primary service encounters a hardware fault, traffic shifts to it without restarting. This is part of the deployment design, not an afterthought.

**Can this architecture apply to other regulated markets?**
Yes. Once the design and runbooks exist for this market, subsequent deployments follow the same pattern with significantly less engineering effort.

---

We are ready to move on this as soon as we have your approval.
