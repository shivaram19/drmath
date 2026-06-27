import 'package:flutter/material.dart';

import '../models/attempt.dart';
import '../models/capability.dart';
import '../services/nursing_api_service.dart';
import '../services/nursing_storage_service.dart';
import '../widgets/capability_bar.dart';
import '../widgets/loading_state.dart';
import '../widgets/nursing_app_bar.dart';
import 'nursing_quiz_screen.dart';

/// Shows diagnostic/mock results and capability map.
class NursingResultsScreen extends StatefulWidget {
  final List<Attempt> attempts;

  const NursingResultsScreen({super.key, required this.attempts});

  @override
  State<NursingResultsScreen> createState() => _NursingResultsScreenState();
}

class _NursingResultsScreenState extends State<NursingResultsScreen> {
  final _api = NursingApiService();
  final _storage = NursingStorageService();
  bool _loading = true;
  String? _error;
  CapabilityAnalysis? _analysis;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    try {
      final analysis = await _api.analyzeAttempts(widget.attempts);
      await _storage.saveCapabilityMap({
        'subject_capabilities': analysis.subjectCapabilities
            .map((c) => {
                  'subject_id': c.subjectId,
                  'accuracy': c.accuracy,
                  'priority_score': c.priorityScore,
                })
            .toList(),
        'topic_capabilities': analysis.topicCapabilities
            .map((c) => {
                  'topic_id': c.topicId,
                  'accuracy': c.accuracy,
                  'priority_score': c.priorityScore,
                })
            .toList(),
      });
      if (mounted) {
        setState(() {
          _analysis = analysis;
          _loading = false;
        });
      }
    } catch (e) {
      if (mounted) setState(() => _error = e.toString());
    }
  }

  @override
  Widget build(BuildContext context) {
    final correct = widget.attempts.where((a) => a.isCorrect).length;
    final total = widget.attempts.length;
    final pct = total > 0 ? (correct / total * 100).round() : 0;

    return Scaffold(
      appBar: const NursingAppBar(title: 'Results', showBackButton: false),
      body: _loading
          ? const NursingLoading()
          : _error != null
              ? NursingError(message: _error!, onRetry: _load)
              : ListView(
                  padding: const EdgeInsets.all(16),
                  children: [
                    Card(
                      child: Padding(
                        padding: const EdgeInsets.all(16),
                        child: Column(
                          children: [
                            Text(
                              '$correct / $total',
                              style: Theme.of(context).textTheme.headlineMedium,
                            ),
                            Text('$pct% correct'),
                          ],
                        ),
                      ),
                    ),
                    const SizedBox(height: 16),
                    Text(
                      'Weak Areas',
                      style: Theme.of(context).textTheme.titleMedium,
                    ),
                    const SizedBox(height: 8),
                    ...?_analysis?.topicCapabilities.take(5).map(
                          (c) => CapabilityBar(
                            label: c.topicId?.replaceAll('_', ' ') ?? '',
                            value: c.accuracy,
                            color: c.accuracy < 0.5 ? Colors.red : Colors.orange,
                          ),
                        ),
                    const SizedBox(height: 24),
                    ElevatedButton.icon(
                      onPressed: () {
                        Navigator.of(context).pushAndRemoveUntil(
                          MaterialPageRoute<void>(
                            builder: (_) => const NursingQuizScreen(
                              mode: QuizMode.diagnostic,
                            ),
                          ),
                          (route) => route.isFirst,
                        );
                      },
                      icon: const Icon(Icons.refresh),
                      label: const Text('Try Again'),
                    ),
                    const SizedBox(height: 12),
                    OutlinedButton.icon(
                      onPressed: () {
                        Navigator.of(context).popUntil((route) => route.isFirst);
                      },
                      icon: const Icon(Icons.home),
                      label: const Text('Home'),
                    ),
                  ],
                ),
    );
  }
}
