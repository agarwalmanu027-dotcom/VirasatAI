import 'dart:convert';

import 'package:http/http.dart' as http;

/// Set at build time with --dart-define=VIRASATAI_API_BASE_URL=https://...
/// No server is bundled into a static web build or APK.
class AuthApi {
  static const baseUrl = String.fromEnvironment('VIRASATAI_API_BASE_URL',
      defaultValue: 'https://virasatai-api.agarwalmanu027.workers.dev');

  static bool get isConfigured => baseUrl.trim().isNotEmpty;

  static Uri _url(String path) {
    if (!isConfigured) {
      throw const AuthApiException('Account server is not configured yet.');
    }
    return Uri.parse('${baseUrl.replaceAll(RegExp(r'/$'), '')}$path');
  }

  static Future<Map<String, dynamic>> _request(
    String method,
    String path, {
    Map<String, dynamic>? body,
    String? token,
  }) async {
    final client = http.Client();
    try {
      final request = http.Request(method, _url(path));
      request.headers['Content-Type'] = 'application/json';
      if (token != null) request.headers['Authorization'] = 'Bearer $token';
      if (body != null) request.body = jsonEncode(body);
      final streamed =
          await client.send(request).timeout(const Duration(seconds: 12));
      final response = await http.Response.fromStream(streamed);
      final data = jsonDecode(response.body) as Map<String, dynamic>;
      if (response.statusCode < 200 || response.statusCode >= 300) {
        throw AuthApiException(
            data['message'] as String? ?? 'Account request failed.');
      }
      return data;
    } on AuthApiException {
      rethrow;
    } catch (_) {
      throw const AuthApiException(
          'Cannot reach the account server. Check your connection.');
    } finally {
      client.close();
    }
  }

  static Future<AuthResult> register(
      String name, String email, String password) async {
    final data = await _request('POST', '/auth/register', body: {
      'displayName': name,
      'email': email,
      'password': password,
    });
    return AuthResult.fromJson(data);
  }

  static Future<AuthResult> login(String email, String password) async {
    final data = await _request('POST', '/auth/login', body: {
      'email': email,
      'password': password,
    });
    return AuthResult.fromJson(data);
  }

  static Future<String> updateName(String token, String name) async {
    final data = await _request('PATCH', '/auth/me',
        token: token, body: {'displayName': name});
    return (data['user'] as Map<String, dynamic>)['displayName'] as String;
  }

  static Future<void> logout(String token) async {
    await _request('POST', '/auth/logout', token: token);
  }

  static Future<void> createReport(
      String token, Map<String, dynamic> report) async {
    await _request('POST', '/reports', token: token, body: {
      'clientId': report['clientId'],
      'placeId': report['placeId'],
      'category': report['category'],
      'description': report['description'],
      'locationLabel': report['locationLabel'],
      'latitude': report['latitude'],
      'longitude': report['longitude'],
      'accuracyM': report['accuracyM'],
      'photoBase64': report['photoBase64'],
    });
  }

  static Future<Map<String, dynamic>> myReports(String token) =>
      _request('GET', '/reports', token: token);

  static Future<void> deleteReport(String token, String reportId) async {
    await _request('DELETE', '/reports/$reportId', token: token);
  }

  static Future<Map<String, dynamic>> myReviews(String token) =>
      _request('GET', '/reviews/mine', token: token);

  static Future<Map<String, dynamic>> reviews(String placeId) =>
      _request('GET', '/places/$placeId/reviews');

  static Future<void> saveReview(
      String token, String placeId, int rating, String comment) async {
    await _request('POST', '/places/$placeId/reviews',
        token: token, body: {'rating': rating, 'comment': comment});
  }
}

class AuthResult {
  const AuthResult(
      {required this.token,
      required this.email,
      required this.displayName,
      required this.expiresAt});
  final String token;
  final String email;
  final String displayName;
  final DateTime expiresAt;

  factory AuthResult.fromJson(Map<String, dynamic> data) {
    final user = data['user'] as Map<String, dynamic>;
    return AuthResult(
      token: data['token'] as String,
      email: user['email'] as String,
      displayName: user['displayName'] as String,
      expiresAt: DateTime.parse(data['expiresAt'] as String),
    );
  }
}

class AuthApiException implements Exception {
  const AuthApiException(this.message);
  final String message;
}
