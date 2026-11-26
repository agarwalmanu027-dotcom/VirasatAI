import 'dart:async';

import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter_tts/flutter_tts.dart';

import '../../app/theme.dart';
import 'speech_chunks.dart';

// Hindi and English are packaged with the app. The other scheduled languages
// become selectable when the online translation service is connected.
const _storyLanguages = <String, String>{
  'en': 'English',
  'hi': 'Hindi',
  'as': 'Assamese',
  'bn': 'Bengali',
  'brx': 'Bodo',
  'doi': 'Dogri',
  'gu': 'Gujarati',
  'kn': 'Kannada',
  'ks': 'Kashmiri',
  'kok': 'Konkani',
  'mai': 'Maithili',
  'ml': 'Malayalam',
  'mni': 'Manipuri',
  'mr': 'Marathi',
  'ne': 'Nepali',
  'or': 'Odia',
  'pa': 'Punjabi',
  'sa': 'Sanskrit',
  'sat': 'Santali',
  'sd': 'Sindhi',
  'ta': 'Tamil',
  'te': 'Telugu',
  'ur': 'Urdu',
};

/// Prepared English/Hindi story with device speech and a language voice choice.
class StoryReaderScreen extends StatefulWidget {
  const StoryReaderScreen({
    super.key,
    required this.titleEnglish,
    required this.titleHindi,
    required this.storyEnglish,
    required this.storyHindi,
    required this.initialHindi,
  });

  final String titleEnglish;
  final String titleHindi;
  final Future<String> storyEnglish;
  final Future<String> storyHindi;
  final bool initialHindi;

  @override
  State<StoryReaderScreen> createState() => _StoryReaderScreenState();
}

class _StoryReaderScreenState extends State<StoryReaderScreen> {
  final FlutterTts _tts = FlutterTts();
  final List<Map<String, String>> _voices = [];
  Completer<void>? _chunkDone;
  String? _chosenVoice;
  late bool _isHindi;
  bool _speaking = false;
  bool _speechError = false;
  int _runId = 0;

  String _voiceKey(Map<String, String> voice) =>
      '${voice['locale']}|${voice['name']}';

  List<Map<String, String>> get _matchingVoices => _voices.where((voice) {
        final locale = (voice['locale'] ?? '').toLowerCase();
        return locale.startsWith(_isHindi ? 'hi' : 'en');
      }).toList()
        ..sort((a, b) {
          final preferred = _isHindi ? 'hi-in' : 'en-in';
          final aPreferred =
              (a['locale'] ?? '').toLowerCase().replaceAll('_', '-') ==
                  preferred;
          final bPreferred =
              (b['locale'] ?? '').toLowerCase().replaceAll('_', '-') ==
                  preferred;
          if (aPreferred != bPreferred) return aPreferred ? -1 : 1;
          return (a['name'] ?? '').compareTo(b['name'] ?? '');
        });

  @override
  void initState() {
    super.initState();
    _isHindi = widget.initialHindi;
    _tts.setCompletionHandler(_completeChunk);
    _tts.setCancelHandler(_completeChunk);
    _tts.setErrorHandler((_) {
      _speechError = true;
      _completeChunk();
    });
    unawaited(_loadVoices());
  }

  void _completeChunk() {
    final done = _chunkDone;
    if (done != null && !done.isCompleted) done.complete();
  }

  Future<void> _loadVoices() async {
    try {
      var raw = await _tts.getVoices;
      if (kIsWeb && (raw is! List || raw.isEmpty)) {
        await Future<void>.delayed(const Duration(milliseconds: 700));
        raw = await _tts.getVoices;
      }
      if (!mounted || raw is! List) return;
      final voices = <Map<String, String>>[];
      for (final item in raw) {
        if (item is! Map) continue;
        final name = item['name']?.toString() ?? '';
        final locale = item['locale']?.toString() ?? '';
        if (name.isNotEmpty &&
            locale.isNotEmpty &&
            !voices.any((voice) =>
                voice['name'] == name && voice['locale'] == locale)) {
          voices.add({'name': name, 'locale': locale});
        }
      }
      setState(() {
        _voices
          ..clear()
          ..addAll(voices);
      });
    } catch (_) {
      // Voice listing can be unavailable while the browser initializes TTS.
    }
  }

  Future<void> _stop() async {
    _runId++;
    _completeChunk();
    if (mounted) setState(() => _speaking = false);
    try {
      await _tts.stop();
    } catch (_) {}
  }

  Future<void> _changeLanguage() async {
    await _stop();
    if (!mounted) return;
    setState(() {
      _isHindi = !_isHindi;
      _chosenVoice = null;
    });
    unawaited(_loadVoices());
  }

  void _showMessage(String message) {
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(message)),
    );
  }

  Future<void> _start(String text) async {
    if (_speaking) return;
    final chunks = splitSpeechChunks(text, maxLength: 140);
    if (chunks.isEmpty) return;
    final run = ++_runId;
    setState(() => _speaking = true);
    _speechError = false;
    try {
      // Voice discovery already runs on page open; don't block the first tap.
      if (run != _runId) return;
      final voices = _matchingVoices;
      if (kIsWeb && _isHindi && voices.isEmpty) {
        _showMessage(
            'Hindi voice is not available in this browser. Install a Hindi TTS voice on this device.');
        return;
      }
      final selected =
          voices.where((voice) => _voiceKey(voice) == _chosenVoice);
      final voice = selected.isNotEmpty
          ? selected.first
          : voices.isNotEmpty
              ? voices.first
              : null;
      if (kIsWeb && !_isHindi && voice == null) {
        _showMessage('English voice is not available in this browser.');
        return;
      }
      await _tts
          .setLanguage(voice?['locale'] ?? (_isHindi ? 'hi-IN' : 'en-IN'));
      // Let the device use its default hi-IN/en-IN voice unless the user chose one.
      if (voice != null && _chosenVoice != null) await _tts.setVoice(voice);
      // Browser rate 0.5 was unnaturally slow; native engines use another scale.
      await _tts.setSpeechRate(kIsWeb ? 0.95 : 0.5);
      for (final chunk in chunks) {
        if (run != _runId) break;
        _chunkDone = Completer<void>();
        await _tts.speak(chunk);
        await _chunkDone!.future.timeout(const Duration(seconds: 40));
        if (_speechError) {
          _showMessage('Speech stopped on this device. Try another voice.');
          break;
        }
        await Future<void>.delayed(const Duration(milliseconds: 100));
      }
    } on TimeoutException {
      _showMessage('Speech paused unexpectedly. Please try again.');
      await _tts.stop();
    } catch (_) {
      _showMessage('Speech could not start on this device.');
    } finally {
      if (run == _runId) {
        _chunkDone = null;
        if (mounted) setState(() => _speaking = false);
      }
    }
  }

  @override
  void dispose() {
    _runId++;
    _completeChunk();
    unawaited(_tts.stop());
    super.dispose();
  }

  @override
  Widget build(BuildContext context) => Scaffold(
        backgroundColor: AppTheme.primaryColor,
        appBar: AppBar(
          backgroundColor: AppTheme.primaryColor,
          foregroundColor: Colors.white,
          title: Text(_isHindi ? widget.titleHindi : widget.titleEnglish),
          actions: [
            TextButton(
              onPressed: _changeLanguage,
              child: Text(_isHindi ? 'English' : 'हिंदी',
                  style: const TextStyle(color: Colors.white)),
            ),
          ],
        ),
        body: SafeArea(
          child: Center(
            child: ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 760),
              child: SingleChildScrollView(
                padding: const EdgeInsets.all(16),
                child: Container(
                  width: double.infinity,
                  padding: const EdgeInsets.all(20),
                  decoration: BoxDecoration(
                    color: AppTheme.surfaceColor,
                    borderRadius: BorderRadius.circular(16),
                  ),
                  child: FutureBuilder<String>(
                    future: _isHindi ? widget.storyHindi : widget.storyEnglish,
                    builder: (context, snapshot) {
                      if (snapshot.hasError) {
                        return const Text('The story could not be opened.');
                      }
                      if (!snapshot.hasData) {
                        return const Center(child: CircularProgressIndicator());
                      }
                      final voices = _matchingVoices;
                      final selected = voices
                              .any((voice) => _voiceKey(voice) == _chosenVoice)
                          ? _chosenVoice
                          : voices.isEmpty
                              ? null
                              : _voiceKey(voices.first);
                      return Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          FilledButton.icon(
                            onPressed: () =>
                                _speaking ? _stop() : _start(snapshot.data!),
                            icon:
                                Icon(_speaking ? Icons.stop : Icons.volume_up),
                            label: Text(_speaking
                                ? (_isHindi ? 'रोकें' : 'Stop')
                                : (_isHindi ? 'सुनें' : 'Listen')),
                          ),
                          const SizedBox(height: 12),
                          DropdownButtonFormField<String>(
                            initialValue: _isHindi ? 'hi' : 'en',
                            isExpanded: true,
                            decoration: const InputDecoration(
                              labelText: 'Story language',
                              border: OutlineInputBorder(),
                            ),
                            items: [
                              for (final entry in _storyLanguages.entries)
                                DropdownMenuItem(
                                  value: entry.key,
                                  child: Text(entry.key == 'en' ||
                                          entry.key == 'hi'
                                      ? '${entry.value} · available offline'
                                      : '${entry.value} · online, coming soon'),
                                ),
                            ],
                            selectedItemBuilder: (context) => [
                              for (final entry in _storyLanguages.entries)
                                Text(entry.value,
                                    overflow: TextOverflow.ellipsis),
                            ],
                            onChanged: (language) {
                              if (language == null) return;
                              if (language == 'en' || language == 'hi') {
                                if ((language == 'hi') != _isHindi) {
                                  _changeLanguage();
                                }
                              } else {
                                _showMessage(
                                    '${_storyLanguages[language]} translation will be available after Bhashini is connected.');
                              }
                            },
                          ),
                          if (voices.isNotEmpty) ...[
                            const SizedBox(height: 8),
                            DropdownButton<String>(
                              value: selected,
                              isExpanded: true,
                              items: [
                                for (final voice in voices)
                                  DropdownMenuItem(
                                    value: _voiceKey(voice),
                                    child: Text(
                                        '${voice['name']} (${voice['locale']})',
                                        overflow: TextOverflow.ellipsis),
                                  ),
                              ],
                              onChanged: (value) async {
                                await _stop();
                                if (mounted) {
                                  setState(() => _chosenVoice = value);
                                }
                              },
                            ),
                          ],
                          const SizedBox(height: 16),
                          SelectableText(snapshot.data!,
                              style:
                                  const TextStyle(fontSize: 16, height: 1.65)),
                        ],
                      );
                    },
                  ),
                ),
              ),
            ),
          ),
        ),
      );
}
