# Static Analysis — analysis_options.yaml, Custom Lint

**Single Responsibility:** Enforce code quality at compile time.

## Problem

Without strict analysis, deprecated APIs (`withOpacity`), unused imports, and type unsafe code accumulate. The result: runtime errors that static analysis would have caught.

## Configuration

```yaml
# analysis_options.yaml
include: package:flutter_lints/flutter.yaml

analyzer:
  exclude:
    - "**/*.g.dart"
    - "lib/generated/**"
  language:
    strict-casts: true
    strict-inference: true
    strict-raw-types: true
  errors:
    invalid_assignment: error
    missing_return: error
    dead_code: info

linter:
  rules:
    # Style
    prefer_single_quotes: true
    prefer_const_constructors: true
    prefer_const_literals_to_create_immutables: true
    always_specify_types: false # Dart is inferred; don't fight it
    # Architecture
    avoid_relative_lib_imports: true
    directives_ordering: true
    # Quality
    avoid_print: true # Use debugPrint or logging package
    avoid_slow_async_io: true
    cancel_subscriptions: true
    close_sinks: true

formatter:
  page_width: 100
  trailing_commas: preserve
```

## Strict Mode Impact

| Mode | Effect |
|------|--------|
| `strict-casts: true` | Disallows implicit downcasts (`dynamic` → `String`) |
| `strict-inference: true` | Disallows `var` without inferred type |
| `strict-raw-types: true` | Requires generic type parameters (`List` → `List<String>`) |

## Custom Lint (Advanced)

```yaml
# pubspec.yaml
dev_dependencies:
  custom_lint: ^0.6.0
  dr_math_lints: # Your custom package
    path: packages/dr_math_lints

# analysis_options.yaml
analyzer:
  plugins:
    - custom_lint
```

```dart
// packages/dr_math_lints/lib/dr_math_lints.dart
import 'package:custom_lint_builder/custom_lint_builder.dart';

PluginBase createPlugin() => _DrMathLints();

class _DrMathLints extends PluginBase {
  @override
  List<LintRule> getLintRules(CustomLintConfigs configs) => [
    NoHardcodedColors(),
    RequireTooltipOnIconButton(),
  ];
}

class NoHardcodedColors extends DartLintRule {
  NoHardcodedColors() : super(code: const LintCode(
    name: 'no_hardcoded_colors',
    problemMessage: 'Use Theme.of(context).colorScheme instead of hardcoded colors',
  ));

  @override
  void run(CustomLintResolver resolver, ErrorReporter reporter, CustomLintContext context) {
    context.registry.addInstanceCreationExpression((node) {
      if (node.constructorName.type.name.lexeme == 'Color') {
        reporter.reportErrorForNode(code, node);
      }
    });
  }
}
```

## CI Enforcement

```yaml
# .github/workflows/flutter.yml
- name: Analyze
  run: flutter analyze --fatal-infos

- name: Format check
  run: dart format --set-exit-if-changed .
```

## Anti-Patterns

| Anti-Pattern | Fix |
|-------------|-----|
| No analysis_options.yaml | Uses minimal defaults, misses issues |
| `// ignore: type=lint` on every file | Fix the root cause |
| `avoid_print: false` | Print statements leak to production |
| Not running `dart fix --apply` | Missed automated migrations |

## Expert Sources

Dart Team. "Static analysis." https://dart.dev/tools/analysis  
Flutter Skills. "dart-run-static-analysis." https://github.com/flutter/skills
