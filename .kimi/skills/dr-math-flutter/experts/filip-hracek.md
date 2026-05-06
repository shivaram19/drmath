# Expert: Filip Hráček

**GitHub:** https://github.com/filiph  
**Key Projects:** Flutter Performance Book, "History of Everything" app, Giant Robot game  
**Authority:** Former Google Flutter/Dart team; rendering pipeline expert

## Why He Matters

Hráček's insight: **"Most performance issues are rebuild scope issues, not rendering issues."** Developers profile the GPU when the real problem is `setState` rebuilding 500 list items.

## Key Patterns

### Widget Rebuild Profiler (First Tool)

Before optimizing anything:
1. `flutter run --profile`
2. DevTools → Performance → Widget Rebuilds
3. Look for widgets rebuilding on every frame
4. Fix those first — 80% of jank lives here

### const Is Not Optional

```dart
// BAD: Rebuilds every frame unnecessarily
Widget build(BuildContext context) {
  return Column(
    children: [
      Header(title: 'MathWise'), // Rebuilds!
    ],
  );
}

// GOOD: const prevents rebuild
Widget build(BuildContext context) {
  return const Column(
    children: [
      Header(title: 'MathWise'), // Never rebuilds
    ],
  );
}
```

**Impact:** On a complex screen, `const` can reduce rebuild count by 90%.

### Isolate for Heavy Work

```dart
// BAD: 300ms jank on main thread
final parsed = jsonDecode(hugeJson);

// GOOD: Offload to isolate
final parsed = await compute(jsonDecode, hugeJson);

// DART 3.7+ (cleaner):
final parsed = await Isolate.run(() => jsonDecode(hugeJson));
```

### Impeller Rendering Engine

Flutter 3.27 uses Impeller by default on iOS and Android:
- **Eliminates shader compilation jank** (no more first-frame stutter)
- **Predictable performance** (no JIT shader compilation)
- **Reduced memory** (no shader cache)

**Check:** `flutter run` logs show "Impeller" in renderer info.

### Image Optimization

```dart
// BAD: Decodes full-resolution image on main thread
Image.asset('assets/large_photo.jpg')

// GOOD: Cache and resize
CachedNetworkImage(
  imageUrl: url,
  memCacheWidth: 800, // Decode at target size
  placeholder: (context, url) => const SkeletonLoader(),
)
```

## Failure Modes He Observed

1. **Profiling GPU first:** Wrong target. Check widget rebuilds first.
2. **Missing `const`:** Thousands of unnecessary rebuilds per second.
3. **JSON parsing on main thread:** 300ms+ jank on app startup.
4. **Full-resolution images:** Memory pressure + decode time.
5. **Ignoring Impeller:** Still disabling it manually. Impeller is production-ready.

## Performance Checklist

- [ ] Run DevTools Widget Rebuild profiler
- [ ] Add `const` to all stateless widgets and constants
- [ ] Use `ListView.builder` for all lists >10 items
- [ ] Offload JSON parsing to isolates
- [ ] Resize images to display dimensions
- [ ] Use `RepaintBoundary` around animations
- [ ] Verify Impeller is active

## Citation

```
[^1]: Hráček, F. Flutter Performance Book. https://flutterperformance.com
[^2]: Hráček, F. "The Boring Flutter Development Show." 
      Google Flutter team, 2018-2021.
```
