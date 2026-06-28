import 'package:flutter/material.dart';

import '../controllers/nursing_session_controller.dart';
import '../models/attempt.dart';
import '../models/capability.dart';
import '../services/nursing_api_exception.dart';
import '../services/nursing_api_service.dart';
import '../services/nursing_session_logger.dart';
import '../services/nursing_storage_service.dart';
import '../widgets/capability_bar.dart';
import '../widgets/loading_state.dart';
import '../widgets/nursing_app_bar.dart';
import 'nursing_quiz_screen.dart';

/// Shows diagnostic/mock results and capability map.
class NursingResultsScreen extends StatefulWidget {
  final List<Attempt> attempts;
  final NursingApiService? api;
  final NursingStorageService? storage;
  final NursingSessionLogger? logger;

  const NursingResultsScreen({
    super.key,
    required this.attempts,
    this.api,
    this.storage,
    this.logger,
  });

  @override
  State<NursingResultsScreen> createState() => _NursingResultsScreenState();
}

class _NursingResultsScreenState extends State<NursingResultsScreen> {
  late final NursingApiService _api = widget.api ?? NursingApiService();
  late final NursingStorageService _storage = widget.storage ?? NursingStorageService();
  late final NursingSessionLogger _logger = widget.logger ?? NursingSessionLogger();
  bool _loading = true;
  String? _error;
  CapabilityAnalysis? _analysis;
  bool _pendingSync = false;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() {
      _loading = true;
      _error = null;
      _pendingSync = false;
    });

    try {
      // If a previous session was queued while offline, try to sync it now.
      final pending = await _storage.loadPendingAnalysis();
      if (pending.isNotEmpty) {
        try {
          await _api.analyzeAttempts(pending);
          await _storage.clearPendingAnalysis();
        } on NursingApiException catch (_) {
          // Still offline; leave the previous queue intact.
        }
      }

      final analysis = await _api.analyzeAttempts(widget.attempts);
      final correct = widget.attempts.where((a) => a.isCorrect).length;
      final total = widget.attempts.length;
      final weakAreas = analysis.topicCapabilities
          .where((c) => (c.accuracy < 0.7 || c.priorityScore > 0.3))
          .map((c) => c.topicId)
          .whereType<String>()
          .toList();
      await _logger.log(
        mode: 'results',
        attemptsCount: widget.attempts.length,
        score: total > 0 ? correct / total : 0,
        weakAreas: weakAreas,
      );
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
    } on NursingApiException catch (e) {
      if (e.isOffline) {
        await _storage.queuePendingAnalysis(widget.attempts);
        final localAnalysis = _localAnalysisFromAttempts(widget.attempts);
        final correct = widget.attempts.where((a) => a.isCorrect).length;
        final total = widget.attempts.length;
        final weakAreas = localAnalysis.topicCapabilities
            .where((c) => c.accuracy < 0.7)
            .map((c) => c.topicId)
            .whereType<String>()
            .toList();
        await _logger.log(
          mode: 'results_offline',
          attemptsCount: widget.attempts.length,
          score: total > 0 ? correct / total : 0,
          weakAreas: weakAreas,
        );
        if (mounted) {
          setState(() {
            _analysis = localAnalysis;
            _pendingSync = true;
            _loading = false;
          });
        }
      } else {
        if (mounted) {
          setState(() {
            _error = e.message;
            _loading = false;
          });
        }
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _error = e.toString();
          _loading = false;
        });
      }
    }
  }

  /// Builds a simple local capability analysis when the backend is offline.
  CapabilityAnalysis _localAnalysisFromAttempts(List<Attempt> attempts) {
    final byTopic = <String, List<Attempt>>{};
    for (final attempt in attempts) {
      byTopic.putIfAbsent(attempt.topicId, () => []).add(attempt);
    }

    final topicCapabilities = byTopic.entries.map((entry) {
      final list = entry.value;
      final correct = list.where((a) => a.isCorrect).length;
      return Capability(
        accuracy: correct / list.length,
        speedScore: 0.5,
        confidenceGap: 0.0,
        consistencyScore: 0.5,
        priorityScore: 1 - (correct / list.length),
        topicId: entry.key,
      );
    }).toList();

    return CapabilityAnalysis(
      subjectCapabilities: const [],
      topicCapabilities: topicCapabilities,
      dimensionCapabilities: const [],
    );
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
                    if (_pendingSync) ...[
                      const SizedBox(height: 12),
                      Card(
                        color: Colors.orange.shade50,
                        child: const Padding(
                          padding: EdgeInsets.all(12),
                          child: Row(
                            children: [
                              Icon(Icons.cloud_off, size: 18),
                              SizedBox(width: 8),
                              Expanded(
                                child: Text(
                                  'You are offline. Weak-area analysis will sync when you reconnect.',
                                ),
                              ),
                            ],
                          ),
                        ),
                      ),
                    ],
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
                            builder: (_) => NursingQuizScreen(
                              mode: QuizMode.diagnostic,
                              api: widget.api,
                              storage: widget.storage,
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
