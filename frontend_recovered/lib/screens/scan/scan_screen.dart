import 'dart:typed_data';

import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:image_picker/image_picker.dart';

import '../../app/theme.dart';
import '../../app/routes.dart';
import '../../data/guide_catalog.dart';
import '../../data/monument_classifier.dart';
import '../../data/monument_guess.dart';

/// Offline photo scan for the 20 main monument groups.
class ScanScreen extends StatefulWidget {
  const ScanScreen(
      {super.key, this.imagePicker, this.classifier, this.autoOpenCamera});

  final ImagePicker? imagePicker;
  final Future<MonumentGuess?> Function(Uint8List)? classifier;

  /// Opens the phone camera on entry. Injectable picker tests may opt in.
  final bool? autoOpenCamera;

  @override
  State<ScanScreen> createState() => _ScanScreenState();
}

/// Two local UI states of the scan flow:
/// - [capturing] — camera/gallery choices.
/// - [captured] — photo review while identification is being developed.
enum _ScanStage { capturing, captured }

class _ScanScreenState extends State<ScanScreen> {
  // Legacy display threshold for accepted classifier results. The classifier
  // separately rejects unsupported/ambiguous photos; this is not a calibrated
  // probability or evidence of independent phone-photo accuracy.
  static const double _suggestionThreshold = 0.55;
  _ScanStage _stage = _ScanStage.capturing;

  late final ImagePicker _picker;
  Uint8List? _selectedBytes;
  MonumentGuess? _guess;
  String? _matchedName;
  String? _analysisError;
  bool _analyzing = false;
  bool _picking = false;

  bool get _canSuggest =>
      !_analyzing &&
      _analysisError == null &&
      _guess != null &&
      _guess!.confidence.isFinite &&
      _guess!.confidence >= _suggestionThreshold &&
      _guess!.confidence <= 1.0 &&
      _matchedName != null;

  @override
  void initState() {
    super.initState();
    _picker = widget.imagePicker ?? ImagePicker();
    if (widget.autoOpenCamera ?? widget.imagePicker == null) {
      WidgetsBinding.instance.addPostFrameCallback((_) {
        if (mounted && _stage == _ScanStage.capturing) _capture();
      });
    }
  }

  Future<void> _capture() async {
    if (_picking) return;
    setState(() => _picking = true);
    try {
      final image = await _picker.pickImage(
        source: ImageSource.camera,
        preferredCameraDevice: CameraDevice.rear,
        maxWidth: 1024,
        maxHeight: 1024,
        imageQuality: 82,
      );
      if (image != null) await _previewImage(image);
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Failed to capture photo: $e')),
      );
    } finally {
      if (mounted) setState(() => _picking = false);
    }
  }

  Future<void> _chooseFromGallery() async {
    if (_picking) return;
    setState(() => _picking = true);
    try {
      final image = await _picker.pickImage(
        source: ImageSource.gallery,
        maxWidth: 1024,
        maxHeight: 1024,
        imageQuality: 82,
      );
      if (image != null) await _previewImage(image);
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Failed to pick image: $e')),
      );
    } finally {
      if (mounted) setState(() => _picking = false);
    }
  }

  Future<void> _previewImage(XFile image) async {
    final bytes = await image.readAsBytes();
    if (!mounted) return;
    setState(() {
      _selectedBytes = bytes;
      _stage = _ScanStage.captured;
      _guess = null;
      _matchedName = null;
      _analysisError = null;
      _analyzing = true;
    });
    try {
      final guess = await (widget.classifier ?? classifyMonument)(bytes);
      final catalog = guess == null ? null : await GuideCatalog.load();
      if (!mounted || _selectedBytes != bytes) return;
      setState(() {
        _guess = guess;
        _matchedName =
            guess == null ? null : catalog?.byId[guess.placeId]?.name;
        _analyzing = false;
      });
    } catch (_) {
      if (!mounted || _selectedBytes != bytes) return;
      setState(() {
        _analysisError = 'Could not analyse this photo on this device.';
        _analyzing = false;
      });
    }
  }

  void _retake() {
    setState(() {
      _selectedBytes = null;
      _stage = _ScanStage.capturing;
      _guess = null;
      _matchedName = null;
      _analysisError = null;
      _analyzing = false;
    });
  }

  void _openGuide() => context.push('/guides');

  void _goBack() {
    if (context.canPop()) {
      context.pop();
    } else {
      context.go(AppRoutes.home);
    }
  }

  @override
  Widget build(BuildContext context) {
    final capturing = _stage == _ScanStage.capturing;

    return Scaffold(
      backgroundColor:
          capturing ? AppTheme.primaryColor : AppTheme.backgroundColor,
      body: SafeArea(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            _buildHeader(context, capturing),
            Expanded(
              child: Padding(
                padding: const EdgeInsets.symmetric(horizontal: 16),
                child: capturing
                    ? _buildViewfinder(context)
                    : _buildCapturedPreview(context),
              ),
            ),
            if (capturing)
              _buildCaptureControls()
            else
              _buildCapturedActions(context),
          ],
        ),
      ),
    );
  }

  // ---------------------------------------------------------------------------
  // Header
  // ---------------------------------------------------------------------------
  Widget _buildHeader(BuildContext context, bool capturing) {
    final theme = Theme.of(context);
    final Color primaryColor =
        capturing ? Colors.white : AppTheme.primaryTextColor;
    final Color secondaryColor =
        capturing ? Colors.white.withAlpha(0xCC) : AppTheme.secondaryTextColor;

    return Padding(
      padding: const EdgeInsets.fromLTRB(8, 8, 16, 16),
      child: Row(
        children: [
          IconButton(
            onPressed: _goBack,
            tooltip: 'Back',
            icon: Icon(Icons.arrow_back_rounded, color: primaryColor),
          ),
          const SizedBox(width: 4),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisSize: MainAxisSize.min,
              children: [
                Text(
                  'Add a monument photo',
                  style: theme.textTheme.titleLarge?.copyWith(
                    fontWeight: FontWeight.bold,
                    color: primaryColor,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  _stage == _ScanStage.capturing
                      ? 'Recognizes 20 supported monuments. Other places may not be recognized.'
                      : 'Review the photo you selected.',
                  style: theme.textTheme.bodySmall?.copyWith(
                    color: secondaryColor,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  // ---------------------------------------------------------------------------
  // Camera state
  // ---------------------------------------------------------------------------
  Widget _buildViewfinder(BuildContext context) {
    return ClipRRect(
      borderRadius: BorderRadius.circular(20),
      child: Container(
        width: double.infinity,
        color: AppTheme.surfaceColor,
        padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 20),
        child: Center(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Container(
                width: 88,
                height: 88,
                decoration: const BoxDecoration(
                  color: AppTheme.backgroundColor,
                  shape: BoxShape.circle,
                ),
                child: const Icon(Icons.camera_alt_outlined,
                    size: 44, color: AppTheme.primaryColor),
              ),
              const SizedBox(height: 20),
              Text('Ready to scan a monument',
                  textAlign: TextAlign.center,
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                      color: AppTheme.primaryTextColor,
                      fontWeight: FontWeight.bold)),
              const SizedBox(height: 10),
              Text(
                'The camera opens separately. If you closed it, tap Open camera below or choose a photo from your gallery.',
                textAlign: TextAlign.center,
                style: Theme.of(context)
                    .textTheme
                    .bodyMedium
                    ?.copyWith(color: AppTheme.secondaryTextColor),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildCaptureControls() {
    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 16, 16, 24),
      child: Column(
        children: [
          SizedBox(
            width: double.infinity,
            child: FilledButton.icon(
              onPressed: _picking ? null : _capture,
              icon: const Icon(Icons.camera_alt_outlined),
              label: Text(_picking ? 'Opening camera...' : 'Open camera'),
              style: FilledButton.styleFrom(
                backgroundColor: Colors.white,
                foregroundColor: AppTheme.primaryColor,
                minimumSize: const Size.fromHeight(56),
              ),
            ),
          ),
          const SizedBox(height: 8),
          TextButton.icon(
            onPressed: _picking ? null : _chooseFromGallery,
            icon: const Icon(Icons.photo_library_outlined, size: 20),
            label: const Text('Choose from gallery'),
            style: TextButton.styleFrom(foregroundColor: Colors.white),
          ),
        ],
      ),
    );
  }

  // ---------------------------------------------------------------------------
  // Captured state
  // ---------------------------------------------------------------------------
  Widget _buildCapturedPreview(BuildContext context) {
    final theme = Theme.of(context);
    return ClipRRect(
      borderRadius: BorderRadius.circular(20),
      child: Stack(
        fit: StackFit.expand,
        children: [
          _buildLocalImage(),
          const DecoratedBox(
            decoration: BoxDecoration(
              gradient: LinearGradient(
                begin: Alignment.topCenter,
                end: Alignment.bottomCenter,
                colors: [
                  Colors.black38,
                  Colors.transparent,
                  Colors.transparent,
                  Colors.black45,
                ],
                stops: [0.0, 0.25, 0.72, 1.0],
              ),
            ),
          ),
          const Positioned(
            top: 16,
            left: 0,
            right: 0,
            child: _CapturedConfirmation(),
          ),
          Positioned(
            left: 16,
            right: 16,
            bottom: 16,
            child: Text(
              'Photo preview',
              textAlign: TextAlign.center,
              style: theme.textTheme.bodyMedium?.copyWith(
                color: Colors.white,
                fontWeight: FontWeight.w600,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildLocalImage() {
    if (_selectedBytes == null) {
      return Container(
        color: AppTheme.primaryColor,
        alignment: Alignment.center,
        child:
            const Icon(Icons.image_outlined, size: 40, color: Colors.white38),
      );
    }

    return Image.memory(
      _selectedBytes!,
      fit: BoxFit.cover,
      errorBuilder: (context, error, stack) => Container(
        color: AppTheme.primaryColor,
        alignment: Alignment.center,
        child: const Icon(Icons.broken_image_outlined,
            size: 40, color: Colors.white38),
      ),
    );
  }

  Widget _buildCapturedActions(BuildContext context) {
    final theme = Theme.of(context);
    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 16, 16, 24),
      child: Column(
        children: [
          Text(
            _analyzing ? 'Checking photo offline...' : 'Photo ready',
            style: theme.textTheme.titleMedium?.copyWith(
              color: AppTheme.primaryTextColor,
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: 8),
          if (_analyzing)
            const Padding(
              padding: EdgeInsets.symmetric(vertical: 8),
              child: CircularProgressIndicator(),
            ),
          Text(
            _analysisError ??
                (_canSuggest
                    ? 'Possible match: $_matchedName. Please confirm before opening the guide.'
                    : _analyzing
                        ? 'The model checks 20 main monuments on this phone.'
                        : 'Monument could not be confidently recognized. Try a clearer photo of a supported monument or choose manually.'),
            textAlign: TextAlign.center,
            style: theme.textTheme.bodySmall?.copyWith(
              color: AppTheme.secondaryTextColor,
            ),
          ),
          const SizedBox(height: 12),
          if (_canSuggest) ...[
            SizedBox(
              width: double.infinity,
              child: FilledButton(
                onPressed: () => context.push(guidePathFor(_guess!.placeId)),
                child: Text('Yes, open $_matchedName'),
              ),
            ),
            const SizedBox(height: 8),
          ],
          SizedBox(
            width: double.infinity,
            child: TextButton(
              onPressed: _openGuide,
              child: const Text('Choose monument manually'),
            ),
          ),
          const SizedBox(height: 4),
          SizedBox(
            width: double.infinity,
            child: OutlinedButton.icon(
              onPressed: _retake,
              icon: const Icon(Icons.refresh_rounded, size: 20),
              label: const Text('Choose again'),
              style: OutlinedButton.styleFrom(
                foregroundColor: AppTheme.primaryColor,
                side: const BorderSide(
                  color: AppTheme.primaryColor,
                  width: 1.5,
                ),
                padding: const EdgeInsets.symmetric(
                  horizontal: 16,
                  vertical: 14,
                ),
                minimumSize: const Size(0, 48),
                shape: const RoundedRectangleBorder(
                  borderRadius: BorderRadius.all(Radius.circular(14)),
                ),
              ),
            ),
          ),
          TextButton(
            onPressed: _goBack,
            child: const Text('Back'),
          ),
        ],
      ),
    );
  }
}

// ---------------------------------------------------------------------------
// Screen-local widgets
// ---------------------------------------------------------------------------

/// Confirmation pill shown over the captured photo.
class _CapturedConfirmation extends StatelessWidget {
  const _CapturedConfirmation();

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
        decoration: BoxDecoration(
          // VirasatAI success color (see `cline.md`).
          color: const Color(0xFF2F855A),
          borderRadius: BorderRadius.circular(14),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(
              Icons.check_circle_rounded,
              size: 16,
              color: Colors.white,
            ),
            const SizedBox(width: 6),
            Text(
              'Photo selected',
              style: Theme.of(context).textTheme.labelMedium?.copyWith(
                    color: Colors.white,
                    fontWeight: FontWeight.w600,
                  ),
            ),
          ],
        ),
      ),
    );
  }
}
