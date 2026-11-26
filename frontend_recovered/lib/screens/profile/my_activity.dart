import 'package:flutter/material.dart';

import '../../app/app_session.dart';
import '../../data/auth_api.dart';
import '../../data/report_queue.dart';
import '../../data/review_queue.dart';

class MyActivity extends StatefulWidget {
  const MyActivity({super.key});
  @override
  State<MyActivity> createState() => _MyActivityState();
}

class _MyActivityState extends State<MyActivity> {
  late Future<_ActivityData> _data = _load();

  Future<_ActivityData> _load() async {
    final session = AppSession.instance;
    final email = session.email;
    final pendingReports =
        (await ReportQueue.read()).where((e) => e.ownerEmail == email).toList();
    final pendingReviews =
        (await ReviewQueue.read()).where((e) => e.ownerEmail == email).toList();
    Map<String, dynamic>? reports;
    Map<String, dynamic>? reviews;
    if (session.token != null) {
      try {
        reports = await AuthApi.myReports(session.token!);
      } catch (_) {/* Offline history remains available. */}
      try {
        reviews = await AuthApi.myReviews(session.token!);
      } catch (_) {/* Offline history remains available. */}
    }
    return _ActivityData(pendingReports, pendingReviews, reports, reviews);
  }

  void _refresh() => setState(() => _data = _load());

  Future<void> _deleteSentReport(String id) async {
    final confirmed = await showDialog<bool>(
        context: context,
        builder: (dialogContext) => AlertDialog(
              title: const Text('Delete report?'),
              content: const Text(
                  'This will remove your submitted report from VirasatAI.'),
              actions: [
                TextButton(
                    onPressed: () => Navigator.pop(dialogContext, false),
                    child: const Text('Cancel')),
                TextButton(
                    onPressed: () => Navigator.pop(dialogContext, true),
                    child: const Text('Delete')),
              ],
            ));
    if (confirmed != true) return;
    try {
      await AuthApi.deleteReport(AppSession.instance.token!, id);
      _refresh();
    } on AuthApiException catch (error) {
      if (mounted) {
        ScaffoldMessenger.of(context)
            .showSnackBar(SnackBar(content: Text(error.message)));
      }
    }
  }

  @override
  Widget build(BuildContext context) => Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(children: [
            const Expanded(
                child: Text('My reports & reviews',
                    style:
                        TextStyle(fontSize: 19, fontWeight: FontWeight.bold))),
            IconButton(
                tooltip: 'Refresh activity',
                onPressed: _refresh,
                icon: const Icon(Icons.refresh)),
          ]),
          FutureBuilder<_ActivityData>(
              future: _data,
              builder: (context, snapshot) {
                if (snapshot.connectionState != ConnectionState.done) {
                  return const LinearProgressIndicator();
                }
                if (snapshot.hasError || !snapshot.hasData) {
                  return Card(
                    child: ListTile(
                      title: const Text('Activity could not load'),
                      subtitle: const Text('Please try refreshing this page.'),
                      trailing: IconButton(
                        tooltip: 'Retry activity',
                        onPressed: _refresh,
                        icon: const Icon(Icons.refresh),
                      ),
                    ),
                  );
                }
                final data = snapshot.data!;
                final sentReports = (data.reports?['reports'] as List?) ?? [];
                final sentReviews = (data.reviews?['reviews'] as List?) ?? [];
                return Card(
                    child: Column(children: [
                  if (data.pendingReports.isEmpty &&
                      data.pendingReviews.isEmpty &&
                      sentReports.isEmpty &&
                      sentReviews.isEmpty)
                    const ListTile(title: Text('No reports or reviews yet')),
                  for (final item in data.pendingReports)
                    ListTile(
                        leading: const Icon(Icons.schedule),
                        title: Text('Report · ${item.placeId}'),
                        subtitle:
                            const Text('Saved on phone · waiting to sync'),
                        trailing: IconButton(
                            tooltip: 'Delete report draft',
                            icon: const Icon(Icons.delete_outline),
                            onPressed: () async {
                              await ReportQueue.remove(item.clientId);
                              _refresh();
                            })),
                  for (final item in sentReports)
                    ListTile(
                        leading: const Icon(Icons.report_outlined),
                        title: Text('Report · ${item['placeId'] ?? 'Place'}'),
                        subtitle:
                            Text('Submitted · ${item['status'] ?? 'received'}'),
                        trailing: item['status'] == 'submitted'
                            ? IconButton(
                                tooltip: 'Delete submitted report',
                                icon: const Icon(Icons.delete_outline),
                                onPressed: () =>
                                    _deleteSentReport(item['id'] as String))
                            : null),
                  for (final item in data.pendingReviews)
                    ListTile(
                        leading: const Icon(Icons.schedule),
                        title:
                            Text('Review · ${item.placeId} · ${item.rating} ★'),
                        subtitle:
                            const Text('Saved on phone · waiting to post'),
                        trailing: IconButton(
                            tooltip: 'Delete review draft',
                            icon: const Icon(Icons.delete_outline),
                            onPressed: () async {
                              await ReviewQueue.remove(
                                  item.ownerEmail, item.placeId);
                              _refresh();
                            })),
                  for (final item in sentReviews)
                    ListTile(
                        leading: const Icon(Icons.star_outline),
                        title: Text(
                            'Review · ${item['placeId'] ?? 'Place'} · ${item['rating'] ?? ''} ★'),
                        subtitle: Text(item['comment']?.toString() ?? '')),
                  if (AppSession.instance.token != null &&
                      (data.reports == null || data.reviews == null))
                    const ListTile(
                        subtitle: Text(
                            'Online history could not load. Pull refresh when connected.')),
                ]));
              }),
        ],
      );
}

class _ActivityData {
  const _ActivityData(
      this.pendingReports, this.pendingReviews, this.reports, this.reviews);
  final List<PendingReport> pendingReports;
  final List<PendingReview> pendingReviews;
  final Map<String, dynamic>? reports;
  final Map<String, dynamic>? reviews;
}
