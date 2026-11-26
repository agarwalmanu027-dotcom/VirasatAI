/// Represents the AI analysis result of a visitor monument scan.
class ScanResult {
  final String id;
  final String monumentId;
  final String monumentName;
  final String capturedImageUrl;
  final double healthScore;
  final List<String> detectedIssues;
  final double confidence;
  final DateTime timestamp;

  const ScanResult({
    required this.id,
    required this.monumentId,
    required this.monumentName,
    required this.capturedImageUrl,
    required this.healthScore,
    required this.detectedIssues,
    required this.confidence,
    required this.timestamp,
  });
}
