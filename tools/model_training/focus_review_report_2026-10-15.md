# Focused monument image review and third candidate

Date: 15 October 2026

The existing MobileNetV2 candidate was weakest on Badami Cave Temples, City
Palace Udaipur, Jaisalmer Fort, and Amer Fort. A 30-photo contact sheet from
each class showed many close-up details, interiors, and less useful landscape
views. New exterior and distant-view candidates were collected from Wikimedia
Commons, inspected on contact sheets, checked for a suitable license and
source dimensions, and screened for near-duplicates against the prepared
3,141-image dataset.

The private `raw_copy` Drive dataset received **21 reviewed training photos**:
Badami 5, City Palace 3, Jaisalmer 6, and Amer 7. Another 11 photos were put
in a separate external holdout folder: Badami 2, City Palace 1, Jaisalmer 4,
and Amer 4. The selection/source manifest was saved in the private curated
dataset root. No original photos were deleted. Fifteen other candidates were
skipped or failed because they were near-duplicates, too small, or Wikimedia
temporarily rate-limited requests. The three wrong external predictions were
reviewed visually; the images show their intended monuments, so they remain
useful hard examples for evaluation.

The unchanged 78.5% MobileNetV2 candidate scored **8/11 (72.7%)** on those
11 new photos. The sample is small and is concentrated in four classes.
An experimental second fine-tune used the 21 additions plus all 2,201
original training photos, leaving the original validation, test, and external
holdout photos out of training. Results:

| Measure | Original MobileNetV2 | Focus fine-tune |
| --- | ---: | ---: |
| Original 470-photo test | 78.5% | 78.5% |
| New 11-photo external holdout | 8/11 | 8/11 |
| Badami original test | 2/8 | 2/8 |
| City Palace original test | 13/27 | 14/27 |
| Jaisalmer original test | 11/21 | 14/21 |
| Amer original test | 15/26 | 14/26 |

The focus fine-tune is saved as a **candidate only** in the user's private
Drive folder: https://drive.google.com/drive/folders/13Z5sq6_XCWPY34HNgp_wii_FGcYlA-xp .
It contains its Keras model, labels, and metrics. The first candidate remains
in https://drive.google.com/drive/folders/1QMtQcTDq4DFYru2uUYO2ei2WFU-BcKZ7 .
Neither was integrated into the Flutter app. The new model did not improve
overall or external accuracy, so it should not replace the first candidate
yet. It was not exported to TFLite.

The original test set was used to identify weak classes, so further use of it
for selection is not a fully unbiased final test. A larger independent set
of unseen phone photos, especially Amer and Badami exteriors under different
lighting, is needed before deployment. Some class labels in the raw dataset
also still need fuller manual review. The 300-per-main and 100-per-nearby
photo targets are collection targets, not achieved counts or prerequisites
proven necessary for accuracy.
