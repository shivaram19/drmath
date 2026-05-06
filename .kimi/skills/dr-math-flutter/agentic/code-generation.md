# Code Generation — Fine-Tuned Models for Flutter

**Single Responsibility:** Train or prompt AI to generate project-compliant Flutter code.

## Problem

General-purpose LLMs generate Flutter code that:
- Uses deprecated APIs (`withOpacity`)
- Violates project architecture
- Misses accessibility requirements
- Fails `flutter analyze`

## Strategy: In-Context Learning + Fine-Tuning

### Phase 1: In-Context Learning (Current)

Provide project context in every prompt:

```
You are generating Flutter code for Dr. Math.
Constraints:
- Architecture: lib/features/{name}/screens/, lib/shared/models/
- Design: Material 3, seed #6750A4, min touch 48dp
- State: StatefulWidget for local, Riverpod for shared
- Accessibility: tooltip on all IconButtons, no color-only feedback
- Testing: Unit test domain, widget test screens

Task: [specific task]
```

### Phase 2: Fine-Tuned Model (Future)

#### Training Data Collection

```bash
# Extract project corpus
find mathwise_build/lib -name "*.dart" -exec cat {} \; > flutter_corpus.txt

# Format as instruction-following pairs
cat > training_data.jsonl << 'EOF'
{"instruction": "Create a feature screen following Dr. Math architecture", "input": "Screen: algebra-basics, shows CPA pedagogy sections", "output": "<Dart code>"}
{"instruction": "Add accessibility to IconButton", "input": "Button: back navigation", "output": "IconButton(tooltip: 'Go back', ...)"}
EOF
```

#### Model Options

| Model | Size | Method | Cost | Quality |
|-------|------|--------|------|---------|
| CodeGemma 2B | 2B | LoRA | $0 (local) | Autocomplete |
| CodeGemma 7B | 7B | LoRA | $0 (local) | Component gen |
| Gemini Flash | API | Fine-tuning | Low | Feature gen |
| Claude 3.7 | API | Prompting | Medium | Architecture review |

#### Evaluation Metrics

```bash
# Automated evaluation pipeline
generate_code() | tee generated.dart
flutter analyze generated.dart && echo "BUILD_PASS" || echo "BUILD_FAIL"
flutter test generated_test.dart && echo "TEST_PASS" || echo "TEST_FAIL"
# Manual: Architecture compliance review
```

| Metric | Target |
|--------|--------|
| Build pass rate | >90% |
| Test pass rate | >80% |
| Architecture compliance | >95% |
| Accessibility compliance | 100% |

## Prompt Engineering Patterns

### Pattern: Few-Shot with Examples

```
Task: Create a new feature screen for "fractions" topic.

Example 1 (Triangles screen):
```dart
// lib/features/curriculum/triangles_screen.dart
class TrianglesScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Scaffold(
      appBar: AppBar(title: const Text('Triangles')),
      body: const ConceptContent(/*...*/),
    );
  }
}
```

Now generate: FractionsScreen following the same pattern.
```

### Pattern: Chain-of-Thought

```
Task: Add Riverpod to manage quiz state.

Step 1: Identify the state (current question, score, answers)
Step 2: Create AsyncNotifier with repository dependency
Step 3: Update screen to use ConsumerWidget
Step 4: Write unit tests for notifier
Step 5: Verify with flutter analyze and flutter test

Execute each step and verify before proceeding.
```

## Anti-Patterns

| Anti-Pattern | Fix |
|-------------|-----|
| Zero-shot generation | Always provide project context |
| No validation loop | Require `flutter analyze` pass |
| Generating entire app at once | Scaffold feature by feature |
| Ignoring existing patterns | Reference existing files as examples |

## Expert Sources

Flutter Team. "GenUI SDK." https://docs.flutter.dev/ai/genui  
Code with Andrea. "Flutter AI tools 2025." https://codewithandrea.com/newsletter/december-2025
