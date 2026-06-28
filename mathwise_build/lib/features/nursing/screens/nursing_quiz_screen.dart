import 'package:flutter/material.dart';

import '../controllers/nursing_session_controller.dart';
import '../models/nursing_question.dart';
import '../services/nursing_api_service.dart';
import '../services/nursing_session_logger.dart';
import '../services/nursing_storage_service.dart';
import '../widgets/loading_state.dart';
import '../widgets/nursing_app_bar.dart';
import '../widgets/question_card.dart';
import '../widgets/timer_widget.dart';
import 'nursing_report_screen.dart';
import 'nursing_results_screen.dart';

class NursingQuizScreen extends StatefulWidget {
  final QuizMode mode;
  final String? subjectId;
  final String? topicId;
  final NursingApiService? api;
  final NursingStorageService? storage;
  final NursingSessionLogger? logger;

  const NursingQuizScreen({
    super.key,
    required this.mode,
    this.subjectId,
    this.topicId,
    this.api,
    this.storage,
    this.logger,
  });

  @override
  State<NursingQuizScreen> createState() => _NursingQuizScreenState();
}

class _NursingQuizScreenState extends State<NursingQuizScreen> {
  late final NursingSessionController _controller;
  bool _canPop = false;

  @override
  void initState() {
    super.initState();
    _controller = NursingSessionController(
      api: widget.api,
      storage: widget.storage,
    );
    _controller.addListener(_onControllerChanged);
    _load();
  }

  @override
  void dispose() {
    _controller.removeListener(_onControllerChanged);
    _controller.dispose();
    super.dispose();
  }

  void _onControllerChanged() {
    if (mounted) setState(() {});
    if (_controller.remainingSeconds <= 0 &&
        _controller.mode == QuizMode.mock &&
        _controller.hasQuestions) {
      _submit();
    }
  }

  Future<void> _load() async {
    final resumed = await _controller.restoreInflightSession();
    if (resumed && mounted) {
      final shouldResume = await showDialog<bool>(
        context: context,
        barrierDismissible: false,
        builder: (context) => AlertDialog(
          title: const Text('Resume previous session?'),
          content: const Text(
            'You have an unfinished test. Would you like to resume where you left off?',
          ),
          actions: [
            TextButton(
              onPressed: () {
                _controller.abandon();
                Navigator.of(context).pop(false);
              },
              child: const Text('Start New'),
            ),
            TextButton(
              onPressed: () => Navigator.of(context).pop(true),
              child: const Text('Resume'),
            ),
          ],
        ),
      );
      if (shouldResume != true && mounted) {
        await _startNewSession();
      }
    } else if (mounted) {
      await _startNewSession();
    }
  }

  Future<void> _startNewSession() async {
    await _controller.start(
      mode: widget.mode,
      subjectId: widget.subjectId,
      topicId: widget.topicId,
    );
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
              TimerWidget(seconds: _controller.remainingSeconds),
            if (widget.mode == QuizMode.mock)
              IconButton(
                icon: const Icon(Icons.grid_view),
                tooltip: 'Question grid',
                onPressed: _showNavigationGrid,
              ),
          ],
        ),
        body: _controller.loading
            ? const NursingLoading()
            : _controller.error != null
                ? NursingError(message: _controller.error!, onRetry: _load)
                : _controller.hasQuestions
                    ? _buildBody()
                    : const Center(child: Text('No questions available')),
        bottomNavigationBar: _controller.loading ||
                _controller.error != null ||
                !_controller.hasQuestions
            ? null
            : SafeArea(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: ElevatedButton(
                    onPressed: _controller.isLastQuestion
                        ? _confirmSubmit
                        : _next,
                    child: Text(
                      _controller.isLastQuestion ? 'Submit' : 'Next',
                    ),
                  ),
                ),
              ),
      ),
    );
  }

  Widget _buildBody() {
    final q = _controller.currentQuestion!;
    final index = _controller.currentIndex;
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('Question ${index + 1} of ${_controller.questions.length}'),
          const SizedBox(height: 8),
          LinearProgressIndicator(
            value: (index + 1) / _controller.questions.length,
          ),
          const SizedBox(height: 16),
          QuestionCard(
            question: q,
            questionNumber: index + 1,
            totalQuestions: _controller.questions.length,
            selectedAnswer: _controller.selectedAnswers[index],
            onSelect: (value) => _controller.selectAnswer(index, value),
            onReport: () => _reportQuestion(q),
          ),
          if (widget.mode == QuizMode.mock) ...[
            const SizedBox(height: 12),
            CheckboxListTile(
              title: const Text('Mark for review'),
              value: _controller.markedForReview.contains(index),
              onChanged: (value) => _controller.toggleMarkForReview(index),
              controlAffinity: ListTileControlAffinity.leading,
            ),
          ],
        ],
      ),
    );
  }

  void _next() {
    if (!_controller.next()) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please select an answer')),
      );
    }
  }

  void _goToQuestion(int index) {
    _controller.goToQuestion(index);
    Navigator.of(context).pop();
  }

  void _showNavigationGrid() {
    showModalBottomSheet<void>(
      context: context,
      builder: (context) => _QuestionGridSheet(
        totalQuestions: _controller.questions.length,
        currentIndex: _controller.currentIndex,
        answeredIndices: _controller.selectedAnswers.keys.toSet(),
        markedIndices: _controller.markedForReview,
        onSelect: _goToQuestion,
      ),
    );
  }

  void _reportQuestion(NursingQuestion question) {
    Navigator.of(context).push(
      MaterialPageRoute<void>(
        builder: (_) => NursingReportScreen(
          question: question,
          api: widget.api,
        ),
      ),
    );
  }

  Future<void> _confirmSubmit() async {
    if (widget.mode != QuizMode.mock) {
      await _submit();
      return;
    }

    final answered = _controller.answeredCount;
    final unanswered = _controller.unansweredCount;
    final marked = _controller.markedForReview.length;

    final shouldSubmit = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Submit mock test?'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Total questions: ${_controller.questions.length}'),
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
    final attempts = _controller.buildAttempts();
    await _controller.submit();

    if (mounted) {
      Navigator.of(context).pushReplacement(
        MaterialPageRoute<void>(
          builder: (_) => NursingResultsScreen(
            attempts: attempts,
            api: widget.api,
            storage: widget.storage,
            logger: widget.logger,
          ),
        ),
      );
    }
  }

  Future<void> _onPopInvoked(bool didPop, Object? result) async {
    if (didPop) return;
    final shouldPop = await _confirmExit();
    if (!mounted) return;
    if (shouldPop) {
      await _controller.abandon();
      if (!mounted) return;
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
