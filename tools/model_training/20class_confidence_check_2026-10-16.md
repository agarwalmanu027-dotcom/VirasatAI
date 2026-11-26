# 20-class model confidence check — 16 October 2026

The existing 20-class MobileNetV2 is trained and saved in the owner's private Google Drive. This is a calibration and diagnostic check, not a new training run or an APK integration.

Colab restored all 3,141 source photos from the saved split manifest and verified their SHA-256 hashes: 2,201 training, 470 validation and 470 held-out test photos, with zero restore errors. The restored data and model remained in Colab; no photo or model was downloaded to the laptop.

Baseline accuracy without abstention was 356/470 (75.7%) on validation and 369/470 (78.5%) on the held-out test. A threshold of 0.55 was selected using validation only because 305/337 accepted validation predictions (90.5%) were correct while retaining 337/470 photos (71.7%). On the held-out test this threshold retained 371/470 photos (78.9% coverage) with 331/371 correct (89.2% precision).

The separate 15-class online-photo preview set exposes weaker generalization. Without abstention the model got 41/61 correct (67.2%). At the validation-selected 0.55 threshold, it accepted 42/61 and got 34/42 correct (81.0%). An exploratory 0.90 cutoff accepted 21/61 and got 20/21 correct (95.2%), but this is a small, selected preview set and must not be treated as a guarantee or tuned into a formal accuracy claim. Red Fort and the earlier four-class set were absent from this 61-photo check; no real phone-camera set has been tested.

Recommendation for the first offline APK integration: show a tentative suggestion only when confidence is high, require user confirmation before opening a guide, and offer manual selection for every other result. Do not call the model production-validated yet. The user has authorized bringing only the final model file from Colab/Drive into the project. Adding the Flutter inference libraries is awaiting the user's answer to a separate download question.
