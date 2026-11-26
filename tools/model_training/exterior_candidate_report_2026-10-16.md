# Exterior photo fine-tune: candidate evaluation

Date: 16 October 2026. This experiment ran in Google Colab under the owner's private Drive account. The model and photos were not downloaded to the laptop, and no APK change was made.

The starting point was the 20-class MobileNetV2 model trained on 3,141 prepared photos: 2,201 train, 470 validation and 470 test. After restoring the exact original split, 19 visually reviewed exterior previews were added to the **training split only** (7 Badami Cave Temples, 12 Amer Fort). The selected images and source records are in [the private Drive review folder](https://drive.google.com/drive/folders/1BW_MqBDNkgZs0g7EwEb7NzTWIwMYs_4A). No independent test preview was used for training.

| Check | Original model | Exterior candidate |
| --- | ---: | ---: |
| Original 470-photo test | 369/470 (78.5%) | 369/470 (78.5%) |
| Badami in original test | 2/8 | 2/8 |
| Amer in original test | 15/26 | 16/26 |
| Separate 29 preview tiles | 18/29 | 18/29 |
| Badami in separate preview test | 2/8 | 3/8 |
| Amer in separate preview test | 4/8 | 3/8 |

The 29-photo check covers only four classes. Its inputs were 210 × 180 contact-sheet crops, not full-size images or phone camera photos. Jaisalmer had only two unambiguous photos. It is an exploratory diagnostic, not an overall 20-class score. The original test also influenced which classes were targeted, so it is not an untouched final assessment.

Decision: keep the original model as the benchmark and keep this fine-tune as an **unreleased candidate**. The candidate did not improve overall accuracy and traded one Amer preview success for one Badami preview success. Do not replace the app model on these results.

Next evaluation: collect independently sourced, verified full-size images for all 20 classes, with varied angles, light, distance and camera types; reserve them outside training and selection. Check more real phone photographs of Badami and Amer, including confusing sites. Before any APK integration, assess per-class precision/recall, confident wrong answers and an unknown-monument rejection threshold. Review existing training labels and near-duplicates before more fine-tuning. Additional photo quantity alone is not proof of better recognition.

Candidate model and 470-photo metrics: [private Drive folder](https://drive.google.com/drive/folders/1RiXIvTl-_0uokkPQ7J0oqGfaNaQ4vNuG). The independent preview comparison is [saved separately](https://drive.google.com/file/d/1cT_Dz67RlCJpDoMS_LDdkiU0-eVfMkff/view). The Colab run is in [the existing notebook](https://colab.research.google.com/drive/1mfwQrJM8lYUqTr8r3lfShLzTDCJ1H96-?authuser=1).
