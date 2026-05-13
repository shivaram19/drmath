# ADR-015: Cross-Platform App Distribution — APK + Flutter Web

**Date:** 2026-05-09
**Scope:** Web frontend + mobile distribution
**Research Phase:** DFS — Technology deep-dive

## Context

MathWise targets Class VII students (ages 12–13) in India. The student population uses a mix of Android (₹8,000–₹15,000 mid-range devices) and iOS (iPhone SE, older hand-me-downs). We need a distribution strategy that reaches both platforms without requiring macOS/Xcode infrastructure.

## Decision

We provide **two distribution channels**:

1. **Android:** Native APK via FastAPI `FileResponse` at `/mathwise.apk`
2. **iOS:** Flutter web build via `StaticFiles` at `/mathwise-web/`

## Rationale

### Why APK for Android
- Native performance is critical on mid-range Android devices with 4GB RAM.
- Flutter APK is 20.4MB — reasonable for Indian mobile data plans.
- Sideloading APK is standard practice for education apps outside the Play Store.

### Why Flutter Web for iOS (instead of IPA)
- IPA compilation requires macOS + Xcode, which is unavailable in our Linux CI environment.
- Flutter web build provides equivalent UI/UX on Safari via CanvasKit renderer.
- No App Store review gating — students can access immediately.
- iOS Safari supports PWA installation ("Add to Home Screen") for near-native feel.

## Consequences

- **Positive:** Single `flutter build web` command serves both testing and iOS distribution.
- **Positive:** No Apple Developer Program fees ($99/year) or App Store compliance overhead.
- **Negative:** iOS users miss native push notifications (web push is limited on Safari).
- **Negative:** Android web build is not offered; APK is the only Android path.

## References

1. Flutter Docs — Web support: https://docs.flutter.dev/platform-integration/web
2. Can I Use — PWA on iOS Safari: https://caniuse.com/?search=pwa%20ios
3. Apple Developer Program pricing: https://developer.apple.com/programs/

## Implementation Notes

### StaticFiles html=True

FastAPI's `StaticFiles` mount for `/mathwise-web` requires `html=True` to serve `index.html` when a trailing slash is requested (e.g., `/mathwise-web/`). Without this parameter, Starlette returns 404 for directory-style URLs, breaking the iOS "Play in Browser" button which uses `/mathwise-web/` as its href.

**Code:**
```python
app.mount("/mathwise-web", StaticFiles(directory=..., html=True), name="mathwise-web")
```

**Verification:** `curl -I https://drmath.trelolabs.com/mathwise-web/` → HTTP 200
