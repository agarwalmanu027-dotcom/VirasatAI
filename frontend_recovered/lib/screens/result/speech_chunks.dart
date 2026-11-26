/// Keeps browser speech utterances short without dropping story words.
List<String> splitSpeechChunks(String story, {int maxLength = 220}) {
  final normalized = story.replaceAll(RegExp(r'\s+'), ' ').trim();
  if (normalized.isEmpty) return const [];

  final sentences = normalized.split(RegExp(r'(?<=[.!?।])\s+'));
  final chunks = <String>[];
  var current = '';

  void addWords(String sentence) {
    for (final word in sentence.split(' ')) {
      if (word.isEmpty) continue;
      if (current.isNotEmpty && current.length + word.length + 1 > maxLength) {
        chunks.add(current);
        current = '';
      }
      current = current.isEmpty ? word : '$current $word';
    }
  }

  for (final sentence in sentences) {
    if (sentence.isEmpty) continue;
    if (sentence.length > maxLength) {
      if (current.isNotEmpty) {
        chunks.add(current);
        current = '';
      }
      addWords(sentence);
    } else if (current.isEmpty) {
      current = sentence;
    } else if (current.length + sentence.length + 1 <= maxLength) {
      current = '$current $sentence';
    } else {
      chunks.add(current);
      current = sentence;
    }
  }
  if (current.isNotEmpty) chunks.add(current);
  return chunks;
}
