import 'package:flutter/material.dart';

import '../services/nursing_api_service.dart';
import '../widgets/loading_state.dart';
import '../widgets/nursing_app_bar.dart';
import 'nursing_quiz_screen.dart';

/// Shows topics for a selected nursing subject.
class NursingSubjectScreen extends StatefulWidget {
  final String subjectId;

  const NursingSubjectScreen({super.key, required this.subjectId});

  @override
  State<NursingSubjectScreen> createState() => _NursingSubjectScreenState();
}

class _NursingSubjectScreenState extends State<NursingSubjectScreen> {
  final _api = NursingApiService();
  bool _loading = true;
  String? _error;
  List<String> _topics = [];
  Map<String, int> _topicCounts = {};

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    try {
      final data = await _api.fetchTopics();
      final topicsBySubject = (data['topics_by_subject'] as Map<String, dynamic>?) ?? {};
      final topics = (topicsBySubject[widget.subjectId] as List<dynamic>?)
              ?.cast<String>() ??
          [];

      final counts = <String, int>{};
      for (final topic in topics) {
        final questions = await _api.fetchQuestions(
          subjectId: widget.subjectId,
          topicId: topic,
        );
        counts[topic] = questions.length;
      }

      if (mounted) {
        setState(() {
          _topics = topics;
          _topicCounts = counts;
          _loading = false;
        });
      }
    } catch (e) {
      if (mounted) setState(() => _error = e.toString());
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: NursingAppBar(
        title: widget.subjectId.replaceAll('_', ' ').toUpperCase(),
      ),
      body: _loading
          ? const NursingLoading()
          : _error != null
              ? NursingError(message: _error!, onRetry: _load)
              : ListView.builder(
                  padding: const EdgeInsets.all(16),
                  itemCount: _topics.length,
                  itemBuilder: (context, index) {
                    final topic = _topics[index];
                    return Card(
                      margin: const EdgeInsets.only(bottom: 8),
                      child: ListTile(
                        title: Text(topic.replaceAll('_', ' ')),
                        subtitle: Text('${_topicCounts[topic] ?? 0} questions'),
                        trailing: ElevatedButton(
                          onPressed: () => _startPractice(topic),
                          child: const Text('Practice'),
                        ),
                      ),
                    );
                  },
                ),
    );
  }

  void _startPractice(String topicId) {
    Navigator.of(context).push(
      MaterialPageRoute(
        builder: (_) => NursingQuizScreen(
          mode: QuizMode.practice,
          subjectId: widget.subjectId,
          topicId: topicId,
        ),
      ),
    );
  }
}
