# ADR-024: WhatsApp + Telegram Channel Strategy, Consent Model, and Data Retention for Daily Quiz Nudges

**Date:** 2026-05-05  
**Scope:** Backend architecture and compliance model for Phase 10.9 — a behaviorally-designed, dual-channel daily-quiz experiment using WhatsApp and Telegram for opted-in nursing learners in India.  
**Research Phase:** Bidirectional / cross-domain impact analysis (technology + DPDPA compliance + behavioral-science mechanism design + 2026 channel economics).  
**Status:** Proposed.  
**Tracked in:** #52

---

## Context

Phase 10.9 proposes a **daily quiz nudge** experiment for the nursing module. The original hypothesis was that a low-friction, push-style reminder on WhatsApp would improve daily practice adherence more than email or in-app notifications alone.

WhatsApp dominates Indian messaging: India is its largest single-country market, with 535.8 million monthly active users (DataReportal early 2025) and Meta’s own figure of 500 million+ as of late 2024 [^12][^13]. For adult women preparing for nursing entrance exams — a cohort with high time poverty and frequent household interruptions — WhatsApp is often the only channel they reliably monitor.

However, new evidence challenges the "reminder = behavior change" assumption. A Punjab-based RCT (*N* = 388) found that WhatsApp reminders combined with health-misconception debunking did **not** significantly increase hypertension follow-up attendance (2.2 pp effect, *p* = 0.603) [^14]. Conversely, education-specific nudges show mixed-but-promising results when they contain actionable content, active engagement, or social accountability [^15][^16][^17]. This means Phase 10.9 must be designed as a **behavioral-intervention experiment**, not just a delivery-channel experiment.

The question then arose: should the experiment also run on **Telegram**? Telegram has 104 million monthly active users in India, is heavily used in exam-prep and job-alert communities, and offers a free Bot API with native quiz/poll support [^18][^19][^20]. But in June 2026 the Indian government temporarily blocked Telegram nationwide under Section 69-A of the IT Act to combat NEET-UG 2026 exam fraud [^26][^27][^28]. This confirms both Telegram's relevance to exam aspirants and a material platform-level regulatory risk.

Fresh research surfaced two additional product-strategy unknowns. First, the nursing exam-prep market is already crowded: Physics Wallah runs a dedicated Nursing vertical with 21 batches, 600+ lectures, and 5,000+ practice questions for NORCET, RRB Staff Nurse, NHM-CHO, and state exams [^31]. Dr. Math’s 5-question quiz is therefore a micro-habit layer, not a course substitute. Second, spaced microlearning has specific support in nursing education: a 2024 RCT on nurse-anesthesia students found spaced lectures significantly improved retention compared with conventional lectures [^32], and a review of microlearning notes 16–25% recall gains from spaced quizzes [^33]. These findings reinforce that Phase 10.9 must be a high-fidelity behavioral experiment, not a novelty feature, and that the daily nudge needs a syllabus-aligned content base before launch.

Before writing any bot code or scheduler, we must decide:

1. **Channels:** WhatsApp only, Telegram only, or dual-channel opt-in?
2. **Behavioral mechanism:** What message design will we test against a generic reminder control arm?
3. **BSP / API model:** Chat Mitra vs. direct Meta Cloud API for WhatsApp; Telegram Bot API details.
4. **Consent model:** How do we collect, record, and withdraw consent across two channels in a way that satisfies Meta policy, Telegram Terms of Service, and India’s DPDPA, 2023?
5. **Data retention:** How long do we keep identifiers, consent records, send logs, and analytics events?
6. **Reversal / fallback triggers:** At what cost/engagement threshold do we stop, and how do we handle a channel outage or ban?

---

## Decision

### 1. Channels: dual-channel opt-in with WhatsApp as the regulated fallback

We will run Phase 10.9 as a **dual-channel opt-in experiment**. The learner chooses her preferred channel — WhatsApp or Telegram — during opt-in. The same control/treatment arms run within each channel.

| Factor | WhatsApp | Telegram |
|---|---|---|
| India reach (2026) | ~535.8M MAU; largest single-country WhatsApp base [^12] | ~104M MAU; largest country base for Telegram [^18] |
| Gender split (India/global) | ~52% male / 48% female [^12] | ~57% male / 43% female [^19] |
| Exam-prep presence | Universal personal/family channel | Job/exam sites (GNM jobs, state nursing entrances) promote Telegram channels [^20][^21] |
| API cost | Per delivered template message: ~₹0.115 utility / ~₹0.8631 marketing (2026 India) [^22][^23] | Free Bot API; only hosting + optional paid broadcast [^24][^25] |
| Interactive quiz support | Templates with reply buttons / text replies | Native polls/quizzes with instant feedback [^24] |
| Regulatory risk in India | Stable, widely used for government and business messaging | Temporary nationwide ban June 16–22, 2026 under Section 69-A IT Act [^26][^27] |
| Identifier used | Phone-number hash (`+91...`) | Telegram `chat_id` hash |

**Rationale:**
- **WhatsApp** is the safer default: broader reach, more balanced gender adoption, and no recent history of government blocking. It is the right fallback if Telegram becomes unavailable.
- **Telegram** is the cheaper, feature-rich test channel: zero marginal messaging cost and native quiz/poll support make it ideal for the active-retrieval treatment arm.
- A **dual-channel** design lets learners self-select their preferred channel and gives us direct comparative data on engagement, cost, and regulatory resilience.

**Channel fallback trigger:** If Telegram is blocked or otherwise inaccessible, any learner who also provided a WhatsApp number will be migrated to WhatsApp sends; learners with Telegram-only enrollment will be paused until the channel restores. The same fallback applies in reverse only if WhatsApp service is disrupted.

### 1.1 Implementation sequencing (post-introspection adjustment)

The architecture is dual-channel, but we will **not build both senders in the first sprint**. The first goal is to validate the behavioral mechanism at the lowest possible cost and attribution noise.

| Sub-phase | Channel | Goal | Success gate |
|---|---|---|---|
| **10.9a — Discovery & pre-flight** | None | Survey / interview nursing aspirants; lock 60+ verified questions; confirm cadence preference. | ≥60% of respondents say they would use a free daily 5-question quiz; ≥40% prefer Telegram or are neutral. |
| **10.9b — Telegram mechanism MVP** | Telegram only | Test active-retrieval nudge vs. generic reminder. | Treatment lift ≥5 pp in 24-hour quiz-start rate; STOP rate <5%; ≥50 confirmed opt-ins. |
| **10.9c — WhatsApp port & dual-channel choice** | WhatsApp + Telegram | Port winning arm to WhatsApp; offer channel choice; validate WhatsApp economics. | WhatsApp CPAU ≤₹5 for two consecutive weeks; channel engagement within 10 pp. |
| **10.9d — Resilience & scale** | Both + fallback | Add automatic channel fallback, cadence preference, and additional behavioral variants. | Fallback switches <1 hour; cadence preference used by ≥20% of users. |

Telegram is chosen for 10.9b because the Bot API is free, supports native quiz/poll interactions, and lets us falsify the active-retrieval hypothesis before paying WhatsApp per-message fees. WhatsApp is built only after the mechanism shows a meaningful lift.

### 2. Channel-specific implementation

#### 2.1 WhatsApp arm

Use **Chat Mitra Pro** as the primary WhatsApp Business API provider for the experiment.

| Factor | Chat Mitra Pro | Meta Cloud API direct |
|---|---|---|
| Monthly platform fee | ₹999/month | ₹0 |
| Per-message platform fee | ₹0.20/conversation + Meta rates [^1] | Meta rates only |
| Meta India utility rate (reminder) | ~₹0.115 per delivered template [^22][^23] | ~₹0.115 per delivered template [^22][^23] |
| Engineering setup | Low — BSP handles WABA onboarding, template submission, webhooks [^1] | High — we build template orchestration, webhook handling, number management |
| Time to first message | ~30 minutes guided onboarding [^1] | 2–6 weeks typical engineering effort [^2] |
| Support | Phone / WhatsApp / email (India-based) [^1] | Self-service / partner-only |
| Template approval | Managed via BSP dashboard | Direct via Meta Business Manager |

**Rationale:** Phase 10.9 is an experiment. We optimize for **time-to-validated-learning**, not lowest marginal cost at scale. Chat Mitra Pro removes the upfront engineering tax of direct Cloud API integration and provides India-based support. If the experiment reaches steady state and volume justifies it, we can later migrate to direct Cloud API.

**Fallback:** If Chat Mitra onboarding or template approval stalls beyond one week, switch evaluation to **Meta Cloud API direct**.

#### 2.2 Telegram arm

Use the **Telegram Bot API** directly. A bot is created via `@BotFather`, and users opt in by clicking a deep link (`t.me/DrMathBot?start=REF`) and sending `/start`.

- **Cost:** Telegram does not charge per message. Costs are limited to hosting the bot server and any optional paid broadcast (Telegram Stars) if we exceed the soft rate limit of ~30 messages/second [^24][^25].
- **Rate limits:** ~1 message/second to the same chat; ~30 messages/second across different chats in broadcast mode [^24].
- **Interaction model:** Use Telegram’s native **Quiz** poll type for the active-retrieval treatment. A quiz poll shows one question, multiple options, and immediately displays correctness + explanation after the user taps an answer.
- **Opt-out:** Users can block the bot or send `STOP`; both actions suppress future sends.

### 3. Experiment design: test mechanisms, not just delivery

Phase 10.9 is reframed as an A/B experiment that tests whether a behaviorally-designed nudge increases **quiz starts** more than a generic reminder, within each channel.

**Hypothesis:** A behaviorally-designed nudge will produce a higher 24-hour quiz-start rate than a generic reminder; the experiment is designed to identify which mechanism drives the effect.

**Arms (applied per channel):**

- **Arm A — Control:** Generic utility reminder.  
  Example: *“Hi [Name], your daily 5-question nursing quiz is ready. Practice now: {link}. Reply STOP to unsubscribe.”*
- **Arm B — Treatment (active retrieval nudge):**
  - **Telegram:** A Telegram Quiz poll containing one short question. Tapping an answer reveals correctness and a brief explanation, followed by a link to the full daily quiz.
  - **WhatsApp:** A template message containing one short question with numbered options. The learner replies with the number; the webhook responds with correctness, explanation, and a link to the full quiz.

**Why active retrieval?** Retrieval practice — answering a question rather than passively reading a reminder — improves long-term retention [^11]. It also lowers the activation energy for the target behavior because the learner has already begun practicing inside the messaging app.

**Randomization:** Users are randomly assigned to an arm at the moment of confirmed opt-in and remain in that arm for the duration of the experiment.

**Primary metric:** 24-hour quiz-start rate (user opens `/nursing/` within 24 hours of the daily send).  
**Secondary metrics:** reply/interaction rate (treatment), answer accuracy, full-quiz completion rate, streak length, STOP/block rate, cost per active daily user (CPAU).

**Future variants:** If the active-retrieval arm outperforms the control, we will test additional mechanisms in subsequent sprints: implementation-intention prompts [^7], loss-aversion streak framing [^8], and social-norm messages [^9].

### 4. Message category: Utility for quiz-related messages

Daily quiz reminders and micro-questions are **utility messages** (appointment/event reminders or user-requested account updates) because they notify the user of an available daily learning activity they have explicitly signed up for. If future messages include promotional content (e.g., “Upgrade to full course”), they must be sent as **marketing** templates and require a separate, explicit marketing consent.

Every WhatsApp template footer must include:  
`“Reply STOP to unsubscribe.”` [^3][^4]

Telegram messages must similarly include an unsubscribe instruction, e.g., `“Reply STOP to unsubscribe or block this bot.”`

### 5. Consent model: explicit opt-in + confirmation + easy withdrawal

We implement a **two-step opt-in** for each channel:

1. **Primary opt-in:** On the nursing PWA or web landing page, the user selects a channel (WhatsApp or Telegram), enters the relevant identifier (phone number or Telegram username), and checks a clearly labeled checkbox. Before the checkbox is accepted, the user sees a **standalone consent notice** that itemizes the data category being collected (hashed phone number or hashed Telegram chat_id), the specific purpose (`daily_quiz_nudge`), approximate frequency, retention period, and a withdrawal link. The notice is available in **English and Hindi/Telugu** at minimum, satisfying the DPDP Rules, 2025 requirement that notices be presented in English or any Eighth-Schedule language [^29][^30].
2. **Confirmation opt-in:** We send a message on the chosen channel asking the user to reply `YES` to confirm. We do not send daily nudges until `YES` is received.

We store a **consent artifact** per user:

```json
{
  "channel": "whatsapp",
  "identifier_hash": "sha256:+91xxxxxxxxx",
  "consent_version": "2026-05-05",
  "purpose": "daily_quiz_nudge",
  "experiment_arm": "A",
  "source": "nursing_web_optin",
  "opted_in_at": "2026-05-05T09:00:00Z",
  "confirmed_at": "2026-05-05T09:05:00Z",
  "withdrawn_at": null,
  "fallback_channel": "telegram",
  "fallback_identifier_hash": "sha256:<chat_id>"
}
```

For Telegram, the identifier is the Telegram `chat_id`. For WhatsApp, it is the phone number. We never store raw identifiers.

**Withdrawal:** Any incoming message matching `STOP`, `UNSUBSCRIBE`, or similar Hindi/Telugu keywords immediately sets `withdrawn_at` and suppresses all future sends. We reply once to confirm unsubscribe and then stop [^3][^4]. Re-subscription requires a fresh explicit opt-in; a simple `START` does **not** automatically re-enroll a withdrawn user.

This aligns with the DPDP Act, 2023 and the notified **DPDP Rules, 2025**, which require consent to be free, specific, informed, unconditional, and unambiguous, and the means of withdrawal to be **as easy as giving consent** [^5][^29][^30]. We therefore expose a one-click withdrawal link in the consent notice and in every daily message footer, and we suppress all sends within minutes of a STOP/UNSUBSCRIBE reply.

### 6. Data retention

| Data | Retention | Rationale |
|---|---|---|
| Raw phone numbers / chat_ids | **Never stored.** Only SHA-256 hashes are kept. | Minimizes PII and limits breach impact. |
| Consent artifacts | **1 year after opt-out or purpose end.** | DPDPA allows retention where necessary for legal claims; 1 year balances auditability with minimization [^10]. |
| Message send logs | **1 year.** | The DPDP Rules, 2025 impose a minimum one-year retention for processing logs [^29][^10]. |
| Analytics events (anonymous) | **30 days.** | Events without identifiers/hashes match the existing nursing analytics retention policy. Events containing hashed identifiers follow the send-log retention. |
| STOP/withdrawal logs | **1 year.** | Legal defense against claims of non-compliance; also satisfies DPDP Rules minimum log retention. |

Where DPDP Rules, 2025 require a deletion notice (e.g., 48-hour notice before erasure), the purge job will queue deletion and honor the notice period [^10].

We do **not** share identifiers or consent records with Chat Mitra beyond what is technically required to deliver messages. We do **not** use the identifier list for advertising or sell it.

### 7. Cost / engagement / regulatory reversal triggers

Pause the experiment automatically if any of the following thresholds are crossed after at least **100 delivered messages per arm per channel**:

- **STOP/unsubscribe rate > 5%** on either channel — indicates consent quality or frequency problem.
- **24-hour quiz-start rate < 10% in both arms** on a given channel — indicates poor channel-message fit regardless of mechanism.
- **Treatment lift over control < 5 percentage points** in quiz-start rate — indicates the behavioral mechanism is not meaningfully changing behavior.
- **WhatsApp CPAU > ₹5** for two consecutive weeks — indicates the reminder is not converting to practice.
- **Telegram channel outage or government blocking** — trigger channel fallback or pause sends.

When triggered, we halt new sends, review the consent flow and message copy, and decide whether to iterate (test a different behavioral mechanism), pivot to the other channel, or terminate the experiment.

---

## Consequences

### Positive

- **Broader reach:** Dual-channel opt-in lets learners choose the app they already use.
- **Cost efficiency:** Telegram arm has near-zero marginal cost, making longer experiments affordable.
- **Phased learning:** Building Telegram first validates the behavioral mechanism before WhatsApp per-message costs begin; dual-channel choice is added only after the mechanism proves itself.
- **Behavioral focus:** The experiment measures whether the nudge changes practice behavior, not just whether messages are delivered.
- **Feature fit:** Telegram’s native quiz/poll is the ideal active-retrieval delivery mechanism.
- **Compliance by design:** Explicit double opt-in, multilingual standalone notice, one-click withdrawal, and DPDP-aligned log retention satisfy Meta, Telegram, and DPDPA requirements.
- **Reversible:** The reversal trigger and channel fallback prevent runaway spend or user harm if a channel fails.
- **Aligned with existing architecture:** The `AnalyticsSink` port can absorb engagement events; `NursingService` can be extended with a channel-agnostic reminder-subscription service.

### Negative

- **Higher implementation complexity:** We must build and maintain two sender adapters (WhatsApp + Telegram) and a channel-agnostic orchestrator.
- **Higher WhatsApp per-message cost:** ~₹0.115 utility per message + BSP fees; at scale this is more expensive than Telegram.
- **Consent friction:** Double opt-in on two channels will reduce conversion vs. single opt-in, but is necessary for compliance and list quality.
- **Content and discovery gate:** The experiment cannot launch until Phase 10.10 provides at least 60 verified questions and a short user-discovery survey confirms demand. This delays the first send but reduces unsubscribe risk.
- **Telegram regulatory risk:** The June 2026 temporary ban proves Telegram can be blocked around high-stakes exams. We must build the fallback trigger and monitor regulatory news.
- **Billing-model uncertainty resolved but not locked:** Meta’s 2026 India per-message rates are confirmed; final rates should still be verified at BSP onboarding [^22][^23].

### Neutral

- We will need a new `MessageSender` port with WhatsApp and Telegram adapters.
- We will need a lightweight scheduler (cron or APScheduler) and webhook endpoints for inbound STOP/YES/answer messages on both channels.

---

## Alternatives Considered

1. **WhatsApp-only MVP.** Rejected after user input: Telegram offers zero marginal cost and superior quiz interaction; excluding it would miss a large exam-prep audience and comparative data.
2. **Telegram-only MVP.** Rejected: the June 2026 temporary ban demonstrates platform-level regulatory risk, and WhatsApp has broader reach among female nursing aspirants.
3. **Meta Cloud API direct (primary for WhatsApp).** Rejected for the experiment because upfront engineering and onboarding time (2–6 weeks) exceeds our target time-to-learning. Kept as fallback.
4. **SMS instead of WhatsApp/Telegram.** Rejected: SMS has lower engagement, higher spam perception, and no native interactive opt-out/confirmation flow.
5. **In-app push notifications only.** Rejected: the target learners may not open the app daily; the experiment specifically tests whether an external nudge improves adherence.
6. **Single opt-in (no YES confirmation).** Rejected: double opt-in materially improves consent quality, reduces block rates, and is safer under DPDPA’s “free and informed” standard [^5].
7. **Store raw phone numbers or chat_ids.** Rejected: hashing is sufficient for duplicate suppression and delivery; storing raw identifiers increases compliance burden without benefit.
8. **Run only a generic reminder (no control arm).** Rejected: without a control arm we cannot distinguish a true behavioral effect from seasonal effects, notification fatigue, or self-selection bias.

---

## Council of Ten Deliberation Summary

- **Research Scientist:** Decision is anchored in 2026 India-specific messaging data, DPDPA/Meta/Telegram policy sources, a PubMed RCT challenging the reminder hypothesis, and the June 2026 Telegram ban.
- **First-Principles Engineer:** Consent is treated as a first-class entity with an artifact, not a boolean flag. The experiment is framed around the learner’s action (quiz start), not the system’s action (send).
- **Distributed Systems Architect:** A `MessageSender` port with WhatsApp and Telegram adapters lets us swap providers or add channels without touching the scheduler or consent service.
- **Infrastructure-First SRE:** Reversal triggers, channel fallback, and DPDP-aligned log retention (1-year send/consent logs, 30-day anonymous analytics) limit blast radius and observability cost.
- **Ethical Technologist:** No PII retention, explicit opt-in, and easy withdrawal respect learner autonomy; the dual-channel choice puts control in the learner’s hands.
- **Resource Strategist:** Telegram’s free API dramatically reduces the cost of experimentation; WhatsApp is retained as the regulated, reach-maximizing fallback.
- **Diagnostic Problem-Solver:** Reversal trigger targets the root question — does the nudge actually increase daily practice? — not vanity send volume.
- **Curious Explorer:** BSP evaluation, channel comparison, behavioral mechanism candidates, the Telegram ban, and the Phase 10.9 introspection are documented in `docs/research/bidirectional/bidirectional-10-whatsapp-reminder-efficacy-phase10_9.md` and `bidirectional-11-phase10_9-introspection.md`.
- **Clarity-Driven Communicator:** ADR makes channel strategy, consent, retention, experiment arms, and reversal criteria explicit before code is written.
- **Inner-Self Guided Builder:** The learner’s inbox is protected by strict opt-in and STOP handling; we do not optimize engagement at the cost of trust.

---

## References

[^1]: Chat Mitra. (2026). *Chat Mitra Pricing 2026*. https://chatmitra.com/pricing/

[^2]: Message Central. (2026, April 24). *WhatsApp Business API 2026: Complete Guide to Setup, Cloud API, Chatbots, Pricing and BSPs*. https://www.messagecentral.com/blog/whatsapp-business-api-complete-guide

[^3]: Blueticks. (2026, June 23). *WhatsApp Opt-In Compliance Requirements: Meta's Rules for Collecting Consent Without Getting Flagged*. https://blueticks.co/blog/whatsapp-opt-in-compliance-requirements

[^4]: Infobip. (2026, June 18). *WhatsApp opt-in: Policy requirements & collection strategies*. https://www.infobip.com/blog/how-to-collect-whatsapp-business-opt-ins

[^5]: Digital Personal Data Protection Act, 2023, No. 22, Acts of Parliament, 2023 (India). Sections 6–8 (consent, withdrawal, erasure).

[^6]: Cyril Shroff & Partners. (2025, December 7). *FAQs - The Digital Personal Data Protection Act, 2023* — withdrawal and erasure obligations. https://www.cyrilshroff.com/wp-content/uploads/2025/12/FAQs-DPDPA.pdf

[^7]: Gollwitzer, P. M. (1999). Implementation intentions: Strong effects of simple plans. *American Psychologist*, 54(7), 493–503. https://doi.org/10.1037/0003-066X.54.7.493

[^8]: Kahneman, D., & Tversky, A. (1979). Prospect theory: An analysis of decision under risk. *Econometrica*, 47(2), 263–291.

[^9]: Schultz, P. W., Nolan, J. M., Cialdini, R. B., Goldstein, N. J., & Griskevicius, V. (2007). The constructive, destructive, and reconstructive power of social norms. *Psychological Science*, 18(5), 429–434. https://doi.org/10.1111/j.1467-9280.2007.01917.x

[^10]: King, Stubb & Kasiva. (2025, November 25). *Data Retention, Deletion, And Log Management Under The DPDP Act, 2023 And DPDP Rules, 2025* — Rule 8 one-year log retention and deletion notice. https://www.mondaq.com/india/privacy-protection/1710314/data-retention-deletion-and-log-management-under-the-dpdp-act-2023-and-dpdp-rules-2025-navigating-operational-complexities-and-building-compliance-ready-data-data-architectures

[^11]: Roediger, H. L., & Karpicke, J. D. (2006). Test-enhanced learning: Taking memory tests improves long-term retention. *Psychological Science*, 17(3), 249–255. https://doi.org/10.1111/j.1467-9280.2006.01693.x

[^12]: GrabOn. (2026, June 5). *WhatsApp Users Data: Demographics and Usage (2026)*. https://www.grabon.in/indulge/tech/whatsapp-statistics/

[^13]: RichAutomate. (2026, June 12). *How Many WhatsApp Users in India? 2026 Stats & Data*. https://richautomate.in/blog/whatsapp-users-india-2026-statistics

[^14]: Favaretti, C., Subramonia Pillai, V., Murthy, S., Chandrasekar, A., Yan, S. D., Sulaiman, H., Gautam, A., Kaur, B., Ali, M. K., McConnell, M., & Sudharsanan, N. (2024). Effectiveness of WhatsApp based debunking reminders on follow-up visit attendance for individuals with hypertension: a randomized controlled trial in India. *BMC Public Health*, 24, 2441. https://doi.org/10.1186/s12889-024-19894-9

[^15]: Aziz, F. F. A. (2025). Nudged to Class: Exploring Online Reminders through a Quasi-Experiment. *International Journal of Research and Innovation in Social Science*, 8(12). https://doi.org/10.47772/IJRISS.2024.8120278

[^16]: Adil, F., Nazir, R., & Akhtar, M. (2022). Investigating the impact on learning outcomes through the use of EdTech during COVID-19: Evidence from an RCT in the Punjab province of Pakistan. *Frontiers in Education*, 7, 993265. https://doi.org/10.3389/feduc.2022.993265

[^17]: Central Square Foundation. (2022). *Understanding EdTech Usage at Home Using Dedicated Devices — Part 2*. https://www.centralsquarefoundation.org/Understanding_EdTech_Usage_at_Home_Using_Dedicated_Devices_Part2.pdf

[^18]: GrabOn. (2026, May 26). *Telegram Stats: Users By Country, Age and Financial Data (2026)*. https://www.grabon.in/indulge/tech/telegram-users-statistics/

[^19]: DemandSage. (2026, April 6). *Telegram Users Statistics 2026 [Latest Global Data]*. https://www.demandsage.com/telegram-statistics/

[^20]: Jobskar. (2025, April 15). *GNM Jobs 2025*. https://www.jobskar.com/search-jobs/jobs-by-education/GNM-jobs

[^21]: Jharkhand Exam Prep. (2025, June 18). *Jharkhand Nursing Entrance Exam 2025 (JCECEB)*. https://jharkhandexamprep.com/jharkhand-nursing-entrance-exam/

[^22]: MessageBot. (2026, June 24). *WhatsApp Business API Pricing in India 2026*. https://messagebot.in/blog/whatsapp-business-api-pricing-in-india/

[^23]: Ojiva AI. (2026, June 2). *WhatsApp Business API Pricing in India 2026: Cost Breakdown*. https://www.ojiva.ai/blogs/whatsapp-business-api-pricing-india/

[^24]: Botract. (2026, February 16). *How Much Does a Telegram Bot Cost? Complete Pricing Breakdown (2026)*. https://www.botract.com/blog/telegram-bot-cost-pricing-guide

[^25]: GramIO. (2026, June 4). *Telegram Bot API rate limits*. https://gramio.dev/rate-limits

[^26]: TechCrunch. (2026, June 16). *India temporarily blocks access to Telegram over exam fraud concerns*. https://techcrunch.com/2026/06/16/india-temporarily-blocks-access-to-telegram-over-exam-fraud-concerns/

[^27]: India.com. (2026, June 16). *Central government imposes temporary ban on Telegram ahead of NEET Retest 2026*. https://www.india.com/news/india/central-government-imposes-temporary-ban-telegram-ahead-of-neet-retest-2026-8447702/

[^28]: Physics Wallah. (2026, June 16). *Is Telegram Banned in India? NEET 2026 Block Explained*. https://www.pw.live/news/is-telegram-banned-in-india

[^29]: Press Information Bureau, Government of India. (2025, November 17). *DPDP Rules, 2025 Notified*. https://static.pib.gov.in/WriteReadData/specificdocs/documents/2025/nov/doc20251117695301.pdf

[^30]: GoTrust. (2026, April 17). *DPDPA Consent Management: How to Collect, Store and Withdraw User Consent Legally*. https://www.gotrust.nl/blog/dpdpa-consent-management-how-to-collect-store-and-withdraw-user-consent-legally

[^31]: Physics Wallah. (2026). *Nursing Pro 1.0 (2026) for All Nursing Exams, Complete Batch Details*. https://www.pw.live/nursing/exams/nusring-pro-1-0-2026-for-all-nursing-exams

[^32]: Khalafi, A., Gholami, M., Zolfaghari, M., Paryad, E., & Lebadi, M. A. (2024). The effect of spaced learning on the learning outcome and retention of nurse anesthesia students: a randomized-controlled study. *BMC Medical Education*, 24, 277. https://doi.org/10.1186/s12909-024-05233-5

[^33]: TecnoScientifica. (2025). *Microlearning and its Effectiveness in Modern Education: A Mini Review*. https://tecnoscientifica.com/journal/apga/article/download/496/258

[^34]: Ziyud, A. (2026). Who, Where, What, and How to Nudge: A Systematic Review of Co-Designed Digital Nudges for Behavioral Interventions. *Multimodal Technologies and Interaction*, 10(4), 43. https://doi.org/10.3390/mti10040043

[^35]: Engagys. (2026, January 6). *Nudge Theory in Practice: Designing Experiences That Influence Healthcare Consumer Behaviors*. https://www.engagys.com/insights/nudge-theory-designing-experience-influence-healthcare-consumer-behavior/

[^36]: CampaignMitra. (2026). *How WhatsApp Business API Became India’s Most Powerful Customer Engagement Tool in 2026*. https://campaignmitra.com/blog/how-whatsapp-business-api-became-indias-most-power/

[^37]: LeadNXT. (2026, February 4). *WhatsApp Business API Trends For 2026*. https://blog.leadnxt.com/2025/12/whatsapp-business-api-trends-for-2026/
