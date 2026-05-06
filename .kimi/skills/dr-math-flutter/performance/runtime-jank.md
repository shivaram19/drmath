# Runtime Jank — 60fps Frame Budget

**Single Responsibility:** Eliminate UI frame drops during user interaction.

## Problem

A frame has 16.67ms budget at 60fps. If build + layout + paint exceeds this, the user sees stutter. Most jank in Flutter comes from **build scope**, not GPU rendering.

## Root Causes & Fixes

### 1. setState Rebuilds Too Much

```dart
// BAD: setState rebuilds entire HomeScreen
class HomeScreenState extends State<HomeScreen> {
  int _counter = 0;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Column(
        children: [
          const Header(), // Rebuilds unnecessarily!
          Text('$_counter'),
          const Footer(), // Rebuilds unnecessarily!
        ],
      ),
    );
  }
}

// GOOD: Extract state to isolated widget
class CounterSection extends StatefulWidget {
  @override
  State<CounterSection> createState() => _CounterSectionState();
}

class _CounterSectionState extends State<CounterSection> {
  int _counter = 0;

  @override
  Widget build(BuildContext context) => Text('$_counter');
}
```

### 2. Missing const Constructors

```dart
// BAD: Rebuilds on every parent setState
Widget build(BuildContext context) {
  return Column(
    children: [
      MyWidget(), // Rebuilds every time!
    ],
  );
}

// GOOD: const prevents rebuild when inputs unchanged
Widget build(BuildContext context) {
  return const Column(
    children: [
      MyWidget(), // Never rebuilds unless parent config changes
    ],
  );
}
```

**Lint:** `prefer_const_constructors` enforces this.

### 3. ListView Without builder

```dart
// BAD: Builds ALL items immediately
ListView(
  children: items.map((i) => ItemWidget(i)).toList(), // 500 widgets!
)

// GOOD: Lazily builds visible items + cache extent
ListView.builder(
  itemCount: items.length,
  itemBuilder: (context, index) => ItemWidget(items[index]),
)
```

### 4. RepaintBoundary for Animations

```dart
// BAD: Complex animation repaints parent
AnimatedBuilder(
  animation: _controller,
  builder: (_, __) => Transform.rotate(...),
)

// GOOD: Isolate paint region
RepaintBoundary(
  child: AnimatedBuilder(
    animation: _controller,
    builder: (_, __) => Transform.rotate(...),
  ),
)
```

### 5. Heavy Computation on Main Thread

```dart
// BAD: 300ms jank parsing large JSON
final data = jsonDecode(largeJsonString);

// GOOD: Offload to isolate
final data = await compute(jsonDecode, largeJsonString);
// Or with Dart 3.7+:
final data = await Isolate.run(() => jsonDecode(largeJsonString));
```

## Profiling with DevTools

1. `flutter run --profile`
2. Open DevTools → Performance tab
3. Identify red bars (frames > 16ms)
4. Click frame → see build timeline per widget
5. Identify widget with excessive build time

## Anti-Patterns

| Anti-Pattern | Fix |
|-------------|-----|
| Rebuilding `Scaffold` for a button color change | Extract state to child widget |
| `MediaQuery.of(context)` in build | Use `MediaQuery.sizeOf` (selective rebuild) |
| `Theme.of(context)` in build | Use specific selectors if only one property needed |
| Complex `CustomPaint` without caching | Cache `Picture` objects |
| Image decoding on main thread | Pre-cache with `precacheImage` |

## Expert Sources

Hráček, F. "Flutter Performance." https://flutterperformance.com  
Welsch, P. "Flutter Isolates." https://passsy.de/blog/2018-09-09-dart-advanced-isolates
