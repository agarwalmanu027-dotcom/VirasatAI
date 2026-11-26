# Monument recognition: second candidate experiment

Date: 15 October 2026

The existing 20-monument image set was reused: 3,141 selected photos, split into
2,201 training, 470 validation, and 470 held-out test images. The split excludes
exact duplicate files and same-class images with very close perceptual hashes.
Place identity has not been checked manually for every image, and this is not
an independent phone-camera test.

| Candidate | Held-out test accuracy |
| --- | ---: |
| Small CNN trained from scratch | 33.4% |
| ImageNet-pretrained MobileNetV2, then fine-tuned | 78.5% |

The MobileNetV2 run used 10 frozen-backbone epochs and four fine-tuning epochs.
Its final validation accuracy was 75.7%. The pretrained weights were downloaded
in Google Colab with the user's approval. Nothing was installed on the laptop.

The weakest held-out classes were Badami Cave Temples (2/8, 25%), City Palace
Udaipur (13/27, 48%), Jaisalmer Fort (11/21, 52%), and Amer Fort (15/26, 58%).
Those classes need focused image and label review before deployment. Badami also
has only 56 selected images, so its eight-photo test estimate is unstable.

The candidate model and labels are saved in the user's private Google Drive:
https://drive.google.com/drive/folders/1QMtQcTDq4DFYru2uUYO2ei2WFU-BcKZ7

The folder contains `monument_model.keras`, `monument_model.tflite`, `labels.txt`,
`metrics.json`, and `tflite_qa.json`. The TFLite export was run on 20 held-out
samples; its top prediction agreed with Keras on all 20, with maximum probability
difference of approximately 0.00000453. This confirms basic conversion parity,
not real-world recognition accuracy or Android integration.

Next: inspect the raw labels and images for the weak classes; collect verified,
varied views where needed; test unseen phone photos; then decide whether this
model is ready to integrate into the Flutter app. Keep the current app unchanged
until those checks pass.
