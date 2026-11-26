import 'package:flutter/foundation.dart';
import '../data/saved_session.dart';

/// The active UI session. Real account credentials are saved on Android.
class AppSession extends ChangeNotifier {
  AppSession._();

  static final AppSession instance = AppSession._();

  String? _email;
  String? _displayName;
  String? _token;

  bool get isSignedIn => _email != null;
  String? get email => _email;
  String get displayName => _displayName ?? 'Explorer';
  String? get token => _token;
  bool get isDemo => isSignedIn && _token == null;

  Future<void> restore() async {
    try {
      final saved = await SavedSession.read();
      if (saved == null) return;
      final expiry = DateTime.parse(saved['expiresAt'] as String);
      if (!expiry.isAfter(DateTime.now().toUtc())) {
        await SavedSession.clear();
        return;
      }
      signInReal(
          email: saved['email'] as String,
          displayName: saved['displayName'] as String,
          token: saved['token'] as String);
    } catch (_) {
      // Corrupt or unavailable saved data must not prevent the login screen.
    }
  }

  Future<void> saveReal(
      {required String email,
      required String displayName,
      required String token,
      required DateTime expiresAt}) async {
    await SavedSession.write(
        email: email,
        displayName: displayName,
        token: token,
        expiresAt: expiresAt);
    signInReal(email: email, displayName: displayName, token: token);
  }

  void signInForDemo(String email) {
    _token = null;
    _email = email.trim().toLowerCase();
    _displayName = _email!.split('@').first.replaceAll(RegExp(r'[._-]+'), ' ');
    notifyListeners();
  }

  void signInReal(
      {required String email,
      required String displayName,
      required String token}) {
    _email = email;
    _displayName = displayName;
    _token = token;
    notifyListeners();
  }

  void updateDisplayName(String name) {
    if (!isSignedIn) return;
    final trimmed = name.trim();
    if (trimmed.isEmpty) return;
    _displayName = trimmed;
    notifyListeners();
  }

  void signOut() {
    _email = null;
    _displayName = null;
    _token = null;
    notifyListeners();
    SavedSession.clear().catchError((_) {});
  }
}
