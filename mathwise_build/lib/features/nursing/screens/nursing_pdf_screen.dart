import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import '../models/attempt.dart';
import '../models/capability.dart';
import '../services/nursing_api_exception.dart';
import '../services/nursing_api_service.dart';
import '../widgets/capability_bar.dart';
import '../widgets/nursing_app_bar.dart';

/// Generate a weak-area practice PDF and copy the HTML to the clipboard.
class NursingPdfScreen extends StatefulWidget {
  final List<Attempt> attempts;

  const NursingPdfScreen({super.key, required this.attempts});

  @override
  State<NursingPdfScreen> createState() => _NursingPdfScreenState();
}

class _NursingPdfScreenState extends State<NursingPdfScreen> {
  final _api = NursingApiService();
  List<Capability> _weakTopics = [];
  final Set<String> _selectedTopics = {};
  bool _generating = false;
  String? _html;
  String? _error;

  @override
  void initState() {
    super.initState();
    _loadWeakTopics();
  }

  Future<void> _loadWeakTopics() async {
    try {
      final analysis = await _api.analyzeAttempts(widget.attempts);
      final topics = analysis.topicCapabilities
          .where((c) => (c.accuracy < 0.7 || c.priorityScore > 0.3))
          .toList();
      if (mounted) {
        setState(() {
          _weakTopics = topics;
          _selectedTopics.addAll(
            topics.map((c) => c.topicId).whereType<String>(),
          );
        });
      }
    } on NursingApiException catch (e) {
      if (mounted) {
        setState(() => _error = e.message);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(e.message)),
        );
      }
    } catch (e) {
      if (mounted) setState(() => _error = e.toString());
    }
  }

  Future<void> _generate() async {
    setState(() => _generating = true);
    try {
      final html = await _api.exportPdf(widget.attempts);
      if (mounted) setState(() => _html = html);
    } on NursingApiException catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(e.message)),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(e.toString())),
        );
      }
    } finally {
      if (mounted) setState(() => _generating = false);
    }
  }

  Future<void> _copyToClipboard() async {
    if (_html == null) return;
    await Clipboard.setData(ClipboardData(text: _html!));
    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('HTML copied to clipboard')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: const NursingAppBar(title: 'Practice PDF'),
      body: _html != null ? _buildPreview() : _buildTopicSelection(),
    );
  }

  Widget _buildTopicSelection() {
    if (_weakTopics.isEmpty && _error == null) {
      return const Center(child: CircularProgressIndicator());
    }

    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        Text(
          'Select weak areas to include',
          style: Theme.of(context).textTheme.titleMedium,
        ),
        const SizedBox(height: 8),
        if (_error != null)
          Card(
            color: Colors.red.shade50,
            child: Padding(
              padding: const EdgeInsets.all(12),
              child: Text(_error!),
            ),
          )
        else
          ..._weakTopics.map((c) {
            final topicId = c.topicId ?? '';
            return CheckboxListTile(
              title: Text(topicId.replaceAll('_', ' ')),
              subtitle: CapabilityBar(
                label: 'Accuracy',
                value: c.accuracy,
                color: c.accuracy < 0.5 ? Colors.red : Colors.orange,
              ),
              value: _selectedTopics.contains(topicId),
              onChanged: (value) {
                setState(() {
                  if (value == true) {
                    _selectedTopics.add(topicId);
                  } else {
                    _selectedTopics.remove(topicId);
                  }
                });
              },
            );
          }),
        const SizedBox(height: 20),
        SizedBox(
          width: double.infinity,
          child: ElevatedButton(
            onPressed: _generating || _selectedTopics.isEmpty
                ? null
                : _generate,
            child: _generating
                ? const SizedBox(
                    width: 20,
                    height: 20,
                    child: CircularProgressIndicator(strokeWidth: 2),
                  )
                : const Text('Generate Practice PDF'),
          ),
        ),
      ],
    );
  }

  Widget _buildPreview() {
    return Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Expanded(
            child: Card(
              child: SingleChildScrollView(
                padding: const EdgeInsets.all(16),
                child: Text(_html!),
              ),
            ),
          ),
          const SizedBox(height: 12),
          SizedBox(
            width: double.infinity,
            child: ElevatedButton.icon(
              onPressed: _copyToClipboard,
              icon: const Icon(Icons.copy),
              label: const Text('Copy HTML'),
            ),
          ),
          const SizedBox(height: 8),
          SizedBox(
            width: double.infinity,
            child: OutlinedButton(
              onPressed: () => setState(() => _html = null),
              child: const Text('Back'),
            ),
          ),
        ],
      ),
    );
  }
}
