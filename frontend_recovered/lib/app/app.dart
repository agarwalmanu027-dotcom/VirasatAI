import 'dart:async';

import 'package:flutter/material.dart';
import '../data/report_queue.dart';
import '../data/review_queue.dart';
import 'app_session.dart';
import 'routes.dart';
import 'theme.dart';

class VirasatApp extends StatefulWidget {
  const VirasatApp({super.key});

  @override
  State<VirasatApp> createState() => _VirasatAppState();
}

class _VirasatAppState extends State<VirasatApp> with WidgetsBindingObserver {
  Timer? _syncTimer;
  String? _locationToken;

  void _sync() {
    if (AppSession.instance.token == null) return;
    unawaited(ReportQueue.syncCurrentUser().catchError((_) => 0));
    unawaited(ReviewQueue.syncCurrentUser().catchError((_) => 0));
  }

  void _onSession() {
    _sync();
    final token = AppSession.instance.token;
    if (token == null) {
      _locationToken = null;
    } else if (token != _locationToken) {
      _locationToken = token;
      unawaited(
          ReportQueue.currentLocation().catchError((_) => <String, double>{}));
    }
  }

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);
    AppSession.instance.addListener(_onSession);
    _syncTimer = Timer.periodic(const Duration(seconds: 30), (_) => _sync());
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    if (state == AppLifecycleState.resumed) _sync();
  }

  @override
  void dispose() {
    _syncTimer?.cancel();
    AppSession.instance.removeListener(_onSession);
    WidgetsBinding.instance.removeObserver(this);
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp.router(
      title: 'VirasatAI',
      theme: AppTheme.light,
      routerConfig: AppRoutes.router,
      debugShowCheckedModeBanner: false,
    );
  }
}
