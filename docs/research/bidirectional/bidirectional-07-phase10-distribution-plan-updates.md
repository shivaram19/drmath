# Bidirectional-07: Phase 10 Distribution Plan Updates After Introspection

**Date:** 2026-06-28  
**Scope:** Update the Phase 10 nursing distribution backlog based on internet research, self-interview, and completed Phases 10.1–10.5.  
**Research Phase:** Bidirectional — cross-domain impact of Bharat mobile behavior, WhatsApp virality, and DPDPA compliance.  
**Author:** Council-of-Ten review.

---

## 1. Context

Phases 10.1–10.5 are complete. The remaining Phase 10 work was originally scoped as native-app polish, analytics, and content expansion. The introspection in `bidirectional-03-phase10-distribution-introspection.md` surfaced five high-leverage unknowns that require backlog changes before we continue:

1. WhatsApp link-preview quality.
2. DPDPA notice completeness.
3. Consent-gated analytics vs. server logs.
4. PWA offline resilience on real devices.
5. HomeScreen responsive pass is broader than the nursing card.

## 2. Changes to the Phase 10 Backlog

| Original Item | Change | Rationale |
|---|---|---|
| 10.6 Analytics instrumentation | Split into **10.6a** (consent-gated analytics events) and **10.6b** (server-log retention policy). | DPDPA distinguishes legitimate-use security logs from consent-based analytics [^1][^2]. |
| 10.6 Share tracking | Add **Open Graph / social preview** as a prerequisite for any share-campaign experiment. | WhatsApp is the dominant distribution channel; poor link previews reduce CTR [^3]. |
| 10.7 HomeScreen nursing card overflow | Broaden to **HomeScreen 320–360 dp responsive pass** (Course Progress row, Games card, bottom nav). | Narrow-screen widget test revealed overflows across multiple cards, not just nursing. |
| 10.8 Content expansion | Keep, but add acceptance criterion: ** every new question maps to a verified source concept**. | High-stakes medical content requires provenance [^4]. |
| 10.9 User interviews | Add explicit research question: **Does the learner prefer web link, WhatsApp bot, or APK?** | IAMAI data shows shared-device, short-video, and WhatsApp dominance [^5][^6]. |
| 10.10 PWA-to-APK conversion | Defer until we have 30 days of `/nursing/` traffic and share data. | Conversion optimization without baseline metrics is premature. |

## 3. New Acceptance Criteria

### 10.6a Consent-Gated Analytics
- `landing_quiz_started`, `share_clicked`, and `quiz_completed` events fire only after `mw_privacy_consent.accepted === true`.
- Events contain no PII, no IP, no device ID.
- A `consent_version` field is attached to every event.

### 10.6b Server-Log Retention
- nginx access logs for `/nursing/` and `/api/nursing/*` are rotated and deleted after 30 days.
- Logs are used for security and uptime only, not for user-level analytics.
- This is documented in the privacy notice as a **legitimate use** under DPDPA Section 7.

### 10.6c Open Graph / WhatsApp Preview
- `/nursing/` includes valid Open Graph tags for title, description, image, URL, and locale.
- The `og:image` is ≤ 300 KB and 1200×630 px.
- WhatsApp link preview shows the Telugu/English title and description correctly.

### 10.7 HomeScreen Responsive Pass
- `flutter test test/features/home/home_screen_test.dart` passes at 360×800 and 320×640 viewports.
- No RenderFlex overflow exceptions on any Row in `HomeScreen` or `MathWiseBottomNav`.

## 4. Immediate Next Steps

1. Create GitHub issues for 10.6a, 10.6b, 10.6c, and updated 10.7.
2. Update `STATE.md` to reflect the refined backlog.
3. Update `/nursing/privacy.html` with Grievance Officer and retention details (10.6b).
4. Add Open Graph tags to `/nursing/index.html` (10.6c).

## 5. References

[^1]: Government of India. (2023). *The Digital Personal Data Protection Act, 2023*. India Code. https://www.indiacode.nic.in/handle/123456789/22037?view_type=browse

[^2]: Grant Thornton. (2025). *Privacy Compliance Guide 2025* (DPDPA Rules 2025). https://www.grantthornton.in/globalassets/1.-member-firms/india/assets/pdfs/privacy-compliance-guide-2025.pdf

[^3]: TxxT. (n.d.). *WhatsApp Automation for Education & Edtech India*. https://www.txxt.in/Education.html

[^4]: Solanki & Nayak. (2013). *International Journal of User-Driven Healthcare*. Cited in prior nursing research docs.

[^5]: IAMAI & Kantar. (2026). *Internet in India Report 2025*. https://www.iamai.in/sites/default/files/articles/Rural%20India%20Takes%20Driving%20Seat%20in%20India%E2%80%99s%20Internet%20Usage%20Growth.pdf

[^6]: Analytics India Magazine. (2024). *WhatsApp Becomes the New Classroom Leaving Edtech Companies Behind*. https://analyticsindiamag.com/ai-features/whatsapp-becomes-the-new-classroom-leaving-edtech-companies-behind/
