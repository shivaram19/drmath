# ADR-024: WhatsApp Channel Choice, Consent Model, and Data Retention for Daily Quiz Reminders

**Date:** 2026-05-05  
**Scope:** Backend architecture and compliance model for Phase 10.9 — sending daily nursing-quiz reminders over WhatsApp to opted-in users in India.  
**Research Phase:** Bidirectional / cross-domain impact analysis (technology + DPDPA compliance).  
**Status:** Proposed.  
**Tracked in:** #52

---

## Context

Phase 10.9 proposes a **WhatsApp daily quiz reminder** experiment for the nursing module. The hypothesis is that a low-friction, push-style nudge on a channel the learner already checks will improve daily practice adherence more than email or in-app notifications alone.

WhatsApp dominates Indian messaging: it is the #1 channel in India, used by ~70% of the addressable population and an estimated 550–850 million users nationwide [^1][^2]. For adult women preparing for nursing entrance exams — a cohort with high time poverty and frequent household interruptions — WhatsApp is often the only channel they reliably monitor [^3].

Before writing any bot code or scheduler, we must decide:

1. **Channel / BSP:** Meta Cloud API directly, or a Business Solution Provider (BSP) such as Chat Mitra?
2. **Consent model:** How do we collect, record, and withdraw consent in a way that satisfies both Meta policy and India’s Digital Personal Data Protection Act, 2023 (DPDPA)?
3. **Data retention:** How long do we keep phone numbers, consent records, send logs, and analytics events?
4. **Reversal trigger:** At what cost/engagement threshold do we stop the experiment?

---

## Decision

### 1. Channel: Chat Mitra Pro as primary BSP; Meta Cloud API direct as fallback

Use **Chat Mitra Pro** as the primary WhatsApp Business API provider for the experiment.

| Factor | Chat Mitra Pro | Meta Cloud API direct |
|---|---|---|
| Monthly platform fee | ₹999/month | ₹0 |
| Per-message platform fee | ₹0.20/conversation + Meta rates [^4] | Meta rates only |
| Meta India utility rate (reminder) | ~₹0.11–0.16 per delivered template [^5][^6] | ~₹0.11–0.16 per delivered template [^5][^6] |
| Engineering setup | Low — BSP handles WABA onboarding, template submission, webhooks [^4] | High — we build template orchestration, webhook handling, number management |
| Time to first message | ~30 minutes guided onboarding [^4] | 2–6 weeks typical engineering effort [^6] |
| Support | Phone / WhatsApp / email (India-based) [^4] | Self-service / partner-only |
| Template approval | Managed via BSP dashboard | Direct via Meta Business Manager |

**Rationale:** Phase 10.9 is an experiment, not a committed product lane. We optimize for **time-to-validated-learning**, not lowest marginal cost at scale. Chat Mitra Pro removes the upfront engineering tax of direct Cloud API integration, provides India-based support, and still passes Meta’s rates through without markup. If the experiment reaches steady state and volume justifies it, we can later migrate to direct Cloud API to eliminate the ₹999/month + ₹0.20 platform fee.

**Fallback:** If Chat Mitra onboarding or template approval stalls beyond one week, switch evaluation to **Meta Cloud API direct**.

### 2. Message category: Utility for pure reminders; Marketing only with separate consent

Daily quiz reminders are **utility messages** (appointment/event reminders) because they notify the user of an available daily learning activity they have explicitly signed up for. If future messages include promotional content (e.g., “Upgrade to full course”), they must be sent as **marketing** templates and require a separate, explicit marketing consent.

Every template footer must include:  
`“Reply STOP to unsubscribe.”` [^7][^8]

### 3. Consent model: explicit opt-in + confirmation + easy withdrawal

We implement a **two-step opt-in**:

1. **Primary opt-in:** On the nursing PWA or web landing page, the user checks a clearly labeled checkbox that names Dr. Math, describes the daily reminder, states the approximate frequency, and notes the STOP instruction.
2. **Confirmation opt-in:** We send a WhatsApp message asking the user to reply `YES` to confirm. We do not send daily reminders until `YES` is received.

We store a **consent artifact** per user:

```json
{
  "phone_hash": "sha256:+91xxxxxxxxx",
  "consent_version": "2026-05-05",
  "channel": "whatsapp",
  "purpose": "daily_quiz_reminder",
  "source": "nursing_web_optin",
  "opted_in_at": "2026-05-05T09:00:00Z",
  "confirmed_at": "2026-05-05T09:05:00Z",
  "withdrawn_at": null
}
```

**Withdrawal:** Any incoming message matching `STOP`, `UNSUBSCRIBE`, or similar Hindi/Telugu keywords immediately sets `withdrawn_at` and suppresses all future sends. We reply once to confirm unsubscribe and then stop [^7][^8]. Re-subscription requires a fresh explicit opt-in; a simple `START` does **not** automatically re-enroll a withdrawn user.

This aligns with DPDPA requirements that consent be free, specific, informed, unconditional, and unambiguous, and that withdrawal be as easy as giving consent [^9][^10].

### 4. Data retention

| Data | Retention | Rationale |
|---|---|---|
| Raw phone numbers | **Never stored.** Only SHA-256 hashes are kept. | Minimizes PII and limits breach impact. |
| Consent artifacts | **1 year after opt-out or purpose end.** | DPDPA allows retention where necessary for legal claims; 1 year balances auditability with minimization [^11]. |
| Message send logs | **30 days.** | Enough to debug delivery and measure engagement; then purged. |
| Analytics events (anonymous) | **30 days.** | Matches existing nursing analytics retention policy. |
| STOP/withdrawal logs | **1 year.** | Legal defense against claims of non-compliance. |

We do **not** share phone numbers or consent records with Chat Mitra beyond what is technically required to deliver messages. We do **not** use the phone list for advertising or sell it.

### 5. Cost / engagement reversal trigger

Pause the experiment automatically if any of the following thresholds are crossed after at least **100 delivered reminder messages**:

- **STOP/unsubscribe rate > 5%** — indicates consent quality or frequency problem.
- **Open/engagement rate < 15%** — indicates channel-message fit is poor.
- **Cost per active daily user > ₹5** for two consecutive weeks — indicates the reminder is not converting to practice.

When triggered, we halt new sends, review the consent flow and message copy, and decide whether to iterate, pivot to another channel, or terminate the experiment.

---

## Consequences

### Positive

- **Fast validation:** Chat Mitra Pro should let us send the first reminder within days, not weeks.
- **Compliance by design:** Explicit double opt-in, STOP handling, and short retention periods satisfy Meta policy and DPDPA.
- **Reversible:** The reversal trigger prevents runaway spend on a channel that does not move the learning metric.
- **Aligned with existing architecture:** The new `AnalyticsSink` port can absorb WhatsApp engagement events; `NursingService` can be extended with a reminder subscription service.

### Negative

- **Higher per-message cost than direct Cloud API:** ~₹0.20 platform fee per conversation on top of Meta rates.
- **Vendor dependency:** Template approval and number management are partly gated by Chat Mitra; migration later requires work.
- **Consent friction:** Double opt-in will reduce conversion vs. single opt-in, but is necessary for compliance and list quality.

### Neutral

- We will need a new `WhatsAppSender` port/adapter if we later swap BSPs or go direct.
- We will need a lightweight scheduler (cron or APScheduler) and a webhook endpoint for inbound STOP/YES messages.

---

## Alternatives Considered

1. **Meta Cloud API direct (primary).** Rejected for the experiment because the upfront engineering and onboarding time (2–6 weeks) exceeds our target time-to-learning. Kept as fallback.
2. **SMS instead of WhatsApp.** Rejected: SMS has lower engagement, higher spam perception, and no native interactive opt-out/confirmation flow in the same channel.
3. **In-app push notifications only.** Rejected: the target learners may not open the app daily; the experiment specifically tests whether an external nudge improves adherence.
4. **Single opt-in (no YES confirmation).** Rejected: double opt-in materially improves consent quality, reduces block rates, and is safer under DPDPA’s “free and informed” standard [^9].
5. **Store raw phone numbers.** Rejected: hashing is sufficient for duplicate suppression and delivery; storing raw numbers increases compliance burden without benefit.

---

## Council of Ten Deliberation Summary

- **Research Scientist:** Decision is anchored in India-specific messaging penetration data and DPDPA/Meta policy sources, not vendor marketing alone.
- **First-Principles Engineer:** Consent is treated as a first-class entity with an artifact, not a boolean flag.
- **Distributed Systems Architect:** A `WhatsAppSender` port will let us swap Chat Mitra for direct Cloud API without touching the scheduler or consent service.
- **Infrastructure-First SRE:** Reversal trigger and 30-day log retention limit blast radius and observability cost.
- **Ethical Technologist:** No PII retention, explicit opt-in, and easy withdrawal respect learner autonomy.
- **Resource Strategist:** ₹999/month + usage is acceptable for an experiment; direct Cloud API migration is deferred until unit economics justify it.
- **Diagnostic Problem-Solver:** Reversal trigger targets the root question — does the reminder actually increase daily practice? — not vanity send volume.
- **Curious Explorer:** BSP evaluation is documented; fallback path is explicit.
- **Clarity-Driven Communicator:** ADR makes channel, consent, retention, and reversal criteria explicit before code is written.
- **Inner-Self Guided Builder:** The learner’s inbox is protected by strict opt-in and STOP handling; we do not optimize engagement at the cost of trust.

---

## References

[^1]: Infobip. (2026, June 19). *Research: The most popular messaging apps by country*. https://www.infobip.com/blog/most-popular-messaging-apps-by-country

[^2]: SQ Magazine. (2026, June 2). *WhatsApp Statistics 2026: Messaging Volumes, Calls, Business Use & More* (Resourcera data). https://sqmagazine.co.uk/whatsapp-statistics/

[^3]: WeddingWire India. (2024). *The Newly Wed Survey Report 2024-2025* — 58.6% of couples use WhatsApp for all wedding-related communication. https://www.weddingwire.in/wedding-tips/annual-wedding-industry-report--c11025

[^4]: Chat Mitra. (2026). *Chat Mitra Pricing 2026*. https://chatmitra.com/pricing/

[^5]: Leads Loom. (2026, June 13). *WhatsApp Business API: The Complete 2026 Setup, Pricing & Integration Guide*. https://www.leadsloom.in/blog/whatsapp-business-api

[^6]: Message Central. (2026, April 24). *WhatsApp Business API 2026: Complete Guide to Setup, Cloud API, Chatbots, Pricing and BSPs*. https://www.messagecentral.com/blog/whatsapp-business-api-complete-guide

[^7]: Blueticks. (2026, June 23). *WhatsApp Opt-In Compliance Requirements: Meta's Rules for Collecting Consent Without Getting Flagged*. https://blueticks.co/blog/whatsapp-opt-in-compliance-requirements

[^8]: Infobip. (2026, June 18). *WhatsApp opt-in: Policy requirements & collection strategies*. https://www.infobip.com/blog/how-to-collect-whatsapp-business-opt-ins

[^9]: Digital Personal Data Protection Act, 2023, No. 22, Acts of Parliament, 2023 (India). Sections 6–8 (consent, withdrawal, erasure).

[^10]: Cyril Shroff & Partners. (2025, December 7). *FAQs - The Digital Personal Data Protection Act, 2023* — withdrawal and erasure obligations. https://www.cyrilshroff.com/wp-content/uploads/2025/12/FAQs-DPDPA.pdf

[^11]: King, Stubb & Kasiva. (2025, November 25). *Data Retention, Deletion, And Log Management Under The DPDP Act, 2023 And DPDP Rules, 2025* — Rule 8 one-year log retention and deletion notice. https://www.mondaq.com/india/privacy-protection/1710314/data-retention-deletion-and-log-management-under-the-dpdp-act-2023-and-dpdp-rules-2025-navigating-operational-complexities-and-building-compliance-ready-data-architectures
