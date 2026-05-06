# Agentic Flutter Development

**Single Responsibility:** Use AI to generate, refactor, and validate Flutter code.

## Problem

AI generates code that compiles but violates architecture, misses accessibility, and introduces anti-patterns. The agent must know the project's constraints before generating.

## AI Ecosystem for Flutter (2025)

| Tool | Function | Status |
|------|----------|--------|
| Dart/Flutter MCP Server | AI ↔ DevTools, widget tree, pub.dev | Official |
| Flutter AI Rules | Project-specific AI behavior constraints | Official |
| GenUI SDK | AI generates widget surfaces from JSON schemas | Alpha |
| Flutter AI Toolkit | Pre-built AI chat widgets | Stable v1.0 |
| Genkit Dart | Model-agnostic AI backend in Dart | Open source |
| Gemini CLI + Flutter Extension | Agentic code generation | Official |

## Workflow: AI-Assisted Feature Development

```
1. Research (BFS)        → Read SKILL.md, expert files, ADRs
2. Design (Human+AI)     → Generate ADR draft, architecture diagram
3. Scaffold (AI)         → Generate files following layer contracts
4. Validate (AI+Tool)    → flutter analyze, flutter test, check coverage
5. Iterate (Human)       → Review, refine, commit
```

## Project Rules for AI

Create `mathwise_build/.kimi/rules/flutter.md`:

```markdown
# Dr. Math Flutter Rules

## Architecture
- All features under lib/features/{name}/
- All models under lib/shared/models/ (pure Dart)
- All repositories under lib/shared/data/
- No cross-feature imports
- Use named routes for navigation

## Design System
- Material 3 with seed color #6750A4
- No hardcoded colors — use Theme.of(context).colorScheme
- Minimum touch target 48dp
- All IconButtons have tooltip

## State Management
- StatefulWidget for local UI state
- Riverpod for app-level shared state
- No BLoC for simple features

## Testing
- Unit test all domain logic
- Widget test all screens
- Integration test critical flows

## Accessibility
- Test with 2.0x text scale
- No color-only feedback
- Screen reader labels on all interactives

## Performance
- const constructors everywhere possible
- ListView.builder for lists
- Check mounted before setState after async
```

## Fine-Tuned Model Strategy

### Data Collection

Export all project Dart files as training corpus:
```bash
find mathwise_build/lib -name "*.dart" > flutter_corpus.txt
```

### Training Format (Instruction-Following)

```json
{
  "instruction": "Create a feature screen for 'algebra-basics' following Dr. Math architecture",
  "input": "Screen shows algebra concept with CPA pedagogy: Concrete, Pictorial, Abstract sections",
  "output": "<complete Dart file following lib/features/ pattern, using Theme.of, const, accessibility>"
}
```

### Model Options

| Model | Size | Location | Use Case |
|-------|------|----------|----------|
| CodeGemma 2B | 2B | Local (Ollama) | Fast autocomplete, lint-level fixes |
| CodeGemma 7B | 7B | Local (Ollama) | Component generation |
| Gemini 2.5 Flash | API | Google AI | Full feature generation, ADR drafting |
| Claude 3.7 Sonnet | API | Anthropic | Complex refactoring, architecture review |

### Evaluation Metrics

- **Build pass rate:** % of generated code that `flutter analyze` passes
- **Test pass rate:** % that `flutter test` passes
- **Architecture compliance:** Manual review against layer contracts
- **Accessibility score:** Automated axe-core equivalent for Flutter

## Anti-Patterns

| Anti-Pattern | Fix |
|-------------|-----|
| AI generates without reading project rules | Always inject `.kimi/rules/flutter.md` into context |
| AI uses deprecated APIs (`withOpacity`) | Post-process with `dart fix --apply` |
| AI imports non-existent packages | Verify pubspec.yaml before accepting |
| AI ignores accessibility | Explicitly require `tooltip` and `Semantics` |
| AI creates god classes | Enforce "Single Responsibility" in prompt |

## Expert Sources

Flutter Team. "Build with AI." https://docs.flutter.dev/ai  
Code with Andrea. "Flutter AI tools 2025." https://codewithandrea.com/newsletter/december-2025
