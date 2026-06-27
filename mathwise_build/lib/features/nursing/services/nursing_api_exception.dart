/// Exception thrown by [NursingApiService] when a network or API call fails.
class NursingApiException implements Exception {
  final String message;
  final bool isOffline;
  final int? statusCode;

  const NursingApiException({
    required this.message,
    this.isOffline = false,
    this.statusCode,
  });

  @override
  String toString() => 'NursingApiException: $message';
}
