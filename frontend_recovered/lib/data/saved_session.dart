import 'dart:convert';

import 'package:flutter/services.dart';

class SavedSession {
  static const _channel = MethodChannel('virasatai/session');

  static Future<Map<String, dynamic>?> read() async {
    final raw = await _channel.invokeMethod<String>('read');
    if (raw == null) return null;
    return jsonDecode(raw) as Map<String, dynamic>;
  }

  static Future<void> write(
          {required String email,
          required String displayName,
          required String token,
          required DateTime expiresAt}) =>
      _channel.invokeMethod<void>(
          'write',
          jsonEncode({
            'email': email,
            'displayName': displayName,
            'token': token,
            'expiresAt': expiresAt.toUtc().toIso8601String(),
          }));

  static Future<void> clear() => _channel.invokeMethod<void>('clear');
}
