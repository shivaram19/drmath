import 'dart:async';
import 'dart:convert';
import 'dart:io';

import 'package:flutter/services.dart';
import 'package:http/http.dart' as http;

import '../models/attempt.dart';
import '../models/capability.dart';
import '../models/nursing_question.dart';
import 'nursing_api_exception.dart';

/// HTTP client for the Dr. Math nursing API with offline fallback.
///
/// In production this points to the deployed backend. For development,
/// override [baseUrl] (e.g., `http://10.0.2.2:8000` for Android emulator).
class NursingApiService {
  final String baseUrl;
  final Duration timeout;
  final AssetBundle? assetBundle;

  NursingApiService({
    this.baseUrl = 'https://drmath.trelolabs.com',
    this.timeout = const Duration(seconds: 10),
    this.assetBundle,
  });

  Future<Map<String, dynamic>> fetchStatus() async {
    final response = await _get('$baseUrl/api/nursing/status');
    return jsonDecode(response.body) as Map<String, dynamic>;
  }

  Future<Map<String, dynamic>> fetchTopics() async {
    final response = await _get('$baseUrl/api/nursing/topics');
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

    try {
      final uri = Uri.parse('$baseUrl/api/nursing/questions')
          .replace(queryParameters: params);
      final response = await _get(uri.toString());
      final list = jsonDecode(response.body) as List<dynamic>;
      return list
          .map((e) => NursingQuestion.fromJson(e as Map<String, dynamic>))
          .toList();
    } on NursingApiException catch (_) {
      return _loadFallbackQuestions(
        subjectId: subjectId,
        topicId: topicId,
        cognitiveLevel: cognitiveLevel,
        context: context,
        difficulty: difficulty,
        conceptTag: conceptTag,
        limit: limit,
      );
    }
  }

  Future<List<NursingQuestion>> startDiagnostic({int numQuestions = 20}) async {
    try {
      final response = await _post(
        '$baseUrl/api/nursing/diagnostic/start',
        body: jsonEncode({'num_questions': numQuestions}),
      );
      final data = jsonDecode(response.body) as Map<String, dynamic>;
      final list = data['questions'] as List<dynamic>;
      return list
          .map((e) => NursingQuestion.fromJson(e as Map<String, dynamic>))
          .toList();
    } on NursingApiException catch (_) {
      final fallback = await _loadFallbackQuestions();
      return _shuffleAndLimit(fallback, numQuestions);
    }
  }

  Future<List<NursingQuestion>> startMock(
      {String patternKey = 'mhsrb_staff_nurse'}) async {
    try {
      final response = await _post(
        '$baseUrl/api/nursing/mock/start?pattern_key=$patternKey',
      );
      final data = jsonDecode(response.body) as Map<String, dynamic>;
      final list = data['questions'] as List<dynamic>;
      return list
          .map((e) => NursingQuestion.fromJson(e as Map<String, dynamic>))
          .toList();
    } on NursingApiException catch (_) {
      final fallback = await _loadFallbackQuestions();
      return _shuffleAndLimit(fallback, fallback.length);
    }
  }

  Future<CapabilityAnalysis> analyzeAttempts(List<Attempt> attempts) async {
    final response = await _post(
      '$baseUrl/api/nursing/analyze',
      body: jsonEncode(attempts.map((a) => a.toJson()).toList()),
    );
    return CapabilityAnalysis.fromJson(
        jsonDecode(response.body) as Map<String, dynamic>);
  }

  Future<String> exportPdf(List<Attempt> attempts, {int topN = 3}) async {
    final response = await _post(
      '$baseUrl/api/nursing/pdf',
      body: jsonEncode({
        'attempts': attempts.map((a) => a.toJson()).toList(),
        'top_n': topN,
      }),
    );
    return response.body;
  }

  Future<Map<String, dynamic>> reportQuestion(
      int questionId, String reason) async {
    final response = await _post(
      '$baseUrl/api/nursing/report',
      body: jsonEncode(
          {'question_id': questionId, 'reason': reason}),
    );
    return jsonDecode(response.body) as Map<String, dynamic>;
  }

  Future<http.Response> _get(String url) async {
    try {
      final response = await http
          .get(Uri.parse(url))
          .timeout(timeout);
      _check(response);
      return response;
    } on TimeoutException {
      throw const NursingApiException(
        message: 'Request timed out. Please check your connection.',
        isOffline: true,
      );
    } on SocketException {
      throw const NursingApiException(
        message: 'No internet connection.',
        isOffline: true,
      );
    } on NursingApiException {
      rethrow;
    } catch (e) {
      throw NursingApiException(message: 'Network error: $e');
    }
  }

  Future<http.Response> _post(String url, {String? body}) async {
    try {
      final response = await http
          .post(
            Uri.parse(url),
            headers: {'Content-Type': 'application/json'},
            body: body,
          )
          .timeout(timeout);
      _check(response);
      return response;
    } on TimeoutException {
      throw const NursingApiException(
        message: 'Request timed out. Please check your connection.',
        isOffline: true,
      );
    } on SocketException {
      throw const NursingApiException(
        message: 'No internet connection.',
        isOffline: true,
      );
    } on NursingApiException {
      rethrow;
    } catch (e) {
      throw NursingApiException(message: 'Network error: $e');
    }
  }

  void _check(http.Response response) {
    if (response.statusCode < 200 || response.statusCode >= 300) {
      throw NursingApiException(
        message: 'Nursing API error ${response.statusCode}: ${response.body}',
        statusCode: response.statusCode,
      );
    }
  }

  Future<List<NursingQuestion>> _loadFallbackQuestions({
    String? subjectId,
    String? topicId,
    String? cognitiveLevel,
    String? context,
    int? difficulty,
    String? conceptTag,
    int? limit,
  }) async {
    try {
      final bundle = assetBundle ?? rootBundle;
      final raw = await bundle.loadString('assets/nursing/nursing_seed_questions.json');
      final list = jsonDecode(raw) as List<dynamic>;
      var questions = list
          .map((e) => NursingQuestion.fromJson(e as Map<String, dynamic>))
          .toList();

      if (subjectId != null) {
        questions = questions.where((q) => q.subjectId == subjectId).toList();
      }
      if (topicId != null) {
        questions = questions.where((q) => q.topicId == topicId).toList();
      }
      if (cognitiveLevel != null) {
        questions =
            questions.where((q) => q.cognitiveLevel == cognitiveLevel).toList();
      }
      if (context != null) {
        questions = questions.where((q) => q.context == context).toList();
      }
      if (difficulty != null) {
        questions = questions.where((q) => q.difficulty == difficulty).toList();
      }
      if (conceptTag != null) {
        questions = questions.where((q) => q.conceptTag == conceptTag).toList();
      }
      if (limit != null && limit < questions.length) {
        questions = questions.sublist(0, limit);
      }
      return questions;
    } catch (e) {
      throw NursingApiException(
        message: 'Offline fallback failed: $e',
        isOffline: true,
      );
    }
  }

  List<NursingQuestion> _shuffleAndLimit(
      List<NursingQuestion> questions, int limit) {
    final copy = List<NursingQuestion>.of(questions)..shuffle();
    return copy.length > limit ? copy.sublist(0, limit) : copy;
  }
}
