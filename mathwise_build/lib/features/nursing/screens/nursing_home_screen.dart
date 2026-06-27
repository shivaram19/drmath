import 'package:flutter/material.dart';

import '../services/nursing_api_service.dart';
import '../widgets/language_toggle.dart';
import '../widgets/loading_state.dart';
import '../widgets/nursing_app_bar.dart';
import 'nursing_quiz_screen.dart';
import 'nursing_settings_screen.dart';
import 'nursing_subject_screen.dart';

/// Landing page for the nursing practice module.
class NursingHomeScreen extends StatefulWidget {
  const NursingHomeScreen({super.key});

  @override
  State<NursingHomeScreen> createState() => _NursingHomeScreenState();
}

class _NursingHomeScreenState extends State<NursingHomeScreen> {
  final _api = NursingApiService();
  bool _loading = true;
  String? _error;
  Map<String, dynamic>? _topicsData;
  int _questionCount = 0;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    try {
      final status = await _api.fetchStatus();
      final topics = await _api.fetchTopics();
      if (mounted) {
        setState(() {
          _questionCount = int.tryParse((status['questions'] ?? '0').toString()) ?? 0;
          _topicsData = topics;
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
        title: 'Nursing Practice',
        showBackButton: false,
        actions: [
          const LanguageToggle(),
          IconButton(
            icon: const Icon(Icons.settings_outlined),
            tooltip: 'Settings',
            onPressed: () {
              Navigator.of(context).push(
                MaterialPageRoute<void>(
                  builder: (_) => const NursingSettingsScreen(),
                ),
              );
            },
          ),
        ],
      ),
      body: _loading
          ? const NursingLoading()
          : _error != null
              ? NursingError(message: _error!, onRetry: _load)
              : _buildBody(),
    );
  }

  Widget _buildBody() {
    final subjects = (_topicsData?['subjects'] as List<dynamic>?)?.cast<String>() ?? [];
    final counts = (_topicsData?['counts'] as Map<String, dynamic>?) ?? {};

    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        _buildWelcomeCard(),
        const SizedBox(height: 16),
        _buildQuickActions(),
        const SizedBox(height: 24),
        Text(
          'Subjects ($_questionCount questions)',
          style: Theme.of(context).textTheme.titleMedium,
        ),
        const SizedBox(height: 12),
        ...subjects.map((s) => _buildSubjectTile(s, (counts[s] as int? ?? 0))),
      ],
    );
  }

  Widget _buildWelcomeCard() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Telangana Staff Nurse Practice',
              style: Theme.of(context).textTheme.headlineSmall,
            ),
            const SizedBox(height: 8),
            const Text('Find your weak areas and practice topic-wise.'),
            const SizedBox(height: 12),
            const Text(
              'Practice material, not an official question bank.',
              style: TextStyle(fontSize: 12, color: Colors.grey),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildQuickActions() {
    return Row(
      children: [
        Expanded(
          child: ElevatedButton.icon(
            onPressed: () => _startQuiz(QuizMode.diagnostic),
            icon: const Icon(Icons.assignment),
            label: const Text('Diagnostic'),
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: OutlinedButton.icon(
            onPressed: () => _startQuiz(QuizMode.mock),
            icon: const Icon(Icons.timer),
            label: const Text('Mock'),
          ),
        ),
      ],
    );
  }

  Widget _buildSubjectTile(String subjectId, int count) {
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: ListTile(
        leading: const Icon(Icons.book_outlined),
        title: Text(subjectId.replaceAll('_', ' ').toUpperCase()),
        subtitle: Text('$count questions'),
        trailing: const Icon(Icons.chevron_right),
        onTap: () {
          Navigator.of(context).push(
            MaterialPageRoute<void>(
              builder: (_) => NursingSubjectScreen(subjectId: subjectId),
            ),
          );
        },
      ),
    );
  }

  void _startQuiz(QuizMode mode) {
    Navigator.of(context).push(
      MaterialPageRoute<void>(
        builder: (_) => NursingQuizScreen(mode: mode),
      ),
    );
  }
}
