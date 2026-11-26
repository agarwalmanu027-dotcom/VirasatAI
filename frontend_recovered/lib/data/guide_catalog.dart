import 'dart:convert';

import 'package:flutter/services.dart';

/// Browseable heritage content, packaged from the project's reviewed library.
class GuideEntry {
  const GuideEntry({
    required this.id,
    required this.name,
    required this.groupId,
    required this.groupOrder,
    required this.isMain,
    required this.ready,
    required this.pendingReason,
    required this.location,
    required this.overview,
    required this.overviewHindi,
    required this.facts,
    required this.storyEnglish,
    required this.storyHindi,
    required this.photos,
    this.factsHindi = const [],
    this.factLabels = const [],
    this.factLabelsHindi = const [],
    this.detailsSummaryHindi = '',
    this.history = '',
    this.historyHindi = '',
    this.architecture = '',
    this.architectureHindi = '',
  });

  final String id;
  final String name;
  final String groupId;
  final int groupOrder;
  final bool isMain;
  final bool ready;
  final String? pendingReason;
  final String location;
  final String overview;
  final String overviewHindi;
  final List<String> facts;
  final String storyEnglish;
  final String storyHindi;
  final List<String> photos;
  final List<String> factsHindi;
  final List<String> factLabels;
  final List<String> factLabelsHindi;
  final String detailsSummaryHindi;
  final String history;
  final String historyHindi;
  final String architecture;
  final String architectureHindi;

  factory GuideEntry.fromJson(Map<String, dynamic> data) => GuideEntry(
        id: data['id'] as String,
        name: data['name'] as String,
        groupId: data['groupId'] as String,
        groupOrder: data['groupOrder'] as int,
        isMain: data['isMain'] as bool,
        ready: data['ready'] as bool,
        pendingReason: data['pendingReason'] as String?,
        location: data['location'] as String? ?? '',
        overview: data['overview'] as String? ?? '',
        overviewHindi: data['overviewHindi'] as String? ?? '',
        facts: List<String>.from(data['facts'] as List),
        storyEnglish: data['storyEnglish'] as String? ?? '',
        storyHindi: data['storyHindi'] as String? ?? '',
        photos: List<String>.from(data['photos'] as List),
        factsHindi: List<String>.from(data['factsHindi'] as List? ?? const []),
        factLabels: List<String>.from(data['factLabels'] as List? ?? const []),
        factLabelsHindi:
            List<String>.from(data['factLabelsHindi'] as List? ?? const []),
        detailsSummaryHindi: data['detailsSummaryHindi'] as String? ?? '',
        history: data['history'] as String? ?? '',
        historyHindi: data['historyHindi'] as String? ?? '',
        architecture: data['architecture'] as String? ?? '',
        architectureHindi: data['architectureHindi'] as String? ?? '',
      );
}

class GuideCatalog {
  GuideCatalog(this.entries)
      : byId = {for (final entry in entries) entry.id: entry};

  final List<GuideEntry> entries;
  final Map<String, GuideEntry> byId;

  List<GuideEntry> get mainGroups =>
      entries.where((entry) => entry.isMain).toList();

  List<GuideEntry> nearbyFor(String mainId) => entries
      .where((entry) => !entry.isMain && entry.groupId == mainId)
      .toList();

  static Future<GuideCatalog>? _cached;

  static Future<GuideCatalog> load() => _cached ??= _read();

  static Future<GuideCatalog> _read() async {
    final raw = await rootBundle.loadString('assets/data/guide_catalog.json');
    final decoded = jsonDecode(raw) as Map<String, dynamic>;
    final records = decoded['entries'] as List;
    return GuideCatalog(records
        .map((record) => GuideEntry.fromJson(record as Map<String, dynamic>))
        .toList(growable: false));
  }
}

String guidePathFor(String id) {
  if (id == 'taj_mahal') return '/result/taj-mahal';
  if (id == 'qutub_minar') return '/result/qutub-minar';
  return '/guide/$id';
}
