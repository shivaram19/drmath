import 'dart:async';
import 'package:flutter/material.dart';

import '../models/attempt.dart';
import '../models/nursing_question.dart';
import '../services/nursing_api_service.dart';
import '../services/nursing_storage_service.dart';
import '../widgets/loading_state.dart';
import '../widgets/nursing_app_bar.dart';
import '../widgets/question_card.dart';
import '../widgets/timer_widget.dart';
import 'nursing_report_screen.dart';
import 'nursing_results_screen.dart';

enum QuizMode { diagnostic, mock, practice }

class NursingQuizScreen extends StatefulWidget {
  final QuizMode mode;
  final String? subjectId;
  final String? topicId;

  const NursingQuizScreen({
    super.key,
    required this.mode,
    this.subjectId,
    this.topicId,
  });

  @override
  State<NursingQuizScreen> createState() => _NursingQuizScreenState();
}

class _NursingQuizScreenState extends State<NursingQuizScreen> {
  final _api = NursingApiService();
  final _storage = NursingStorageService();
  bool _loading = true;
  String? _error;
  List<NursingQuestion> _questions = [];
  int _currentIndex = 0;
  final Map<int, String> _selectedAnswers = {};
  final Set<int> _markedForReview = {};
  DateTime? _startTime;
  Timer? _mockTimer;
  int _remainingSeconds = 60 * 60;
  bool _canPop = false;

  @override
  void initState() {
    super.initState();
    _load();
  }

  @override
  void dispose() {
    _mockTimer?.cancel();
    super.dispose();
  }

  Future<void> _load() async {
    try {
      List<NursingQuestion> questions;
      switch (widget.mode) {
        case QuizMode.diagnostic:
          questions = await _api.startDiagnostic(numQuestions: 20);
          break;
        case QuizMode.mock:
          questions = await _api.startMock();
          _startMockTimer();
          break;
        case QuizMode.practice:
          questions = await _api.fetchQuestions(
            subjectId: widget.subjectId,
            topicId: widget.topicId,
            limit: 20,
          );
          break;
      }
      if (mounted) {
        setState(() {
          _questions = questions;
          _loading = false;
          _startTime = DateTime.now();
        });
      }
    } catch (e) {
      if (mounted) setState(() => _error = e.toString());
    }
  }

  void _startMockTimer() {
    _remainingSeconds = 60 * 60;
    _mockTimer = Timer.periodic(const Duration(seconds: 1), (timer) {
      if (!mounted) {
        timer.cancel();
        return;
      }
      setState(() => _remainingSeconds--);
      if (_remainingSeconds <= 0) {
        timer.cancel();
        _submit();
      }
    });
  }

  String get _title {
    switch (widget.mode) {
      case QuizMode.diagnostic:
        return 'Diagnostic Test';
      case QuizMode.mock:
        return 'Mock Test';
      case QuizMode.practice:
        return 'Practice';
    }
  }

  @override
  Widget build(BuildContext context) {
    return PopScope<Object?>(
      canPop: _canPop,
      onPopInvokedWithResult: _onPopInvoked,
      child: Scaffold(
        appBar: NursingAppBar(
          title: _title,
          actions: [
            if (widget.mode == QuizMode.mock)
              TimerWidget(seconds: _remainingSeconds),
            if (widget.mode == QuizMode.mock)
              IconButton(
                icon: const Icon(Icons.grid_view),
                tooltip: 'Question grid',
                onPressed: _showNavigationGrid,
              ),
          ],
        ),
        body: _loading
            ? const NursingLoading()
            : _error != null
                ? NursingError(message: _error!, onRetry: _load)
                : _buildBody(),
        bottomNavigationBar: _loading || _questions.isEmpty
            ? null
            : SafeArea(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: ElevatedButton(
                    onPressed: _isLastQuestion ? _confirmSubmit : _next,
                    child: Text(_isLastQuestion ? 'Submit' : 'Next'),
                  ),
                ),
              ),
      ),
    );
  }

  bool get _isLastQuestion => _currentIndex == _questions.length - 1;

  Widget _buildBody() {
    final q = _questions[_currentIndex];
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('Question ${_currentIndex + 1} of ${_questions.length}'),
          const SizedBox(height: 8),
          LinearProgressIndicator(
            value: (_currentIndex + 1) / _questions.length,
          ),
          const SizedBox(height: 16),
          QuestionCard(
            question: q,
            questionNumber: _currentIndex + 1,
            totalQuestions: _questions.length,
            selectedAnswer: _selectedAnswers[_currentIndex],
            onSelect: (value) => setState(
              () => _selectedAnswers[_currentIndex] = value,
            ),
            onReport: () => _reportQuestion(q),
          ),
          if (widget.mode == QuizMode.mock) ...[
            const SizedBox(height: 12),
            CheckboxListTile(
              title: const Text('Mark for review'),
              value: _markedForReview.contains(_currentIndex),
              onChanged: (value) => setState(() {
                if (value == true) {
                  _markedForReview.add(_currentIndex);
                } else {
                  _markedForReview.remove(_currentIndex);
                }
              }),
              controlAffinity: ListTileControlAffinity.leading,
            ),
          ],
        ],
      ),
    );
  }

  void _next() {
    if (_selectedAnswers.containsKey(_currentIndex)) {
      setState(() => _currentIndex++);
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please select an answer')),
      );
    }
  }

  void _goToQuestion(int index) {
    setState(() => _currentIndex = index);
    Navigator.of(context).pop();
  }

  void _showNavigationGrid() {
    showModalBottomSheet<void>(
      context: context,
      builder: (context) => _QuestionGridSheet(
        totalQuestions: _questions.length,
        currentIndex: _currentIndex,
        answeredIndices: _selectedAnswers.keys.toSet(),
        markedIndices: _markedForReview,
        onSelect: _goToQuestion,
      ),
    );
  }

  void _reportQuestion(NursingQuestion question) {
    Navigator.of(context).push(
      MaterialPageRoute<void>(
        builder: (_) => NursingReportScreen(question: question),
      ),
    );
  }

  Future<void> _confirmSubmit() async {
    if (widget.mode != QuizMode.mock) {
      await _submit();
      return;
    }

    final answered = _selectedAnswers.length;
    final unanswered = _questions.length - answered;
    final marked = _markedForReview.length;

    final shouldSubmit = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Submit mock test?'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Total questions: ${_questions.length}'),
            Text('Answered: $answered'),
            Text('Unanswered: $unanswered'),
            Text('Marked for review: $marked'),
            const SizedBox(height: 12),
            if (unanswered > 0)
              const Text(
                'You have unanswered questions. Submit anyway?',
                style: TextStyle(fontWeight: FontWeight.bold),
              ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(false),
            child: const Text('Go Back'),
          ),
          TextButton(
            onPressed: () => Navigator.of(context).pop(true),
            child: const Text('Submit'),
          ),
        ],
      ),
    );

    if (shouldSubmit == true) await _submit();
  }

  Future<void> _submit() async {
    _mockTimer?.cancel();
    final elapsed = _startTime != null
        ? DateTime.now().difference(_startTime!).inSeconds
        : 0;
    final perQuestion = _questions.isNotEmpty
        ? (elapsed / _questions.length).clamp(1, 9999).toDouble()
        : 30.0;

    final attempts = <Attempt>[];
    for (var i = 0; i < _questions.length; i++) {
      final q = _questions[i];
      final selected = _selectedAnswers[i] ?? '';
      attempts.add(Attempt(
        questionId: q.id,
        selectedOption: selected,
        isCorrect: selected == q.correctAnswer,
        timeSeconds: perQuestion,
        confidence: 3,
        subjectId: q.subjectId,
        topicId: q.topicId,
        cognitiveLevel: q.cognitiveLevel,
      ));
    }

    await _storage.appendAttempts(attempts);

    if (mounted) {
      Navigator.of(context).pushReplacement(
        MaterialPageRoute<void>(
          builder: (_) => NursingResultsScreen(attempts: attempts),
        ),
      );
    }
  }

  Future<void> _onPopInvoked(bool didPop, Object? result) async {
    if (didPop) return;
    final shouldPop = await _confirmExit();
    if (!mounted) return;
    if (shouldPop) {
      setState(() => _canPop = true);
      Navigator.of(context).pop();
    }
  }

  Future<bool> _confirmExit() async {
    final result = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Leave test?'),
        content: const Text('Your progress will be lost.'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(false),
            child: const Text('Stay'),
          ),
          TextButton(
            onPressed: () => Navigator.of(context).pop(true),
            child: const Text('Leave'),
          ),
        ],
      ),
    );
    return result ?? false;
  }
}

class _QuestionGridSheet extends StatelessWidget {
  final int totalQuestions;
  final int currentIndex;
  final Set<int> answeredIndices;
  final Set<int> markedIndices;
  final ValueChanged<int> onSelect;

  const _QuestionGridSheet({
    required this.totalQuestions,
    required this.currentIndex,
    required this.answeredIndices,
    required this.markedIndices,
    required this.onSelect,
  });

  Color _cellColor(int index) {
    if (index == currentIndex) return Colors.blue.shade100;
    if (markedIndices.contains(index)) return Colors.orange.shade100;
    if (answeredIndices.contains(index)) return Colors.green.shade100;
    return Colors.grey.shade200;
  }

  @override
  Widget build(BuildContext context) {
    return SafeArea(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Jump to question',
              style: Theme.of(context).textTheme.titleMedium,
            ),
            const SizedBox(height: 12),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: List.generate(totalQuestions, (index) {
                return InkWell(
                  onTap: () => onSelect(index),
                  borderRadius: BorderRadius.circular(8),
                  child: Container(
                    width: 48,
                    height: 48,
                    alignment: Alignment.center,
                    decoration: BoxDecoration(
                      color: _cellColor(index),
                      borderRadius: BorderRadius.circular(8),
                      border: index == currentIndex
                          ? Border.all(color: Colors.blue, width: 2)
                          : null,
                    ),
                    child: Text('${index + 1}'),
                  ),
                );
              }),
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                _Legend(color: Colors.green.shade100, label: 'Answered'),
                const SizedBox(width: 12),
                _Legend(color: Colors.orange.shade100, label: 'Marked'),
                const SizedBox(width: 12),
                _Legend(color: Colors.grey.shade200, label: 'Unanswered'),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

class _Legend extends StatelessWidget {
  final Color color;
  final String label;

  const _Legend({required this.color, required this.label});

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Container(width: 12, height: 12, color: color),
        const SizedBox(width: 4),
        Text(label, style: Theme.of(context).textTheme.bodySmall),
      ],
    );
  }
}
