# Build Size Optimization

**Single Responsibility:** Minimize APK/AAB size for emerging market devices.

## Current State

| Build Type | Size | Command |
|-----------|------|---------|
| Debug APK | ~60MB | `flutter build apk` |
| Release APK | ~20MB | `flutter build apk --release` |
| Split per ABI | ~12MB | `flutter build apk --split-per-abi` |
| App Bundle | Variable | `flutter build appbundle` |

**Target:** <15MB per ABI for Indian market (limited bandwidth).

## Optimization Techniques

### 1. Split Per ABI

```bash
flutter build apk --release --split-per-abi
# Generates: app-arm64-v8a-release.apk, app-armeabi-v7a-release.apk
```

**Savings:** ~40% reduction per ABI by excluding x86/x64 libraries.

### 2. Obfuscation + Resource Shrinking

```groovy
// android/app/build.gradle
android {
    buildTypes {
        release {
            minifyEnabled true
            shrinkResources true
            proguardFiles getDefaultProguardFile('proguard-android.txt')
        }
    }
}
```

```bash
flutter build apk --obfuscate --split-debug-info=symbols/
```

### 3. Analyze Size

```bash
flutter build apk --analyze-size
# Opens interactive size report in browser
```

**Look for:**
- Unused assets in `assets/` (remove or compress)
- Large font files (subset with `font-subset`)
- Unnecessary native libraries

### 4. Asset Optimization

```yaml
# pubspec.yaml — only include needed assets
flutter:
  assets:
    - assets/images/      # Compress PNGs with tinypng.com
    - assets/icons/       # Use SVG where possible (vector_drawable)
```

### 5. Deferred Components (Advanced)

```dart
// Load curriculum content on demand
import 'package:deferred_components/deferred_components.dart';

@deferred
Future<void> loadAdvancedMath() async {
  await loadLibrary();
}
```

**Savings:** Initial download excludes non-essential content.

## Anti-Patterns

| Anti-Pattern | Fix |
|-------------|-----|
| Including all 4 ABI architectures in single APK | Use `--split-per-abi` |
| Full-resolution images for thumbnails | Generate 1x/2x/3x variants |
| Bundling unused fonts | Only include weights used (e.g., Regular + Bold) |
| Debug symbols in release | Use `--split-debug-info` |

## Expert Sources

Flutter Team. "App size." https://docs.flutter.dev/perf/app-size  
Welsch, P. "Flutter app size optimization." https://pascalwelsch.com
