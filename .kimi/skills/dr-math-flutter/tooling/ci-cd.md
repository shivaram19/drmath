# CI/CD — Automated Build & Test Pipeline

**Single Responsibility:** Automate quality gates before code reaches production.

## GitHub Actions Workflow

```yaml
# .github/workflows/flutter.yml
name: Flutter CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: subosito/flutter-action@v2
        with:
          flutter-version: '3.27.0'
          channel: 'stable'

      - run: cd mathwise_build && flutter pub get
      - run: cd mathwise_build && flutter analyze --fatal-infos
      - run: cd mathwise_build && dart format --set-exit-if-changed .

  test:
    runs-on: ubuntu-latest
    needs: analyze
    steps:
      - uses: actions/checkout@v4
      - uses: subosito/flutter-action@v2
        with:
          flutter-version: '3.27.0'

      - run: cd mathwise_build && flutter pub get
      - run: cd mathwise_build && flutter test --coverage

      - uses: codecov/codecov-action@v4
        with:
          files: mathwise_build/coverage/lcov.info

  build:
    runs-on: ubuntu-latest
    needs: test
    steps:
      - uses: actions/checkout@v4
      - uses: subosito/flutter-action@v2
        with:
          flutter-version: '3.27.0'

      - run: cd mathwise_build && flutter pub get
      - run: cd mathwise_build && flutter build apk --release --split-per-abi

      - uses: actions/upload-artifact@v4
        with:
          name: apk-release
          path: mathwise_build/build/app/outputs/flutter-apk/
```

## Quality Gates

| Stage | Check | Failure Action |
|-------|-------|---------------|
| Pre-commit | `flutter analyze` | Block commit |
| Pre-commit | `dart format` | Auto-fix or block |
| PR | Unit tests | Block merge |
| PR | Widget tests | Block merge |
| PR | APK build | Block merge |
| Release | Integration tests | Manual QA fallback |
| Release | APK size < 25MB | Block release |

## Pre-Commit Hook

```bash
# .githooks/pre-commit (existing)
#!/bin/bash
cd mathwise_build || exit 1

flutter analyze --fatal-infos || exit 1
dart format --set-exit-if-changed . || exit 1
flutter test || exit 1
```

## Artifact Management

```bash
# Tag-based release
flutter build apk --release --split-per-abi
flutter build appbundle --release

# Upload to GitHub Releases
gh release create v1.0.0 \
  mathwise_build/build/app/outputs/flutter-apk/*.apk \
  mathwise_build/build/app/outputs/bundle/release/*.aab
```

## Anti-Patterns

| Anti-Pattern | Fix |
|-------------|-----|
| No CI for Flutter | Add GitHub Actions |
| CI only on main | Run on all PRs |
| No coverage threshold | Gate at 70% minimum |
| Manual APK builds | Automate release builds |
| No artifact retention | Upload to GitHub Releases |

## Expert Sources

Angelov, F. very_good_workflows. https://github.com/VeryGoodOpenSource/very_good_workflows  
Flutter Team. "Continuous delivery." https://docs.flutter.dev/deployment/cd
