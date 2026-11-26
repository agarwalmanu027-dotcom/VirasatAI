import 'dart:async';
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../app/theme.dart';

/// Screen displayed while identifying a scanned monument.
class AnalysisScreen extends StatefulWidget {
  const AnalysisScreen({super.key});

  @override
  State<AnalysisScreen> createState() => _AnalysisScreenState();
}

class _AnalysisScreenState extends State<AnalysisScreen> {
  Timer? _navigationTimer;

  @override
  void initState() {
    super.initState();
    _navigationTimer = Timer(const Duration(milliseconds: 2000), _goToResult);
  }

  void _goToResult() {
    if (!mounted) return;
    context.go('/result/taj-mahal');
  }

  @override
  void dispose() {
    _navigationTimer?.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Scaffold(
      backgroundColor: AppTheme.backgroundColor,
      body: SafeArea(
        child: Center(
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 32),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                const SizedBox(
                  width: 32,
                  height: 32,
                  child: CircularProgressIndicator(
                    strokeWidth: 3,
                    valueColor: AlwaysStoppedAnimation<Color>(
                      AppTheme.accentColor,
                    ),
                  ),
                ),
                const SizedBox(height: 24),
                Text(
                  'Identifying Monument',
                  textAlign: TextAlign.center,
                  style: theme.textTheme.titleLarge?.copyWith(
                    color: AppTheme.primaryColor,
                    fontWeight: FontWeight.w700,
                    letterSpacing: -0.2,
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  'Analyzing your image...',
                  textAlign: TextAlign.center,
                  style: theme.textTheme.bodyMedium?.copyWith(
                    color: AppTheme.secondaryTextColor,
                    height: 1.4,
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}



