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
          actions: widget.mode == QuizMode.mock
              ? [TimerWidget(seconds: _remainingSeconds)]
              : null,
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
                    onPressed: _isLastQuestion ? _submit : _next,
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
          ),
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
