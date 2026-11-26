import 'dart:convert';
import 'dart:typed_data';

import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';

import '../../app/app_session.dart';
import '../../data/report_queue.dart';
import '../../data/guide_catalog.dart';
import '../../data/guide_hindi.dart';

class ReportIssueScreen extends StatefulWidget {
  const ReportIssueScreen(
      {super.key, required this.placeId, this.isHindi = false});
  final String placeId;
  final bool isHindi;

  @override
  State<ReportIssueScreen> createState() => _ReportIssueScreenState();
}

class _ReportIssueScreenState extends State<ReportIssueScreen> {
  String _t(String en, String hi) => widget.isHindi ? hi : en;
  String _categoryLabel(String category) => switch (category) {
        'litter' => _t('Litter / cleanliness', 'कचरा / सफ़ाई'),
        'damage' => _t('Damage', 'नुकसान'),
        'access' => _t('Access / safety', 'पहुँच / सुरक्षा'),
        'information' => _t('Incorrect information', 'गलत जानकारी'),
        _ => _t('Other', 'अन्य'),
      };
  final _description = TextEditingController();
  final _location = TextEditingController();
  String _category = 'litter';
  List<PendingReport> _pending = [];
  bool _busy = false;
  String? _message;
  String? _photoBase64;
  Map<String, double>? _coordinates;

  Future<void> _pickPhoto(ImageSource source) async {
    try {
      final image = await ImagePicker().pickImage(
          source: source, maxWidth: 1000, maxHeight: 1000, imageQuality: 55);
      if (image == null) return;
      final bytes = await image.readAsBytes();
      if (bytes.length > 1048576 ||
          bytes.length < 4 ||
          bytes.first != 0xff ||
          bytes[1] != 0xd8 ||
          bytes[bytes.length - 2] != 0xff ||
          bytes.last != 0xd9) {
        setState(() => _message = _t('JPEG photo must be under 1 MB.',
            'जेपीईजी तस्वीर 1 एमबी से छोटी होनी चाहिए।'));
        return;
      }
      setState(() {
        _photoBase64 = base64Encode(bytes);
        _message = null;
      });
    } catch (_) {
      setState(() =>
          _message = _t('Photo could not be opened.', 'तस्वीर नहीं खुल सकी।'));
    }
  }

  Future<void> _getLocation() async {
    setState(() => _message =
        _t('Getting GPS location...', 'जीपीएस स्थान लिया जा रहा है...'));
    try {
      final coordinates = await ReportQueue.currentLocation();
      if (mounted) {
        setState(() {
          _coordinates = coordinates;
          _message = null;
        });
      }
    } catch (_) {
      if (mounted) {
        setState(() => _message = _t(
            'Location unavailable. Check phone location and permission.',
            'स्थान नहीं मिला। फोन की लोकेशन और अनुमति जाँचें।'));
      }
    }
  }

  @override
  void initState() {
    super.initState();
    _refresh();
    _getLocation();
  }

  @override
  void dispose() {
    _description.dispose();
    _location.dispose();
    super.dispose();
  }

  Future<void> _refresh() async {
    try {
      final items = await ReportQueue.read();
      if (mounted) {
        setState(() => _pending = items
            .where((item) =>
                item.ownerEmail == AppSession.instance.email &&
                item.placeId == widget.placeId)
            .toList());
      }
    } catch (_) {
      if (mounted) {
        setState(() => _message = _t(
            'Offline drafts are unavailable on this device.',
            'इस डिवाइस पर ऑफलाइन ड्राफ्ट उपलब्ध नहीं हैं।'));
      }
    }
  }

  Future<void> _save() async {
    final text = _description.text.trim();
    if (text.length > 2000 || (text.isEmpty && _photoBase64 == null)) {
      setState(() => _message =
          _t('Add a photo or description.', 'तस्वीर या विवरण जोड़ें।'));
      return;
    }
    if (_location.text.trim().length > 200) {
      setState(() => _message = _t('Keep the location under 200 characters.',
          'स्थान का विवरण 200 अक्षरों से छोटा रखें।'));
      return;
    }
    final email = AppSession.instance.email;
    if (email == null) return;
    setState(() {
      _busy = true;
      _message = null;
    });
    try {
      if (_coordinates == null) {
        try {
          _coordinates = await ReportQueue.currentLocation();
        } catch (_) {/* Save without a fix rather than lose the report. */}
      }
      final hadGps = _coordinates != null;
      final clientId = ReportQueue.newClientId();
      await ReportQueue.add(PendingReport(
        clientId: clientId,
        ownerEmail: email,
        placeId: widget.placeId,
        category: _category,
        description: text,
        locationLabel: _location.text.trim(),
        latitude: _coordinates?['latitude'],
        longitude: _coordinates?['longitude'],
        accuracyM: _coordinates?['accuracyM'],
        photoBase64: _photoBase64,
        createdAt: DateTime.now().toUtc().toIso8601String(),
      ));
      _photoBase64 = null;
      _coordinates = null;
      _description.clear();
      _location.clear();
      await _refresh();
      var sent = false;
      if (AppSession.instance.token != null) {
        try {
          await ReportQueue.syncCurrentUser();
          sent = !(await ReportQueue.read())
              .any((item) => item.clientId == clientId);
          await _refresh();
        } catch (_) {/* Draft stays on this phone. */}
      }
      if (mounted) {
        setState(() => _message = sent
            ? _t('Report submitted.', 'रिपोर्ट भेज दी गई।')
            : _t(
                'Report saved on this phone. It will sync when online${hadGps ? '' : ' (GPS unavailable)'}.',
                'रिपोर्ट फोन पर सहेजी गई है। ऑनलाइन होने पर भेजी जाएगी${hadGps ? '' : ' (GPS उपलब्ध नहीं था)'}।'));
      }
    } catch (_) {
      if (mounted) {
        setState(() => _message = _t('Draft could not be saved. Try again.',
            'ड्राफ्ट सहेजा नहीं जा सका। फिर कोशिश करें।'));
      }
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  Future<void> _deleteDraft(PendingReport report) async {
    setState(() => _busy = true);
    try {
      await ReportQueue.remove(report.clientId);
      await _refresh();
      if (mounted) {
        setState(
            () => _message = _t('Draft deleted.', 'ड्राफ्ट हटा दिया गया।'));
      }
    } catch (_) {
      if (mounted) {
        setState(() => _message =
            _t('Draft could not be deleted.', 'ड्राफ्ट हटाया नहीं जा सका।'));
      }
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  @override
  Widget build(BuildContext context) => Scaffold(
        appBar: AppBar(
            title:
                Text(_t('Report a heritage issue', 'धरोहर की समस्या बताएँ'))),
        body: SafeArea(
            child: Center(
                child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 600),
          child: ListView(padding: const EdgeInsets.all(20), children: [
            FutureBuilder<GuideCatalog>(
                future: GuideCatalog.load(),
                builder: (context, snapshot) {
                  final name = snapshot.data?.byId[widget.placeId]?.name ??
                      widget.placeId;
                  return Text(
                      _t('Place: $name', 'जगह: ${guideNameHindi(name)}'),
                      style: Theme.of(context).textTheme.titleLarge);
                }),
            const SizedBox(height: 8),
            Text(_t(
                'Add a photo or description. GPS coordinates are saved with your permission. Reports need review before forwarding to an authority.',
                'तस्वीर या विवरण जोड़ें। आपकी अनुमति से जीपीएस स्थान सहेजा जाएगा। किसी विभाग को भेजने से पहले रिपोर्ट की जाँच होगी।')),
            const SizedBox(height: 18),
            DropdownButtonFormField<String>(
              initialValue: _category,
              decoration: InputDecoration(
                  labelText: _t('Issue type', 'समस्या का प्रकार'),
                  border: const OutlineInputBorder()),
              items: ['litter', 'damage', 'access', 'information', 'other']
                  .map((category) => DropdownMenuItem(
                      value: category, child: Text(_categoryLabel(category))))
                  .toList(),
              onChanged: _busy
                  ? null
                  : (value) {
                      if (value != null) setState(() => _category = value);
                    },
            ),
            const SizedBox(height: 14),
            Wrap(spacing: 8, children: [
              OutlinedButton.icon(
                  onPressed:
                      _busy ? null : () => _pickPhoto(ImageSource.camera),
                  icon: const Icon(Icons.camera_alt_outlined),
                  label: Text(_t('Take photo', 'तस्वीर लें'))),
              OutlinedButton.icon(
                  onPressed:
                      _busy ? null : () => _pickPhoto(ImageSource.gallery),
                  icon: const Icon(Icons.photo_library_outlined),
                  label: Text(_t('Choose photo', 'तस्वीर चुनें'))),
            ]),
            if (_photoBase64 != null) ...[
              ClipRRect(
                  borderRadius: BorderRadius.circular(12),
                  child: Image.memory(
                      Uint8List.fromList(base64Decode(_photoBase64!)),
                      height: 180,
                      width: double.infinity,
                      fit: BoxFit.cover)),
              Align(
                  alignment: Alignment.centerRight,
                  child: TextButton.icon(
                      onPressed: _busy
                          ? null
                          : () => setState(() => _photoBase64 = null),
                      icon: const Icon(Icons.delete_outline),
                      label: Text(_t('Remove photo', 'तस्वीर हटाएँ')))),
            ],
            const SizedBox(height: 12),
            TextField(
                controller: _description,
                maxLines: 5,
                maxLength: 2000,
                decoration: InputDecoration(
                    labelText: _t('What did you notice? (optional)',
                        'आपने क्या देखा? (वैकल्पिक)'),
                    border: const OutlineInputBorder())),
            const SizedBox(height: 8),
            TextField(
                controller: _location,
                maxLength: 200,
                decoration: InputDecoration(
                    labelText: _t('Where at this place? (optional)',
                        'इस जगह पर कहाँ? (वैकल्पिक)'),
                    border: const OutlineInputBorder())),
            Text(_t(
                'GPS is captured automatically when you open or submit a report.',
                'रिपोर्ट खोलने या भेजने पर जीपीएस स्थान अपने आप लिया जाता है।')),
            if (_coordinates != null)
              ListTile(
                contentPadding: EdgeInsets.zero,
                leading: const Icon(Icons.gps_fixed, color: Colors.green),
                title: Text(
                    _t('Precise location attached', 'सटीक स्थान जोड़ा गया')),
                subtitle: Text(
                    '${_coordinates!['latitude']!.toStringAsFixed(5)}, ${_coordinates!['longitude']!.toStringAsFixed(5)} (±${_coordinates!['accuracyM']!.toStringAsFixed(0)} m)'),
              ),
            const SizedBox(height: 8),
            FilledButton.icon(
                onPressed: _busy ? null : _save,
                icon: const Icon(Icons.send_outlined),
                label: Text(_t('Submit report', 'रिपोर्ट भेजें'))),
            if (_message != null)
              Padding(
                  padding: const EdgeInsets.only(top: 14),
                  child: Text(_message!)),
            const SizedBox(height: 24),
            Text(
                _t('Saved on this phone (${_pending.length})',
                    'इस फोन पर सहेजी रिपोर्ट (${_pending.length})'),
                style: Theme.of(context).textTheme.titleMedium),
            for (final item in _pending)
              Card(
                  child: ListTile(
                leading: Icon(item.photoBase64 == null
                    ? Icons.pending_outlined
                    : Icons.photo_camera_back_outlined),
                title: Text(_categoryLabel(item.category)),
                subtitle: Text([
                  if (item.description.isNotEmpty) item.description,
                  if (item.photoBase64 != null)
                    _t('Photo attached', 'तस्वीर जोड़ी गई'),
                  if (item.latitude != null)
                    _t('GPS attached', 'जीपीएस जोड़ा गया'),
                ].join(' · ')),
                trailing: IconButton(
                    tooltip: _t('Delete draft', 'ड्राफ्ट हटाएँ'),
                    onPressed: _busy ? null : () => _deleteDraft(item),
                    icon: const Icon(Icons.delete_outline)),
              )),
            if (AppSession.instance.isDemo)
              Padding(
                  padding: const EdgeInsets.only(top: 12),
                  child: Text(_t(
                      'Demo login saves drafts only. Sending needs a real account.',
                      'डेमो लॉगिन में केवल ड्राफ्ट सहेजता है। भेजने के लिए वास्तविक खाता चाहिए।'))),
          ]),
        ))),
      );
}
