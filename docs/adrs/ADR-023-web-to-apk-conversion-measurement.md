# ADR-023: Web-to-APK Conversion Prompt and Campaign Measurement for MathWise Nursing

**Date:** 2026-05-05  
**Scope:** Add conversion prompts from the Nursing PWA to the full Flutter APK and measure campaign effectiveness with UTM-tagged links and best-effort install-open attribution.  
**Research Phase:** BFS — PWA-to-native conversion patterns, UTM campaign tagging, Android referrer APIs, DPDPA consent for native analytics.  
**Status:** Approved by Council of Ten.

---

## Context

ADR-019 established a PWA-first discovery channel at `https://drmath.trelolabs.com/nursing/` and positioned the Flutter APK as the richer, optional install for serious learners. Phase 10.8 now needs to:

1. Prompt engaged web users to install the full Android app.
2. Attribute installs to campaigns so we can compare organic shares, paid ads, landing banners, and result-screen CTAs.
3. Stay DPDPA-compliant: no analytics before consent, no personal identifiers, and no third-party trackers.

The target learner uses low-end Android phones, often with side-loaded APKs rather than Play Store installs, so standard Play Install Referrer attribution is unavailable.

---

## Decision

**Show conversion prompts on the result screen, the landing page (for returning users), and inside the WhatsApp share message; tag every prompt with UTM parameters; record click-level events via the existing web analytics endpoint; and collect best-effort install-open attribution in the Flutter app using `Intent.EXTRA_REFERRER`, gated by a new native consent record.**

Specifically:

1. **Prompt surfaces**
   - Result-screen card after quiz completion (`utm_medium=result_cta`).
   - Dismissible landing banner for users who have completed a quiz before (`utm_medium=landing_banner`).
   - Optional full-app link appended to the WhatsApp share text (`utm_source=whatsapp_share`).
2. **Campaign tagging**
   - All links point to `/mathwise.apk` with `utm_source`, `utm_medium`, `utm_campaign`, and `utm_content` populated from the landing URL or the placement.
   - Default campaign: `utm_campaign=nursing_full_app_install`.
3. **Click-level measurement**
   - `apk_prompt_shown` — fires when a prompt renders.
   - `apk_download_clicked` — fires when the user taps a download link; payload includes full UTM set and placement.
   - `score_shared` metadata gains `includes_app_link: true` when the share text contains the APK URL.
4. **Install-open measurement**
   - The Flutter app reads `Intent.EXTRA_REFERRER` on first cold start via the `referrer` plugin [^1][^2].
   - If a native consent record is accepted, the app sends `app_first_open` with the raw referrer URL and parsed UTM fields.
   - Because side-loaded APKs do not receive a Play Store install referrer, this is partial attribution; click-level data remains the primary conversion signal.
5. **Consent**
   - Web events continue to use the existing web consent key (`mw_privacy_consent`) and version `2026-06-28`.
   - Native analytics use a separate key (`mw_native_consent`) with version `2026-05-05`; a one-time in-app dialog asks for consent on first open.
   - The privacy notice is updated to describe native first-open referrer collection.
6. **Data minimization**
   - No IP, device ID, phone number, Aadhaar, or exact location is collected.
   - The server validates that UTM fields are strings ≤128 chars to prevent log injection.

---

## Consequences

### Positive
- Directly tests the ADR-019 reversal trigger by measuring how many web quiz finishers install the full app.
- UTM tagging lets us compare channel efficiency (organic share vs. landing banner vs. result CTA) without paid analytics vendors.
- Native consent is isolated from web consent, so adding native analytics does not force a web re-consent prompt.

### Negative
- Install-open attribution is incomplete because direct APK downloads do not provide a guaranteed install referrer; some conversions will only be visible as click events.
- Adds a new dependency (`referrer`) and a new native consent dialog to the Flutter app.
- Two consent records (web vs. native) increase operational complexity slightly.

### Neutral
- The existing `/api/nursing/analytics` endpoint remains the single sink for both web and native events; UTM fields live inside `metadata`.

---

## Alternatives Considered

1. **Use Google Play Install Referrer API (`android_play_install_referrer`).** Rejected because the APK is distributed by direct download, not through Google Play, so the API has no referrer to return.
2. **Use a third-party attribution SDK (e.g., Branch, AppsFlyer).** Rejected because it would introduce external data processors, require additional consent disclosures, increase payload size, and conflict with the project’s data-minimization principles [^4].
3. **Track only clicks, not install-open.** Rejected because click-to-install conversion is the key reversal metric; best-effort install-open data improves funnel accuracy even if incomplete.
4. **Reuse web consent for native analytics.** Rejected because a web consent record cannot represent informed consent for native app processing; DPDPA requires consent to be specific to the processing context [^4].

---

## Council of Ten Deliberation Summary

| Persona | Stance | Key Point |
|---|---|---|
| Research Scientist | ENDORSE | UTM + event logging is the minimum viable experiment to validate PWA-to-native conversion. |
| First-Principles Engineer | ENDORSE | The atomic user need is “try before you install”; prompts after quiz completion respect that. |
| Distributed Systems Architect | ENDORSE | Reuses existing analytics endpoint; no new service or database. |
| Infrastructure-First SRE | ENDORSE | JSONL retention and no PII keep ops risk low; server-side UTM validation prevents abuse. |
| Ethical Technologist | ENDORSE | Separate native consent, no identifiers, and no third-party trackers stay within DPDPA bounds. |
| Resource Strategist | ENDORSE | Avoids paid attribution vendors and keeps the experiment cheap. |
| Diagnostic Problem-Solver | ENDORSE | Measures the real bottleneck (install friction) rather than vanity page views. |
| Curious Explorer | ENDORSE | Creates a clean dataset for ad-hoc funnel analysis. |
| Clarity-Driven Communicator | ENDORSE | ADR documents the partial-attribution caveat and dual-consent design. |
| Inner-Self Guided Builder | ENDORSE | Prompts are optional, dismissible, and only shown to engaged users. |

---

## Action Items

- [x] Implement UTM parsing and prompt rendering in `web/static/nursing/app.js`.
- [x] Add prompt containers to `web/static/nursing/index.html` and styles to `styles.css`.
- [x] Update `web/static/nursing/privacy.html` to describe native first-open analytics.
- [x] Add server-side UTM validation and a pytest case in `tests/test_nursing_api.py`.
- [x] Add `referrer` plugin, `CampaignService`, `AnalyticsService`, and native consent dialog to the Flutter app.
- [x] Add Dart unit tests for UTM parsing and analytics payload.
- [x] Update `STATE.md` and mark Phase 10.8 complete.

---

## References

[^1]: Pub.dev. *referrer — Flutter package*. https://pub.dev/packages/referrer
[^2]: Android Developers. *Intent.EXTRA_REFERRER*. https://developer.android.com/reference/android/content/Intent#EXTRA_REFERRER
[^3]: Google Analytics Help. *How to use UTM parameters*. https://support.google.com/analytics/answer/10917952
[^4]: Government of India. (2023). *The Digital Personal Data Protection Act, 2023*. https://www.indiacode.nic.in/handle/123456789/22037?view_type=browse
