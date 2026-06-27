import 'dart:convert';
import 'package:http/http.dart' as http;

import '../models/nursing_question.dart';
import '../models/attempt.dart';
import '../models/capability.dart';

/// HTTP client for the Dr. Math nursing API.
///
/// In production this points to the deployed backend. For development,
/// adjust [baseUrl] to the local server (e.g., http://10.0.2.2:8000 for Android emulator).
class NursingApiService {
  static const String baseUrl = 'https://drmath.trelolabs.com';

  Future<Map<String, dynamic>> fetchStatus() async {
    final response = await http.get(Uri.parse('$baseUrl/api/nursing/status'));
    _check(response);
    return jsonDecode(response.body) as Map<String, dynamic>;
  }

  Future<Map<String, dynamic>> fetchTopics() async {
    final response = await http.get(Uri.parse('$baseUrl/api/nursing/topics'));
    _check(response);
    return jsonDecode(response.body) as Map<String, dynamic>;
  }

  Future<List<NursingQuestion>> fetchQuestions({
    String? subjectId,
    String? topicId,
    String? cognitiveLevel,
    String? context,
    int? difficulty,
    String? conceptTag,
    int? limit,
  }) async {
    final params = <String, String>{};
    if (subjectId != null) params['subject_id'] = subjectId;
    if (topicId != null) params['topic_id'] = topicId;
    if (cognitiveLevel != null) params['cognitive_level'] = cognitiveLevel;
    if (context != null) params['context'] = context;
    if (difficulty != null) params['difficulty'] = difficulty.toString();
    if (conceptTag != null) params['concept_tag'] = conceptTag;
    if (limit != null) params['limit'] = limit.toString();

    final uri = Uri.parse('$baseUrl/api/nursing/questions').replace(queryParameters: params);
    final response = await http.get(uri);
    _check(response);
    final list = jsonDecode(response.body) as List<dynamic>;
    return list.map((e) => NursingQuestion.fromJson(e as Map<String, dynamic>)).toList();
  }

  Future<List<NursingQuestion>> startDiagnostic({int numQuestions = 20}) async {
    final response = await http.post(
      Uri.parse('$baseUrl/api/nursing/diagnostic/start'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'num_questions': numQuestions}),
    );
    _check(response);
    final data = jsonDecode(response.body) as Map<String, dynamic>;
    final list = data['questions'] as List<dynamic>;
    return list.map((e) => NursingQuestion.fromJson(e as Map<String, dynamic>)).toList();
  }

  Future<List<NursingQuestion>> startMock({String patternKey = 'mhsrb_staff_nurse'}) async {
    final response = await http.post(
      Uri.parse('$baseUrl/api/nursing/mock/start?pattern_key=$patternKey'),
      headers: {'Content-Type': 'application/json'},
    );
    _check(response);
    final data = jsonDecode(response.body) as Map<String, dynamic>;
    final list = data['questions'] as List<dynamic>;
    return list.map((e) => NursingQuestion.fromJson(e as Map<String, dynamic>)).toList();
  }

  Future<CapabilityAnalysis> analyzeAttempts(List<Attempt> attempts) async {
    final response = await http.post(
      Uri.parse('$baseUrl/api/nursing/analyze'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(attempts.map((a) => a.toJson()).toList()),
    );
    _check(response);
    return CapabilityAnalysis.fromJson(jsonDecode(response.body) as Map<String, dynamic>);
  }

  Future<String> exportPdf(List<Attempt> attempts, {int topN = 3}) async {
    final response = await http.post(
      Uri.parse('$baseUrl/api/nursing/pdf'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'attempts': attempts.map((a) => a.toJson()).toList(), 'top_n': topN}),
    );
    _check(response);
    return response.body;
  }

  Future<Map<String, dynamic>> reportQuestion(int questionId, String reason) async {
    final response = await http.post(
      Uri.parse('$baseUrl/api/nursing/report'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'question_id': questionId, 'reason': reason}),
    );
    _check(response);
    return jsonDecode(response.body) as Map<String, dynamic>;
  }

  void _check(http.Response response) {
    if (response.statusCode < 200 || response.statusCode >= 300) {
      throw Exception('Nursing API error ${response.statusCode}: ${response.body}');
    }
  }
}
