# Monument recognition preparation

The current app scan screen still does not identify monuments. Two experimental
20-class models have now been trained in Google Colab, but neither is integrated
into the app. The ImageNet-pretrained MobileNetV2 candidate scored 78.5% on the
original 470-photo test. A focused fine-tune with 21 new training photos also
scored 78.5%; a separate 11-photo online holdout scored 8/11 for both. These
numbers do not establish real phone-camera accuracy. See
`transfer_experiment_report_2026-10-15.md` and
`focus_review_report_2026-10-15.md` for the evidence and limitations.

`independent_online_test_colab.py` prepares a new Commons candidate review in
the existing Colab session. It excludes previously reviewed Commons titles and
near matches to the original prepared dataset. Its contact sheets still require
human monument-identity review before scoring either model. It has not been run
as of 16 October because the notebook is showing a loading error. The user
chose Colab-only evaluation; do not download the model or test photos locally.

## Photo selection

Keep the downloaded `raw` folder as an untouched backup. Review a separate copy. For the first recognition experiment, choose only clear photos of each **main monument** and place them under `05_AI_Dataset/Monument_Recognition/<monument_id>/`. Different angles, distances, lighting, seasons and phones are more useful than many nearly identical front views. Around 300 *good and varied* images per main class is a target, not a requirement or a guarantee of accuracy. A class with fewer good photos is better than one filled with irrelevant images.

Nearby-place photos stay in their own content/gallery folders. They are **not** automatically extra monument classes. A target of 100 images for each nearby place is optional; a small, varied gallery is usually enough for display. The Taj Mahal gallery plan remains around 40 curated display photos total. Training and display selections must be recorded separately; the same original may be selected for both, but the exported folders remain separate.

Reject photos of a different place, collages, maps, watermarks over the subject, very blurred or tiny images, near duplicates, and images where the monument is barely visible. Keep a review log with source and license before publishing gallery images. Do not delete originals until the private copy and selection have been verified.

## Workflow

1. Put reviewed main-monument photos in the class folders. Do not put `Nearby_Heritage` or gallery-only folders inside the training classes.
2. Run `prepare_dataset.py` without flags to audit counts, unreadable files, small files and exact duplicates. This is read-only.
3. After at least two classes have at least 20 usable images each, run `prepare_dataset.py --write`. It makes separate train/validation/test JPEG folders, a manifest, labels and an audit report. The source photos are untouched. Exact duplicates across classes block preparation. It refuses to overwrite an existing prepared output.
4. `train_monument.py` remains the small local CNN baseline path. The newer MobileNetV2 experiment was run in Colab using official pretrained weights, with the user's approval. Its candidate `.keras` and `.tflite` files are in the private Drive folder linked in the transfer experiment report.
5. Test the model on new phone photos that were never in any training split. Connect to the Flutter app only if results are acceptable, with an “unknown/not sure” path for low confidence.

The split uses a fixed random seed and about 70% train, 15% validation, 15% test per class. Exact duplicates are removed before splitting. Similar but non-identical photos, or multiple crops of one source, still need manual grouping so they do not leak across splits. Do not report the test result as real-world accuracy until this is checked.

The local scripts use Python and Pillow for photo preparation; local training
needs TensorFlow, which has not been set up in this workspace. The Colab
experiment downloaded official MobileNetV2 weights to Colab only. Keep
experimental model files out of the app until independent testing and model
selection are complete.
