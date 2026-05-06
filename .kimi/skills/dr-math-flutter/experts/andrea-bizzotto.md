# Expert: Andrea Bizzotto

**GitHub:** https://github.com/bizz84  
**Key Projects:** CodingWithAndrea.com, Flutter Complete Reference  
**Authority:** Clean Architecture educator; Riverpod v2 adoption

## Why He Matters

Bizzotto's focus: **making architecture teachable.** His Riverpod v2 guides bridge the gap between "I know StatefulWidget" and "I need Clean Architecture."

## Key Patterns

### Repository + AsyncNotifier

```dart
// Domain
abstract class QuestionRepository {
  Future<List<Question>> getQuestions(String topicId);
}

// Riverpod binding
@riverpod
class QuestionsList extends _$QuestionsList {
  @override
  Future<List<Question>> build(String topicId) async {
    final repo = ref.watch(questionRepositoryProvider);
    return repo.getQuestions(topicId);
  }

  Future<void> refresh() async {
    final future = ref.read(questionRepositoryProvider).getQuestions(arg);
    state = await AsyncValue.guard(() => future);
  }
}

// UI
class QuestionsScreen extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final questionsAsync = ref.watch(questionsListProvider(topicId));
    return questionsAsync.when(
      data: (questions) => QuestionsListView(questions: questions),
      loading: () => const LoadingIndicator(),
      error: (err, _) => ErrorView(message: err.toString()),
    );
  }
}
```

### Firebase-First Architecture

Bizzotto's observation: Most Flutter apps use Firebase. The common failure is calling Firebase directly from widgets.

```dart
// WRONG: Firebase directly in onPressed
onPressed: () async {
  await FirebaseFirestore.instance.collection('questions').add({...});
}

// RIGHT: Repository abstracts Firebase
class FirestoreQuestionRepository implements QuestionRepository {
  final FirebaseFirestore _firestore;
  FirestoreQuestionRepository(this._firestore);

  @override
  Future<List<Question>> getQuestions(String topicId) async {
    final snapshot = await _firestore
      .collection('questions')
      .where('topicId', isEqualTo: topicId)
      .get();
    return snapshot.docs.map((d) => Question.fromJson(d.data())).toList();
  }
}
```

## Failure Modes He Observed

1. **Firebase in widgets:** No offline support, no testability, no retry logic.
2. **Missing error boundaries:** Async errors crash the entire screen. `AsyncValue` handles this.
3. **Anemic ViewModels:** ViewModels that just forward calls to repository. Add presentation logic (sorting, filtering, formatting) in ViewModel.

## Citation

```
[^1]: Bizzotto, A. "Flutter App Architecture: The Repository Pattern."
      https://codewithandrea.com/articles/flutter-repository-pattern
[^2]: Bizzotto, A. "Flutter Riverpod 2.0: Complete Guide."
      https://codewithandrea.com/articles/flutter-riverpod-2
```
