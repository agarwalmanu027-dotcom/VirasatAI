# Monument recognition split audit (21 October 2026)

Source: private Drive `manifest.csv` (`1hd0mq6BPeJ1N0J_f7F_HOXsUnwmxHeVZ`), 3,141 rows. Metadata audit plus visual review of all 79 same-class pairs with dHash distance <=8: 37 crossed old splits and 42 were already within one split. More distant similarities and source provenance still need review.

## Counts

| Class | Train | Validation | Test |
| --- | ---: | ---: | ---: |
| ajanta_ellora_caves | 126 | 27 | 27 |
| amer_fort | 124 | 26 | 26 |
| badami_cave_temples | 40 | 8 | 8 |
| charminar | 126 | 27 | 27 |
| city_palace_udaipur | 126 | 27 | 27 |
| gateway_of_india | 123 | 26 | 26 |
| golden_temple | 126 | 27 | 27 |
| hampi_monuments | 126 | 27 | 27 |
| jaisalmer_fort | 100 | 21 | 21 |
| khajuraho_monuments | 126 | 27 | 27 |
| konark_sun_temple | 126 | 27 | 27 |
| mahabalipuram | 126 | 27 | 27 |
| meenakshi_temple | 122 | 26 | 26 |
| mehrangarh_fort | 126 | 27 | 27 |
| mysore_palace | 68 | 15 | 15 |
| qutub_minar | 126 | 27 | 27 |
| red_fort | 102 | 22 | 22 |
| sanchi_stupa | 47 | 10 | 10 |
| taj_mahal | 126 | 27 | 27 |
| victoria_memorial | 89 | 19 | 19 |

No SHA-256 duplicates occur anywhere in the manifest. However, same-class pairs across different splits have 11 dHash distances <=4 and 37 distances <=8. These are review candidates, not confirmed duplicates. The <=4 pairs are:

| Class | Split A / file | Split B / file | dHash distance |
| --- | --- | --- | ---: |
| charminar | test / charminar_174.jpg | train / charminar_256.jpg | 4 |
| charminar | test / charminar_158.jpg | train / charminar_157.jpg | 3 |
| charminar | test / charminar_196.jpg | train / charminar_190.jpg | 3 |
| charminar | test / charminar_045.jpg | train / charminar_044.jpg | 3 |
| charminar | test / charminar_023.jpg | train / charminar_024.jpg | 3 |
| charminar | val / charminar_260.jpg | train / charminar_257.jpg | 3 |
| jaisalmer_fort | test / jaisalmer_fort_131.jpg | train / jaisalmer_fort_132.jpg | 3 |
| meenakshi_temple | val / meenakshi_temple_007.jpg | train / aug_meenakshi_temple_271.jpg | 3 |
| mehrangarh_fort | val / mehrangarh_fort_025.jpg | train / mehrangarh_fort_228.jpg | 4 |
| mysore_palace | test / aug_mysore_palace_231.jpg | train / mysore_palace_029.jpg | 3 |
| mysore_palace | test / aug_mysore_palace_292.jpg | train / mysore_palace_090.jpg | 4 |

One cross-class pair has dHash distance <=3: `badami_cave_temples/badami_commons_cave_1_d436fcd545f9.jpg` and `mahabalipuram/mahabalipuram_075.jpg`. Visual inspection showed different scenes; this is a dHash false positive, not evidence of a label error.

## Visually confirmed cross-split overlap

- `charminar_158.jpg` (test) and `charminar_157.jpg` (train) are the same photograph; the train version is black and white. The same bird positions, foreground vehicles, banner, and perspective confirm this.
- `aug_mysore_palace_231.jpg` (test) and `mysore_palace_029.jpg` (train) are the same photograph with a changed crop/size. Identical facade details and sky confirm this.
- `charminar_174.jpg` / `charminar_256.jpg`, `charminar_196.jpg` / `charminar_190.jpg`, `charminar_045.jpg` / `charminar_044.jpg`, `charminar_023.jpg` / `charminar_024.jpg`, and `charminar_260.jpg` / `charminar_257.jpg` are near-identical or same-session views; train and holdout must not separate them.
- `jaisalmer_fort_131.jpg` / `jaisalmer_fort_132.jpg`, `meenakshi_temple_007.jpg` / `aug_meenakshi_temple_271.jpg`, `mehrangarh_fort_025.jpg` / `mehrangarh_fort_228.jpg`, and `aug_mysore_palace_292.jpg` / `mysore_palace_090.jpg` are the same scene with minor framing, processing, or augmentation differences.

All 11 <=4 cross-split pairs were visually reviewed. At least the Charminar colour/black-and-white pair and the Mysore edited pair are definite same-source leakage; the other nine are sufficiently overlapping views to group conservatively. The absence of SHA-256 duplicates does not rule out edited copies.

## Implication and next action

The 78.51% MobileNetV2 test result is a historical baseline, not a reliable estimate on independent source photos because cross-split leakage is confirmed. Very small Badami/Sanchi test groups add uncertainty. Review all flagged pairs and source/augmentation provenance, then build a source-grouped split where every original and all its edits stay in one split. Do not remove files solely from dHash distance. Preserve the old 470-photo test for historical comparison, but use a newly frozen, independent phone-photo test for model selection and the 90% goal; never train on that test set.

`grouped_split_manifest.py` generated an initial grouped proposal in Colab on 21 October: 3,141 photos, 3,120 candidate groups, 21 <=4 pairs (11 crossing old splits). The generated proposal remains in the user's temporary `/content/virasatai_grouped_split` folder. It is **not** a frozen independent test set. Do not claim a new independent test score from it.

A second manifest-level scan found 26 further old cross-split pairs at dHash distance 5–8. Visual inspection of `aug_mysore_palace_295.jpg` and `mysore_palace_093.jpg` confirmed another edited/cropped same-source photo that the distance-4 proposal misses. Therefore the first proposal must not be frozen. Next generate a distance-8 proposal to hold these candidates together, inspect its new pairs, and supplement perceptual hashes with original-source/augmentation provenance. A low dHash threshold alone cannot certify an independent split.

The unreviewed distance-8 proposal generated in Colab had 3,141 photos, 3,067 candidate groups, and 79 near pairs. All 79 same-class dHash <=8 candidates have now been visually inspected. Of the 37 old cross-split pairs, 31 are same-source or sufficiently overlapping same-session views and six are distinct photographs. Of the 42 old same-split pairs, 36 should be grouped and six are distinct. The exact decisions are recorded in `reviewed_source_pairs_2026-10-21.json` and consumed through `--review-file`.

A corrected **candidate** proposal was generated locally in `grouped_split_reviewed_2026-10-21/`: 3,141 photos, 3,077 candidate source groups, 67 reviewed/grouped dHash pairs, and 12 reviewed false-positive pairs excluded from hash grouping. Every reviewed same-source pair shares one source group and one split; every reviewed false-positive pair belongs to separate groups. No source group crosses train/validation/test. Four unit tests and this full-manifest integrity check passed. These checks cover the reviewed <=8 pairs only. The new split is **not frozen**: dHash can miss more distant edits, original-source/augmentation provenance remains incomplete, and an independent phone-photo holdout does not yet exist. No new model accuracy or APK is claimed.

A metadata follow-up found 67 files named `aug_` (Meenakshi 24, Mysore 39, Charminar 1, Victoria Memorial 3). Only eight of these are grouped with a non-`aug_` original by the current visual/hash review; 59 are singleton source groups. The manifest has no parent-photo ID, so their source lineage cannot be established from filenames or hashes alone. Before freezing the split, trace these 59 files to their actual originals using the preparation notebook/source records; if a parent is missing or uncertain, keep its derived image out of validation and test rather than assuming independence. This finding does not invalidate the completed <=8 pair decisions.

Three image-quality cases need a decision before model training: `ajanta_ellora_caves_062.jpg` mostly shows people, `badami_commons_exterior_4a92e9cf43cc.jpg` has overlaid labels, and `khajuraho_monuments_223.jpg` is an annotated diagram of a photo. They are flagged for review, not silently removed.

An optimized MobileNetV2 **candidate training script** was prepared at `train_reviewed_mobilenetv2_colab.py` and syntax checked. It uses the reviewed proposal, removes all 67 pre-generated `aug_` files whose parent links are not fully known, applies augmentation to training photos only, uses ImageNet transfer learning, class weights, AdamW, a lower-learning-rate full fine-tune with batch normalization frozen, and validation-selected checkpoints. It writes per-class precision/recall/F1 and a confusion matrix after a single candidate test evaluation. The reviewed manifest and script were uploaded to the owner's private curated Drive as IDs `19BLdHeZLeq4YxLvB8OWLjwRZs_mgEWSv` and `1eyXQAI4OF11s8mlpQCo8wTun9WlqhdSk`; metadata readback confirmed both in folder `1FL98KnE_e-BigfluYAGfFgLXdXtx9WWT`. Its result remains candidate-only until source provenance, quality flags, and a new independent real-phone test are resolved.

The user subsequently ran this script on a T4 GPU in Colab. It restored all 3,074 retained photos (2,155 train / 463 validation / 456 test), trained 15 frozen and 15 fine-tune epochs, and reported 0.688596 candidate test accuracy (314/456), macro precision 0.7007, macro recall 0.6632, macro F1 0.6650. Weak recall includes Badami 3/8, Jaisalmer 8/21, Mysore 2/6 and Red Fort 8/22. The result was saved in the owner's Drive folder `1rvsp9DdzKsLnPrGCaANyRgq1mLrIsuMX`. The `google_auth_httplib2` timeout lines were warnings; training completed. This run is **not an improvement** over the historical 78.51% MobileNetV2 number, but the two figures use different splits and should not be interpreted as a clean same-test comparison. Keep the app's existing model. This reviewed test set has now informed model selection and must be treated as a development benchmark, not a final independent 90% test.

An EfficientNetV2-S comparison script using the same manifest, exclusions and splits was prepared at `train_reviewed_efficientnetv2s_colab.py`, syntax checked, and uploaded to the same private Drive folder as ID `1L7sbHOD1RLXBtIUiG493rKeHJp1ybwk9`. It reuses restored photos if the current Colab runtime is still alive.

The user ran EfficientNetV2-S on the same 3,074 retained photos and 456-photo development test. It scored 0.6732456 accuracy (307/456), macro precision 0.6784, macro recall 0.6623, and macro F1 0.6513, below the MobileNetV2 candidate's 0.688596 on the same split. Its model and metrics were saved privately in Drive folder `1prW2UotGzrbaBVlR4005xA0C3h1TMTuU`. Neither candidate meets the 90% target; neither should replace the app model. The test has been used for model selection, so a new independent phone-photo holdout is needed for a final claim. Weak/ambiguous classes and high-confidence errors need visual label and image-source review before further architecture changes. A contact-sheet generator for all EfficientNetV2-S development-test errors was prepared at `review_efficientnet_errors_colab.py`, syntax checked, and uploaded as Drive file `15-Ruz1EEGPALtEkhgJQHCRkhGgkWJRhP`; it has not yet run.
