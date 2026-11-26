import 'package:flutter/material.dart';
import '../../app/app_session.dart';
import '../../data/auth_api.dart';
import '../../data/review_queue.dart';

class ReviewsPanel extends StatefulWidget {
  const ReviewsPanel({super.key, required this.placeId, required this.hindi});
  final String placeId;
  final bool hindi;
  @override
  State<ReviewsPanel> createState() => _ReviewsPanelState();
}

class _ReviewsPanelState extends State<ReviewsPanel> {
  final comment = TextEditingController();
  int rating = 5;
  late Future<Map<String, dynamic>> data = AuthApi.reviews(widget.placeId);
  bool saving = false;
  String? message;

  @override
  void dispose() {
    comment.dispose();
    super.dispose();
  }

  Future<void> submit() async {
    final token = AppSession.instance.token;
    final email = AppSession.instance.email;
    if (email == null) return;
    setState(() {
      saving = true;
      message = null;
    });
    try {
      await ReviewQueue.add(PendingReview(
          ownerEmail: email,
          placeId: widget.placeId,
          rating: rating,
          comment: comment.text.trim(),
          createdAt: DateTime.now().toUtc().toIso8601String()));
      var sent = false;
      if (token != null) {
        try {
          await ReviewQueue.syncCurrentUser();
          sent = !(await ReviewQueue.read()).any((item) =>
              item.ownerEmail == email && item.placeId == widget.placeId);
        } catch (_) {/* Review remains on this phone. */}
      }
      if (mounted) {
        setState(() {
          if (sent) data = AuthApi.reviews(widget.placeId);
          saving = false;
          comment.clear();
          message = sent
              ? (widget.hindi
                  ? 'आपका रिव्यू पोस्ट हो गया।'
                  : 'Your review was posted.')
              : (widget.hindi
                  ? 'रिव्यू फोन पर सेव है। ऑनलाइन होने पर भेजा जाएगा।'
                  : 'Review saved on this phone. It will post when online.');
        });
      }
    } catch (_) {
      if (mounted) {
        setState(() => saving = false);
        ScaffoldMessenger.of(context).showSnackBar(const SnackBar(
            content: Text('Review could not be saved on this phone.')));
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Card(
        child: Padding(
      padding: const EdgeInsets.all(16),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Text(widget.hindi ? 'लोगों की राय' : 'Visitor reviews',
            style: Theme.of(context).textTheme.titleLarge),
        FutureBuilder<Map<String, dynamic>>(
            future: data,
            builder: (context, snapshot) {
              if (snapshot.hasError) {
                return Text(widget.hindi
                    ? 'रिव्यू अभी लोड नहीं हुए।'
                    : 'Reviews could not load.');
              }
              if (!snapshot.hasData) {
                return const LinearProgressIndicator();
              }
              final result = snapshot.data!;
              final reviews = result['reviews'] as List;
              return Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                        '${result['count']} reviews · ${(result['average'] as num?)?.toStringAsFixed(1) ?? '—'} / 5'),
                    if (reviews.isEmpty)
                      Padding(
                        padding: const EdgeInsets.only(top: 8),
                        child: Text(widget.hindi
                            ? 'अभी कोई रिव्यू नहीं है। पहला रिव्यू लिखें।'
                            : 'No reviews yet. Be the first to add one.'),
                      ),
                    for (final item in reviews.take(5))
                      ListTile(
                        contentPadding: EdgeInsets.zero,
                        title: Text(
                            '${item['displayName']} · ${item['rating']} ★'),
                        subtitle: Text(item['comment'] as String),
                      ),
                  ]);
            }),
        if (AppSession.instance.email != null) ...[
          Wrap(children: [
            for (var value = 1; value <= 5; value++)
              IconButton(
                tooltip: '$value stars',
                onPressed: () => setState(() => rating = value),
                icon: Icon(value <= rating ? Icons.star : Icons.star_border),
              )
          ]),
          TextField(
              controller: comment,
              maxLength: 1000,
              decoration: InputDecoration(
                  labelText: widget.hindi
                      ? 'आपकी राय (वैकल्पिक)'
                      : 'Your review (optional)')),
          FilledButton(
              onPressed: saving ? null : submit,
              child: Text(widget.hindi ? 'रिव्यू भेजें' : 'Submit review')),
          if (message != null)
            Padding(
              padding: const EdgeInsets.only(top: 8),
              child:
                  Text(message!, style: const TextStyle(color: Colors.green)),
            ),
        ] else
          Text(widget.hindi
              ? 'रिव्यू लिखने के लिए लॉग इन करें।'
              : 'Sign in to write a review.'),
      ]),
    ));
  }
}
