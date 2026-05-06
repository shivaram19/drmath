## DECISION-20260505-001: Flutter Mobile Client for Dr. Math

**Date:** 2026-05-05  
**Proposal:** Build a cross-platform Flutter mobile application (Android/iOS) for the Dr. Math adaptive learning platform, consuming the existing FastAPI backend.  
**Risk Level:** High  
**Final Decision:** Approved (with revised proposal)  

### Council Deliberation

| Persona | Stance | Key Point |
|---|---|---|
| Research Scientist | Endorse (revised) | Flutter TCO study [^8] and India mobile penetration data [^1] are T2/T3 sources; acceptable for engineering decision. |
| First-Principles Engineer | Endorse (revised) | State machine specified: BLoC + local cache + optimistic writes. Adaptive Mark consistency enforced via server-timestamp wins. |
| Distributed Systems Architect | Endorse (revised) | Offline-first with Hive/drift; background sync queue; FastAPI versioned to avoid breaking old builds. |
| Infrastructure-First SRE | Endorse (revised) | Firebase Crashlytics + Sentry dual reporting specified; API latency metrics via Dio interceptor. |
| Diagnostic Problem-Solver | Endorse (revised) | SVG fallback: rasterized PNG bundled for devices failing flutter_svg parse. Root cause addressed. |
| Ethical Technologist | Endorse (revised) | COPPA gate, anonymous auth, hashed device_id, and deletion API specified. Accessibility via flutter_math_fork Semantics. |
| Resource Strategist | Endorse (revised) | TCO: ~70% savings vs. native dual-team; APK 18–22MB acceptable given PWA cannot reliably push-notify on iOS. |
| Curious Explorer | Endorse (revised) | A/B test proposed: measure session duration Flutter vs. web at 90-day mark; log haptic feedback timing. |
| Clarity-Driven Communicator | Endorse (revised) | ADR-009 written. Decision log created. Commit message will cite ADR. |
| Inner-Self Guided Builder | Endorse (revised) | PWA rejected because Indian students on shared family phones need installable, offline-capable apps. Flutter serves the deeper need. |

### Rationale

The Council unanimously approved the revised proposal after ADR-009 addressed all blocking concerns: offline-first sync, COPPA compliance, TCO justification, and state consistency. The 10-Persona Filter confirms this is the right technical choice for Indian Class VII students, not merely the convenient one.

### Dissent Recorded

None. All blocking concerns were resolved in ADR-009 revision.

### Action Items

- [x] ADR written: `docs/adrs/ADR-009-mobile-client-strategy.md`
- [ ] Code implemented: `src/mobile/` Flutter project
- [ ] Tests added: BLoC unit tests, widget tests for 11 screens
- [ ] Metrics/observability: Firebase Crashlytics + Sentry DSN configured
- [ ] Documentation updated: `docs/architecture/mobile-client.md`
