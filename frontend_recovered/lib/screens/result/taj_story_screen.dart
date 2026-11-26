import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import 'story_reader_screen.dart';

/// Displays the prepared Taj Mahal story in the guide's selected language.
class TajStoryScreen extends StatelessWidget {
  const TajStoryScreen({super.key, required this.isHindi});

  final bool isHindi;

  @override
  Widget build(BuildContext context) => StoryReaderScreen(
        titleEnglish: 'Taj Mahal story',
        titleHindi: 'ताज महल की कहानी',
        initialHindi: isHindi,
        storyEnglish: rootBundle.loadString('assets/stories/taj_mahal_en.txt'),
        storyHindi: rootBundle.loadString('assets/stories/taj_mahal_hi.txt'),
      );
}
