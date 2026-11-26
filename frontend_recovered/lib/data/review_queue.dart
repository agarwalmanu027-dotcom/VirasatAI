import 'dart:convert';

import 'package:flutter/services.dart';

import '../app/app_session.dart';
import 'auth_api.dart';

class PendingReview {
  const PendingReview(
      {required this.ownerEmail,
      required this.placeId,
      required this.rating,
      required this.comment,
      required this.createdAt});
  final String ownerEmail;
  final String placeId;
  final int rating;
  final String comment;
  final String createdAt;

  Map<String, dynamic> toJson() => {
        'ownerEmail': ownerEmail,
        'placeId': placeId,
        'rating': rating,
        'comment': comment,
        'createdAt': createdAt,
      };

  factory PendingReview.fromJson(Map<String, dynamic> json) => PendingReview(
        ownerEmail: json['ownerEmail'] as String,
        placeId: json['placeId'] as String,
        rating: json['rating'] as int,
        comment: json['comment'] as String? ?? '',
        createdAt: json['createdAt'] as String,
      );
}

class ReviewQueue {
  static const _channel = MethodChannel('virasatai/reviews');
  static bool _syncing = false;

  static Future<List<PendingReview>> read() async {
    final raw = await _channel.invokeMethod<String>('read') ?? '[]';
    return (jsonDecode(raw) as List)
        .map((item) => PendingReview.fromJson(item as Map<String, dynamic>))
        .toList();
  }

  static Future<void> _write(List<PendingReview> items) =>
      _channel.invokeMethod<void>(
          'write', jsonEncode(items.map((e) => e.toJson()).toList()));

  static Future<void> add(PendingReview review) async {
    final items = await read();
    items.removeWhere((item) =>
        item.ownerEmail == review.ownerEmail && item.placeId == review.placeId);
    items.add(review);
    await _write(items);
  }

  static Future<void> remove(String email, String placeId) async {
    final items = await read();
    items.removeWhere(
        (item) => item.ownerEmail == email && item.placeId == placeId);
    await _write(items);
  }

  static Future<int> syncCurrentUser() async {
    if (_syncing) return 0;
    final session = AppSession.instance;
    final token = session.token;
    final email = session.email;
    if (token == null || email == null || !AuthApi.isConfigured) return 0;
    _syncing = true;
    try {
      var sent = 0;
      for (final item in await read()) {
        if (item.ownerEmail != email) continue;
        await AuthApi.saveReview(
            token, item.placeId, item.rating, item.comment);
        await remove(email, item.placeId);
        sent++;
      }
      return sent;
    } finally {
      _syncing = false;
    }
  }
}
