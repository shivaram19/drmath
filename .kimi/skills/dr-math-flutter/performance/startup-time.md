# Startup Time Optimization — TTI

**Single Responsibility:** Minimize time from app launch to interactive.

## Problem

Users abandon apps that take >3s to launch. On entry-level Android, Flutter defaults can hit 4-5s.

## Measurement

```bash
flutter run --trace-startup --profile
# Look for: "Time to initial frame display"
```

## Optimization Techniques

### 1. Defer Non-Critical Initialization

```dart
// BAD: Everything in main()
void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Firebase.initializeApp(); // 500ms
  await loadAllAssets(); // 300ms
  await precacheImages(); // 200ms
  runApp(const MathWiseApp());
}

// GOOD: Show UI immediately, load in background
void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const MathWiseApp());
}

// In HomeScreen initState:
@override
void initState() {
  super.initState();
  // Defer to post-frame
  WidgetsBinding.instance.addPostFrameCallback((_) {
    _loadNonCriticalData();
  });
}
```

### 2. Reduce Initial Widget Tree

```dart
// BAD: MaterialApp builds entire route tree
MaterialApp(
  routes: {
    '/': (context) => HomeScreen(),
    '/curriculum': (context) => CurriculumScreen(),
    '/practice': (context) => PracticeScreen(),
    // ... 10 more routes, all built eagerly
  },
)

// GOOD: Lazy route building
MaterialApp(
  onGenerateRoute: (settings) {
    switch (settings.name) {
      case '/': return MaterialPageRoute(builder: (_) => const HomeScreen());
      case '/curriculum': return MaterialPageRoute(builder: (_) => const CurriculumScreen());
      // Other routes built only when navigated
    }
  },
)
```

### 3. Shader Warmup (Pre-Impeller)

With Impeller (Flutter 3.27+), shader warmup is **not needed.** Impeller precompiles shaders at build time.

If still on Skia:
```dart
// Deprecated with Impeller
final shaderWarmup = DefaultShaderWarmup();
await shaderWarmup.execute();
```

### 4. Reduce APK Size

See `build-size.md`. Smaller APK = faster install + faster dexopt.

### 5. Native Splash Screen

```xml
<!-- android/app/src/main/res/drawable/launch_background.xml -->
<layer-list xmlns:android="http://schemas.android.com/apk/res/android">
    <item android:drawable="@android:color/white" />
    <item>
        <bitmap android:src="@mipmap/launch_image" android:gravity="center" />
    </item>
</layer-list>
```

**Rule:** Show branded splash within 100ms. Transition to Flutter UI smoothly.

## Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| Cold start TTI | < 2s | `--trace-startup` |
| Warm start TTI | < 1s | `--trace-startup` |
| First frame | < 200ms | DevTools |
| Splash to UI | < 100ms | Visual |

## Anti-Patterns

| Anti-Pattern | Fix |
|-------------|-----|
| Awaiting everything in `main()` | Show UI immediately, defer loads |
| Building all routes eagerly | Use `onGenerateRoute` |
| Still using Skia shader warmup | Migrate to Impeller |
| Large initial asset bundle | Load assets on-demand |

## Expert Sources

Hráček, F. "Flutter Performance: Startup." https://flutterperformance.com  
Flutter Team. "App startup." https://docs.flutter.dev/perf/app-startup
