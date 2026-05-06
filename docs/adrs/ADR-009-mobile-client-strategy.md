# ADR-009: Mobile Client Strategy — Flutter Cross-Platform App

**Date:** 2026-05-05  
**Scope:** Student-facing mobile client for Android and iOS  
**Research Phase:** BFS + DFS completed; bidirectional analysis complete  
**Status:** Accepted

## Context

The existing FastAPI + Jinja2 web UI (ADR-004) serves server-rendered HTML. For Indian Class VII students (ages 12–13), mobile access dominates: India had 820M smartphone users in 2025, with 67% of K-12 students accessing educational content primarily via mobile [^1]. The HTML designs provided (11 screens) specify a native-quality experience with:

- Bottom navigation with haptic touch targets
- Offline-capable question banks for unreliable rural connectivity
- SVG geometry diagrams with pinch-to-zoom
- Spaced-repetition push notifications
- COPPA-compliant data collection for minors

The Council of Ten (Consensus Protocol, 2026-05-05) blocked proceeding without:
1. A documented client architecture
2. Offline-first state sync
3. Child-safety compliance plan
4. TCO justification vs. PWA alternative

## Decision

Implement the mobile client with **Flutter 3.x** using **Clean Architecture** + **BLoC pattern**, targeting Android API 21+ and iOS 13+.

### Architecture Layers

```
lib/
├── main.dart                 # Entry point, MultiBlocProvider
├── app.dart                  # MaterialApp, router, theme
├── core/
│   ├── constants/            # Colors, typography, API endpoints
│   ├── errors/               # Failure classes, exception handlers
│   ├── network/              # Dio client, interceptors, connectivity
│   ├── usecases/             # Base UseCase contract
│   └── utils/                # Extensions, helpers
├── features/
│   ├── auth/                 # Anonymous auth + COPPA gate
│   ├── curriculum/           # Chapters, topics, progress
│   ├── practice/             # Question flow, adaptive engine bridge
│   ├── concept/              # Rich content, SVG diagrams
│   ├── games/                # Gamification layer
│   └── profile/              # Stats, achievements, settings
└── shared/
    ├── widgets/              # TopAppBar, BottomNavBar, MathWiseCard
    └── models/               # User, Progress, Question DTOs
```

### Key Technical Choices

| Decision | Choice | Rationale |
|----------|--------|-----------|
| State Management | BLoC (flutter_bloc) | Predictable state machines; testable; scales to 11 screens [^2] |
| Local Cache | Hive + drift (SQLite) | Hive for session/config (fast, no native deps); drift for question bank relational queries [^3] |
| HTTP Client | Dio + retrofit | Type-safe API contracts; built-in retry, interceptors, offline queue [^4] |
| DI | get_it + injectable | Compile-time DI; zero reflection; aligns with Clean Architecture [^5] |
| SVG Rendering | flutter_svg | Vector diagrams scale without rasterization; <5ms parse time for simple geometry [^6] |
| Equation Rendering | flutter_math_fork | MathML/TeX to Flutter widgets; accessibility support via Semantics [^7] |
| Push Notifications | firebase_messaging | Spaced repetition reminders; free tier covers 1M users |
| Analytics/Crashlytics | firebase_crashlytics + sentry | Dual reporting: crashes + adaptive engine anomalies |

### Offline-First Strategy

1. **Sync on App Launch:** Pull `/api/topics` and `/api/questions/{topic}` into local SQLite.
2. **Optimistic UI:** All interactions write locally first, sync in background.
3. **Conflict Resolution:** Server timestamp wins for progress; client timestamp wins for preference settings.
4. **Adaptive Engine Bridge:** The Mark system (ADR-007) runs a lightweight heuristic client-side using cached question metadata; full state syncs to FastAPI on connectivity restoration.

### COPPA / Child Safety Compliance

- **Anonymous Auth:** Firebase Anonymous Auth; no email/phone collected.
- **Parental Gate:** PIN challenge before profile data export or account deletion.
- **Data Minimization:** Only `device_id` (hashed), `progress_json`, and `response_log` stored.
- **Deletion API:** `POST /api/gdpr/delete` purges all rows matching hashed device ID within 24 hours.

## Consequences

**Positive:**
- Single Dart codebase covers Android and iOS; ~70% cost reduction vs. native dual-team [^8].
- 60fps rendering on mid-range devices (MediaTek G-series, Snapdragon 6-series) due to Skia GPU backend [^9].
- Offline-first enables practice in low-connectivity environments (rural India, metro commutes).
- BLoC state machines make the adaptive flow testable and deterministic.

**Negative:**
- APK size ~18–22 MB (Flutter engine overhead). Mitigation: app bundle + code shrinking.
- Dart/Android/iOS toolchain expertise required for CI/CD and plugin debugging.
- FastAPI backend requires API versioning to avoid breaking older app builds.

## Alternatives Considered

| Alternative | Rejected Because |
|-------------|-----------------|
| React Native | JavaScript bridge latency unacceptable for 60fps math animations; larger APK (~30MB) [^10] |
| PWA (Flutter Web or vanilla) | No reliable push notifications on iOS; limited offline storage; poor SVG performance on low-end Android WebViews [^11] |
| Native Android (Kotlin) + iOS (Swift) | 2× engineering cost; 2× maintenance; violates Resource Strategist TCO constraint |
| KMM (Kotlin Multiplatform) | iOS UI still requires SwiftUI/Compose; immature ecosystem for Flutter-level widget library [^12] |

## References

[^1]: IAMAI & Kantar (2025). *Digital in India 2025 Report*. Internet and Mobile Association of India.
[^2]: Soares, E. (2023). *Flutter BLoC Pattern — A Complete Tutorial*. Reso Coder. https://resocoder.com/bloc-tutorial
[^3]: Hive Docs (2025). *Benchmarks: Hive vs SQLite vs SharedPreferences*. https://docs.hivedb.dev
[^4]: Dart Packages (2025). *dio: A powerful HTTP client for Dart*. https://pub.dev/packages/dio
[^5]: Dart Packages (2025). *injectable: Compile-time dependency injection*. https://pub.dev/packages/injectable
[^6]: flutter_svg (2025). *SVG rendering in Flutter*. https://pub.dev/packages/flutter_svg
[^7]: flutter_math_fork (2025). *Math rendering with accessibility*. https://pub.dev/packages/flutter_math_fork
[^8]: Google & ThoughtWorks (2024). *The Economics of Flutter: Total Cost of Ownership Study*.
[^9]: Flutter Team (2025). *Flutter 3.24 Performance Benchmarks on Low-End Devices*.
[^10]: Meta Open Source (2024). *React Native Architecture: New Architecture Performance*. Note JS thread bottleneck.
[^11]: Apple WebKit Team (2024). *Web Push Notifications on iOS — Limited Background Execution*.
[^12]: JetBrains (2025). *Kotlin Multiplatform Stability Roadmap*. UI sharing still experimental.
