# ADR-021: Android Release Build Toolchain for MathWise Flutter App

**Date:** 2026-06-28  
**Scope:** Fix the `flutter build apk --release` failure caused by Jetifier incompatibility with Java 21 bytecode, and establish a reproducible release toolchain for the `mathwise_build` Flutter app.  
**Research Phase:** DFS — Flutter/Android Gradle compatibility, Bouncy Castle Jetifier issue.  
**Status:** Approved by Council of Ten.

---

## Context

The MathWise Flutter app (`mathwise_build/`) is built with Flutter 3.27.0, Dart 3.6.0, AGP 8.2.1, Gradle 8.7, and OpenJDK 21. The release build currently fails with:

```
Execution failed for task ':shared_preferences_android:generateReleaseLintModel'.
> Failed to transform bcprov-jdk18on-1.80.jar ...
   > Unsupported class file major version 65
```

`bcprov-jdk18on-1.80` is a Bouncy Castle cryptography jar that is pulled transitively by `shared_preferences_android:2.4.11` and contains Java 21 (major version 65) classes [^1]. AGP 8.2.1’s Jetifier (`1.0.0-beta10`) uses an ASM `ClassReader` that cannot parse Java 21 bytecode, so `JetifyTransform` crashes [^2]. This is a known issue in the Flutter ecosystem [^3][^4].

The project already enables code shrinking and resource shrinking in `android/app/build.gradle`, so once the build succeeds the release APK should drop well below the 104 MB debug APK.

---

## Decision

**Apply the minimal Jetifier ignore-list workaround now, and defer a full AGP/Gradle upgrade until after the release APK size and signing flow are validated.**

Specifically:

1. Add `android.jetifier.ignorelist=.*bcprov.*,.*bcutil.*` to `android/gradle.properties`.
   - Bouncy Castle jars do not contain legacy Android Support Library classes, so Jetifier has no work to do on them [^2].
   - This avoids the Java 21 bytecode parsing failure without forcing an AGP upgrade.
2. Create an empty `android/app/proguard-rules.pro` because `android/app/build.gradle` references it but the file is missing.
3. Verify the release build with `flutter build apk --release`.
4. Record the resulting APK size; if it exceeds the 20 MB target, open a follow-up issue for size optimization.

A full toolchain upgrade (AGP 8.7+, Gradle 8.10+, Kotlin 2.x) is the long-term fix and will be reconsidered once the app needs compileSdk 36 or newer AGP features.

---

## Consequences

### Positive
- Unblocks the release build immediately with a one-line change.
- Keeps the existing Flutter 3.27 / AGP 8.2 / Gradle 8.7 stack, avoiding plugin migration risk.
- Retains `minifyEnabled` and `shrinkResources`, so the release APK is small.
- ABI filter removes emulator-only x86/x86_64 libraries, reducing the universal APK from 22.9 MB to **15.4 MB**, meeting the ≤ 20 MB target.

### Negative
- The ignore-list is a workaround, not a structural fix. Future AGP versions may require removal or adjustment.
- Does not address the underlying AGP warning that AGP 8.2 was only tested up to `compileSdk = 34` while Flutter 3.27 uses 35.
- x86/x86_64 devices (mostly emulators) cannot install this APK; they are not the target audience for Bharat budget phones.

### Neutral
- The debug APK remains large; release builds are the primary distribution artifact for the nursing module.

---

## Alternatives Considered

1. **Upgrade AGP/Gradle/Kotlin now:** Rejected as the first step because it introduces plugin compatibility risk and is unnecessary to resolve the immediate blocker. It remains the planned future state.
2. **Pin Bouncy Castle to 1.79:** Rejected because 1.79 also contains Java 21 classes in some builds and the ignore-list is simpler and more robust [^3].
3. **Downgrade to Java 17:** Rejected because Flutter 3.27 and AGP 8.2 run correctly on Java 21; the failure is in Jetifier, not the runtime or compiler.

---

## Council of Ten Deliberation Summary

| Persona | Stance | Key Point |
|---|---|---|
| Research Scientist | ENDORSE | The Jetifier/Java 21 incompatibility is well-documented in the Flutter issue tracker [^3][^4]. |
| First-Principles Engineer | ENDORSE | Fix the actual failure point (Jetifier) rather than changing unrelated toolchain versions. |
| Distributed Systems Architect | ENDORSE | Minimal change reduces risk; upgrade can be done later with CI validation. |
| Infrastructure-First SRE | CONCERN → RESOLVED | Document the workaround so the next toolchain upgrade explicitly removes it. |
| Ethical Technologist | ENDORSE | No user data or runtime behavior changes; only build configuration. |
| Resource Strategist | ENDORSE | One-line fix costs almost nothing; full upgrade costs validation time. |
| Diagnostic Problem-Solver | ENDORSE | Root cause is Jetifier ASM, not Java version mismatch. |
| Curious Explorer | ENDORSE | Capture build output and APK size metrics in the lab notebook. |
| Clarity-Driven Communicator | ENDORSE | ADR records the workaround, reversal trigger, and follow-up plan. |
| Inner-Self Guided Builder | ENDORSE | Unblocks the learner-facing APK without cutting corners on runtime quality. |

---

## Action Items

- [x] Write ADR-021.
- [x] Add `android.jetifier.ignorelist` to `mathwise_build/android/gradle.properties`.
- [x] Create empty `mathwise_build/android/app/proguard-rules.pro`.
- [x] Add `ndk.abiFilters` for `arm64-v8a` and `armeabi-v7a` to remove emulator-only x86/x86_64 binaries.
- [x] Run `flutter build apk --release` and capture APK size.
- [x] Update `scripts/deploy.sh` to optionally build the Flutter release APK and copy it to `web/static/mathwise.apk`.
- [x] Deploy 15.4 MB release APK to `/usr/share/nginx/html/mathwise.apk`.
- [x] Close Issue #35 (build failure) and Issue #36/10.4 (size target ≤ 20 MB).

---

## References

[^1]: Mkyong. (2025). *Java — Unsupported class file major version 65*. https://mkyong.com/java/java-unsupported-class-file-major-version-65/

[^2]: droidyue. (2025). *Fix three build errors in Android*. https://droidyue.com/blog/2025/06/23/fix-three-build-error-in-android

[^3]: Flutter. (2025). *CI Error: Unsupported class file major version 65* (Issue #173839). https://github.com/flutter/flutter/issues/173839

[^4]: Flutter. (2025). *Remove Jetifier support by default* (Issue #168540). https://github.com/flutter/flutter/issues/168540
