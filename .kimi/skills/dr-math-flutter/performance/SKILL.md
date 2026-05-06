# Performance Strategy — Profiling & Optimization

**Single Responsibility:** Define how to measure and improve Flutter app performance.

## Problem

"It works on my emulator" ≠ "It works on a 3-year-old Android device in rural India." Target hardware: entry-level Android with 2GB RAM, Mali GPU.

## Measurement-First

**Never optimize without profiling.** Filip Hráček's rule: 80% of performance issues are rebuild scope, not rendering [^1].

## Key Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Time to Interactive (TTI) | < 2s | `flutter run --trace-startup` |
| Frame build time | < 16ms (60fps) | DevTools Performance tab |
| Frame raster time | < 16ms | DevTools Performance tab |
| APK size | < 25MB | `flutter build apk --analyze-size` |
| Memory footprint | < 150MB | DevTools Memory tab |
| Battery drain | Minimal background activity | Android Profiler |

## Profiling Workflow

1. **Run in profile mode:** `flutter run --profile`
2. **Open DevTools:** `flutter pub global activate devtools && flutter pub global run devtools`
3. **Performance tab:** Identify frames exceeding 16ms
4. **Widget rebuild profiler:** Identify widgets rebuilding unnecessarily
5. **Memory tab:** Detect leaks (un disposed controllers, streams)

## Optimization Checklist

- [ ] `const` constructors on all stateless widgets and constants
- [ ] `ListView.builder` for lists >10 items
- [ ] `RepaintBoundary` around complex animations
- [ ] `compute()` or `Isolate.run()` for JSON parsing >1MB
- [ ] Images cached with `cached_network_image`
- [ ] No `setState` rebuilding ancestor widgets
- [ ] Debounced rapid input (search, sliders)

## Expert Sources

[^1]: Hráček, F. Flutter Performance Book. https://flutterperformance.com  
Flutter Team. "Performance best practices." https://docs.flutter.dev/perf/best-practices
