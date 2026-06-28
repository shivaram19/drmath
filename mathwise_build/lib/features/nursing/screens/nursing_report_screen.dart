import 'package:flutter/material.dart';

import '../models/nursing_question.dart';
import '../services/nursing_api_exception.dart';
import '../services/nursing_api_service.dart';
import '../widgets/nursing_app_bar.dart';
import '../widgets/question_card.dart';

/// Report a questionable nursing question.
class NursingReportScreen extends StatefulWidget {
  final NursingQuestion question;
  final NursingApiService? api;

  const NursingReportScreen({super.key, required this.question, this.api});

  @override
  State<NursingReportScreen> createState() => _NursingReportScreenState();
}

class _NursingReportScreenState extends State<NursingReportScreen> {
  late final NursingApiService _api = widget.api ?? NursingApiService();
  final _reasonController = TextEditingController();
  final _quickReasons = const [
    'Wrong answer',
    'Unclear wording',
    'Outdated',
    'Typo',
  ];
  bool _submitting = false;
  bool _submitted = false;
  String? _error;

  Future<void> _submit() async {
    final reason = _reasonController.text.trim();
    if (reason.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please enter a reason')),
      );
      return;
    }

    setState(() => _submitting = true);
    try {
      await _api.reportQuestion(widget.question.id, reason);
      if (mounted) setState(() => _submitted = true);
    } on NursingApiException catch (e) {
      if (mounted) {
        setState(() => _error = e.message);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(e.message)),
        );
      }
    } catch (e) {
      if (mounted) {
        setState(() => _error = e.toString());
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(e.toString())),
        );
      }
    } finally {
      if (mounted) setState(() => _submitting = false);
    }
  }

  void _addQuickReason(String reason) {
    final current = _reasonController.text;
    _reasonController.text = current.isEmpty ? reason : '$current, $reason';
  }

  @override
  void dispose() {
    _reasonController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: const NursingAppBar(title: 'Report Question'),
      body: _submitted ? _buildSuccess() : _buildForm(),
    );
  }

  Widget _buildForm() {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        QuestionCard(
          question: widget.question,
          readOnly: true,
        ),
        const SizedBox(height: 20),
        Text(
          'What is wrong with this question?',
          style: Theme.of(context).textTheme.titleMedium,
        ),
        const SizedBox(height: 12),
        Wrap(
          spacing: 8,
          children: _quickReasons
              .map(
                (reason) => ActionChip(
                  label: Text(reason),
                  onPressed: () => _addQuickReason(reason),
                ),
              )
              .toList(),
        ),
        const SizedBox(height: 16),
        TextField(
          controller: _reasonController,
          decoration: const InputDecoration(
            labelText: 'Detailed reason',
            border: OutlineInputBorder(),
            alignLabelWithHint: true,
          ),
          maxLines: 4,
        ),
        const SizedBox(height: 20),
        SizedBox(
          width: double.infinity,
          child: ElevatedButton(
            onPressed: _submitting ? null : _submit,
            child: _submitting
                ? const SizedBox(
                    width: 20,
                    height: 20,
                    child: CircularProgressIndicator(strokeWidth: 2),
                  )
                : const Text('Submit Report'),
          ),
        ),
        if (_error != null) ...[
          const SizedBox(height: 12),
          Text(
            _error!,
            style: TextStyle(color: Theme.of(context).colorScheme.error),
          ),
        ],
      ],
    );
  }

  Widget _buildSuccess() {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              Icons.check_circle_outline,
              size: 64,
              color: Theme.of(context).colorScheme.primary,
            ),
            const SizedBox(height: 16),
            Text(
              'Thank you',
              style: Theme.of(context).textTheme.headlineSmall,
            ),
            const SizedBox(height: 8),
            const Text(
              'Your report helps us keep the content accurate.',
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 24),
            ElevatedButton(
              onPressed: () => Navigator.of(context).pop(),
              child: const Text('Go Back'),
            ),
          ],
        ),
      ),
    );
  }
}
