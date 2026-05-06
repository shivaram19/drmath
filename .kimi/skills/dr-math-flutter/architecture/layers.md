# Architecture Layers — UI / Domain / Data

**Single Responsibility:** Define what belongs in each layer and the contract between them.

## Problem

Where does this code go?
```dart
// Is this UI, domain, or data?
final discountedPrice = originalPrice * (1 - discountPercent / 100);
```

Wrong placement = untestable, unreusable, unmaintainable.

## Three-Layer Model

### 1. Domain Layer (Pure Dart)

**Rule:** Zero Flutter imports. Zero `dart:io`. Zero external package imports except `freezed`, `equatable`, or `meta`.

**Contains:**
- Entities (immutable, enforce invariants)
- Value objects (equality by value, not identity)
- Repository interfaces (abstract classes)
- Use cases / interactors (business logic orchestration)

```dart
// shared/models/question.dart — Entity
import 'package:meta/meta.dart';

@immutable
class Question {
  const Question({
    required this.id,
    required this.text,
    required this.options,
    required this.correctIndex,
    this.hint,
  }) : assert(correctIndex >= 0 && correctIndex < options.length,
           'correctIndex must be within options range');

  final String id;
  final String text;
  final List<String> options;
  final int correctIndex;
  final String? hint;

  bool isCorrect(int selectedIndex) => selectedIndex == correctIndex;

  Question copyWith({/*...*/}) => /*...*/;

  @override
  bool operator ==(Object other) => /*...*/;

  @override
  int get hashCode => /*...*/;
}
```

**Invariant enforcement is domain's job.** The `assert` ensures no invalid `Question` can exist.

### 2. Data Layer (Repository + Data Sources)

**Rule:** Implements domain repository interfaces. May use `dart:io`, `http`, `shared_preferences`, `sqflite`.

**Contains:**
- Repository implementations
- Data sources (remote API, local DB, cache)
- DTOs / API models (mappable to/from domain entities)

```dart
// shared/data/question_repository.dart — Interface (belongs to domain technically)
abstract class QuestionRepository {
  Future<List<Question>> getByTopic(String topicId);
  Future<Question?> getById(String id);
}

// shared/data/demo_question_repository.dart — Implementation
class DemoQuestionRepository implements QuestionRepository {
  @override
  Future<List<Question>> getByTopic(String topicId) async {
    // Simulate async boundary
    await Future.delayed(const Duration(milliseconds: 100));
    return DemoData.questions
        .where((q) => q.topicId == topicId)
        .toList();
  }

  @override
  Future<Question?> getById(String id) async {
    return DemoData.questions.cast<Question?>().firstWhere(
      (q) => q?.id == id,
      orElse: () => null,
    );
  }
}
```

**Key:** When transitioning to a real backend, only `DemoQuestionRepository` changes. Screens and domain models remain untouched.

### 3. UI Layer (Presentation)

**Rule:** Contains Flutter imports. No direct HTTP calls. No direct database access. Delegates to repositories or state management.

**Contains:**
- Screens (route endpoints)
- Widgets (reusable UI components)
- State management binding (ViewModels, Notifiers, Blocs)

```dart
// features/practice/practice_question_screen.dart
class PracticeQuestionScreen extends StatefulWidget {
  const PracticeQuestionScreen({super.key, required this.topicId});
  final String topicId;

  @override
  State<PracticeQuestionScreen> createState() => _PracticeQuestionScreenState();
}

class _PracticeQuestionScreenState extends State<PracticeQuestionScreen> {
  late final QuestionRepository _repository;
  List<Question> _questions = [];
  int _currentIndex = 0;
  int? _selectedOption;
  bool _submitted = false;

  @override
  void initState() {
    super.initState();
    _repository = DemoQuestionRepository(); // Injected in real app
    _loadQuestions();
  }

  Future<void> _loadQuestions() async {
    final questions = await _repository.getByTopic(widget.topicId);
    setState(() => _questions = questions);
  }

  void _submit() {
    if (_selectedOption == null) return;
    setState(() => _submitted = true);
  }

  void _next() {
    setState(() {
      _currentIndex++;
      _selectedOption = null;
      _submitted = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    // Pure layout. Zero business logic.
    final question = _questions.isNotEmpty ? _questions[_currentIndex] : null;
    return Scaffold(/* ... */);
  }
}
```

## Data Flow

```
User Action
    │
    ▼
Screen (StatefulWidget / ConsumerWidget)
    │
    ▼
State Manager (Notifier / Bloc / ViewModel)
    │
    ▼
Repository (interface → implementation)
    │
    ▼
Data Source (API / Local / Static)
    │
    ▼
Domain Model (immutable, validated)
```

## Testing Per Layer

| Layer | Test Type | Isolation |
|-------|----------|-----------|
| Domain | Unit test | Pure Dart, no mocks needed |
| Data | Unit test | Mock data sources with mocktail |
| UI | Widget test | Mock repositories, pump widget |
| E2E | Integration test | Full stack, real or fake data |

## Anti-Patterns

| Anti-Pattern | Symptom | Fix |
|-------------|---------|-----|
| **Anemic Domain Model** | Entities are data bags; logic in controllers | Move behavior into entities |
| **Leaky Abstraction** | Repository returns `http.Response` | Map to domain model before returning |
| **UI Layer Business Logic** | `if (user.age > 18 && user.country == 'IN')` in `build()` | Extract to use case / entity method |
| **Synchronous Repository** | `List<Question> getQuestions()` | Always `Future<List<Question>>` — async boundary |
| **God Screen** | Single file >500 lines | Extract widgets, extract state class |

## Expert Source

Rešetár, M. (Reso Coder). "Flutter Clean Architecture / DDD." https://resocoder.com/category/tutorials/flutter/ddd-clean-architecture  
Bizzotto, A. "Flutter App Architecture: The Repository Pattern." https://codewithandrea.com/articles/flutter-repository-pattern
