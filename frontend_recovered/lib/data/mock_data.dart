import '../models/monument.dart';
import '../models/health_record.dart';
import '../models/scan_result.dart';

/// Prototype mock data for VirasatAI demonstration.
class MockData {
  MockData._();

  /// Standard damage types recognized by VirasatAI AI model.
  static const List<String> damageTypes = [
    'Cracks',
    'Surface staining',
    'Vegetation',
    'Graffiti',
    'Spalling',
  ];

  /// Sample mock monuments for Agra heritage sites.
  static final List<Monument> monuments = [
    Monument(
      id: 'akbars_tomb',
      name: "Akbar's Tomb",
      location: 'Sikandra, Agra',
      description:
          "The tomb of the Mughal Emperor Akbar, built in 1605–1613, showcasing a blend of Hindu and Islamic architectural styles across five sandstone levels.",
      imageUrl: 'https://images.unsplash.com/photo-1564507592333-c60657eea523?w=800',
      healthScore: 82.5,
      era: 'Mughal (1613)',
      architecturalStyle: 'Mughal Architecture',
      healthHistory: [
        HealthRecord(
          id: 'hr_akbar_01',
          date: DateTime(2026, 6, 15),
          healthScore: 82.5,
          detectedIssues: ['Cracks', 'Surface staining'],
          summary: 'Minor structural hairline cracks observed on north gateway arch; surface discoloration noted on sandstone panels.',
          imageUrl: 'https://images.unsplash.com/photo-1564507592333-c60657eea523?w=400',
        ),
        HealthRecord(
          id: 'hr_akbar_02',
          date: DateTime(2025, 11, 10),
          healthScore: 85.0,
          detectedIssues: ['Vegetation'],
          summary: 'Routine scan identified small wild growth roots along upper cornice mortar joints.',
        ),
      ],
    ),
    Monument(
      id: 'itmad_ud_daulah',
      name: "Itmad-ud-Daulah's Tomb",
      location: 'Moti Bagh, Agra',
      description:
          "Often called the 'Baby Taj', this mausoleum features delicate Pietra Dura marble inlay work and intricate lattice screens along the Yamuna riverbank.",
      imageUrl: 'https://images.unsplash.com/photo-1548013146-72479768bada?w=800',
      healthScore: 78.0,
      era: 'Mughal (1628)',
      architecturalStyle: 'Indo-Islamic Marble Inlay',
      healthHistory: [
        HealthRecord(
          id: 'hr_itmad_01',
          date: DateTime(2026, 7, 20),
          healthScore: 78.0,
          detectedIssues: ['Surface staining', 'Spalling'],
          summary: 'Acidic rainwater runoff staining marble facades. Minor marble spalling observed on east pavilion base.',
          imageUrl: 'https://images.unsplash.com/photo-1548013146-72479768bada?w=400',
        ),
        HealthRecord(
          id: 'hr_itmad_02',
          date: DateTime(2025, 12, 05),
          healthScore: 81.5,
          detectedIssues: ['Surface staining'],
          summary: 'Discoloration on riverside outer marble wall due to atmospheric pollutants.',
        ),
      ],
    ),
    Monument(
      id: 'mehtab_bagh',
      name: 'Mehtab Bagh',
      location: 'Nagla Devjit, Agra',
      description:
          'A charbagh garden complex aligned directly across the Yamuna River from the Taj Mahal, providing iconic views and environmental buffer.',
      imageUrl: 'https://images.unsplash.com/photo-1585135497273-1a86b09fe70e?w=800',
      healthScore: 91.0,
      era: 'Mughal (1530)',
      architecturalStyle: 'Charbagh Garden Layout',
      healthHistory: [
        HealthRecord(
          id: 'hr_mehtab_01',
          date: DateTime(2026, 8, 01),
          healthScore: 91.0,
          detectedIssues: ['Vegetation'],
          summary: 'Boundary wall mortar intact; minor overgrown vegetation needs routine trimming.',
        ),
      ],
    ),
    Monument(
      id: 'agra_fort',
      name: 'Agra Fort',
      location: 'Rakabganj, Agra',
      description:
          'Historical red sandstone fort and UNESCO World Heritage site, which served as the main residence of Mughal emperors until 1638.',
      imageUrl: 'https://images.unsplash.com/photo-1599661046827-dacff0c0f09a?w=800',
      healthScore: 74.5,
      era: 'Mughal (1573)',
      architecturalStyle: 'Mughal Fortified Architecture',
      healthHistory: [
        HealthRecord(
          id: 'hr_fort_01',
          date: DateTime(2026, 8, 12),
          healthScore: 74.5,
          detectedIssues: ['Cracks', 'Spalling', 'Graffiti'],
          summary: 'Deep stress crack detected near Jahangiri Mahal gateway. Surface spalling on outer ramparts; minor surface graffiti logged near lower passageway.',
          imageUrl: 'https://images.unsplash.com/photo-1599661046827-dacff0c0f09a?w=400',
        ),
        HealthRecord(
          id: 'hr_fort_02',
          date: DateTime(2026, 03, 14),
          healthScore: 77.0,
          detectedIssues: ['Cracks', 'Graffiti'],
          summary: 'Hairline cracks recorded along tourist walkway walls. Superficial pencil markings logged.',
        ),
      ],
    ),
  ];

  /// Recent visitor scan results for demonstration.
  static final List<ScanResult> mockScanResults = [
    ScanResult(
      id: 'scan_001',
      monumentId: 'agra_fort',
      monumentName: 'Agra Fort',
      capturedImageUrl: 'https://images.unsplash.com/photo-1599661046827-dacff0c0f09a?w=600',
      healthScore: 74.5,
      detectedIssues: ['Cracks', 'Spalling'],
      confidence: 0.92,
      timestamp: DateTime(2026, 8, 28, 14, 30),
    ),
    ScanResult(
      id: 'scan_002',
      monumentId: 'itmad_ud_daulah',
      monumentName: "Itmad-ud-Daulah's Tomb",
      capturedImageUrl: 'https://images.unsplash.com/photo-1548013146-72479768bada?w=600',
      healthScore: 78.0,
      detectedIssues: ['Surface staining'],
      confidence: 0.88,
      timestamp: DateTime(2026, 8, 27, 11, 15),
    ),
  ];
}
