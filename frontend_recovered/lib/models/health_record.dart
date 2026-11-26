/// Represents one historical monument health observation record in the VirasatAI system.
class HealthRecord {
  final String id;
  final DateTime date;
  final double healthScore;
  final List<String> detectedIssues;
  final String summary;
  final String? imageUrl;

  const HealthRecord({
    required this.id,
    required this.date,
    required this.healthScore,
    required this.detectedIssues,
    required this.summary,
    this.imageUrl,
  });
}
