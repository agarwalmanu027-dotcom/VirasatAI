import 'health_record.dart';

/// Represents a heritage monument in the VirasatAI system.
/// Immutable model containing current health score, location, and metadata.
class Monument {
  final String id;
  final String name;
  final String location;
  final String description;
  final String imageUrl;
  final double healthScore;
  final String era;
  final String architecturalStyle;
  final List<HealthRecord> healthHistory;

  const Monument({
    required this.id,
    required this.name,
    required this.location,
    required this.description,
    required this.imageUrl,
    required this.healthScore,
    required this.era,
    required this.architecturalStyle,
    this.healthHistory = const [],
  });
}
