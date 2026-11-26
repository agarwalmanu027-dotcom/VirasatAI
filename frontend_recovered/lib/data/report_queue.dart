import 'dart:convert';
import 'dart:math';

import 'package:flutter/services.dart';

import '../app/app_session.dart';
import 'auth_api.dart';

class PendingReport {
  const PendingReport(
      {required this.clientId,
      required this.ownerEmail,
      required this.placeId,
      required this.category,
      required this.description,
      required this.locationLabel,
      required this.createdAt,
      this.latitude,
      this.longitude,
      this.accuracyM,
      this.photoBase64});

  final String clientId;
  final String ownerEmail;
  final String placeId;
  final String category;
  final String description;
  final String locationLabel;
  final String createdAt;
  final double? latitude;
  final double? longitude;
  final double? accuracyM;
  final String? photoBase64;

  Map<String, dynamic> toJson() => {
        'clientId': clientId,
        'ownerEmail': ownerEmail,
        'placeId': placeId,
        'category': category,
        'description': description,
        'locationLabel': locationLabel,
        'createdAt': createdAt,
        'latitude': latitude,
        'longitude': longitude,
        'accuracyM': accuracyM,
        'photoBase64': photoBase64,
      };

  factory PendingReport.fromJson(Map<String, dynamic> json) => PendingReport(
        clientId: json['clientId'] as String,
        ownerEmail: json['ownerEmail'] as String,
        placeId: json['placeId'] as String,
        category: json['category'] as String,
        description: json['description'] as String,
        locationLabel: json['locationLabel'] as String? ?? '',
        createdAt: json['createdAt'] as String,
        latitude: (json['latitude'] as num?)?.toDouble(),
        longitude: (json['longitude'] as num?)?.toDouble(),
        accuracyM: (json['accuracyM'] as num?)?.toDouble(),
        photoBase64: json['photoBase64'] as String?,
      );
}

class ReportQueue {
  static const _channel = MethodChannel('virasatai/reports');
  static bool _syncing = false;
  static Future<Map<String, double>>? _locationRequest;

  static Future<Map<String, double>> currentLocation() {
    return _locationRequest ??=
        _readLocation().whenComplete(() => _locationRequest = null);
  }

  static Future<Map<String, double>> _readLocation() async {
    final result = await _channel
        .invokeMapMethod<String, dynamic>('location')
        .timeout(const Duration(seconds: 15));
    if (result == null) throw PlatformException(code: 'NO_FIX');
    return {
      for (final key in ['latitude', 'longitude', 'accuracyM'])
        key: (result[key] as num).toDouble()
    };
  }

  static Future<List<PendingReport>> read() async {
    final raw = await _channel.invokeMethod<String>('read') ?? '[]';
    final items = jsonDecode(raw) as List<dynamic>;
    return items
        .map((item) => PendingReport.fromJson(item as Map<String, dynamic>))
        .toList();
  }

  static Future<void> _write(List<PendingReport> items) =>
      _channel.invokeMethod<void>(
          'write', jsonEncode(items.map((e) => e.toJson()).toList()));

  static String newClientId() {
    final random = Random.secure();
    final bytes = List<int>.generate(16, (_) => random.nextInt(256));
    bytes[6] = (bytes[6] & 0x0f) | 0x40;
    bytes[8] = (bytes[8] & 0x3f) | 0x80;
    final hex = bytes.map((b) => b.toRadixString(16).padLeft(2, '0')).join();
    return '${hex.substring(0, 8)}-${hex.substring(8, 12)}-${hex.substring(12, 16)}-${hex.substring(16, 20)}-${hex.substring(20)}';
  }

  static Future<void> add(PendingReport report) async {
    final items = await read();
    if (items.length >= 10) {
      throw const AuthApiException('10 drafts save hain. Pehle sync karo.');
    }
    items.add(report);
    await _write(items);
  }

  static Future<void> remove(String clientId) async {
    final items = await read();
    items.removeWhere((item) => item.clientId == clientId);
    await _write(items);
  }

  static Future<int> syncCurrentUser() async {
    if (_syncing) return 0;
    final session = AppSession.instance;
    final token = session.token;
    final email = session.email;
    if (token == null || email == null || !AuthApi.isConfigured) {
      throw const AuthApiException(
          'Real login aur connected server sync ke liye zaroori hai.');
    }
    _syncing = true;
    try {
      final items = await read();
      var sent = 0;
      for (final item in List<PendingReport>.from(items)) {
        if (item.ownerEmail != email) continue;
        await AuthApi.createReport(token, item.toJson());
        items.removeWhere((queued) => queued.clientId == item.clientId);
        await _write(items);
        sent++;
      }
      return sent;
    } finally {
      _syncing = false;
    }
  }
}
