# Independent monument preview check — 16 October 2026

In Colab under `manuagarwal885@gmail.com`, 128 Wikimedia Commons candidates were collected for the 16 classes absent from the prior four-class review. Their 16 contact sheets and license/source manifests are in the private [review folder](https://drive.google.com/drive/folders/1U5FuPI_0YiCIxUaWwZuWjNiMiDms3vO7). All sheets were inspected visually. Only clear monument views, recognizable architecture, and a few site-specific details were accepted. Postage stamps, the Taj Hotel mistaken for the Gateway of India, text plaques, floor plans, distant skylines, people-focused pictures, near-duplicate views, and ambiguous close-ups were excluded. All eight Red Fort candidates were unsuitable; that class is absent from this check.

The original 20-class MobileNetV2 TFLite baseline scored **41/61 (67.2%)** on the 15 covered classes. Each image was the previously collected ~800px preview, not a full original: Wikimedia returned rate-limit errors for every original URL. The detailed per-image predictions, source links and accepted sheet indices are in [reviewed_15class_baseline_results.json](https://drive.google.com/file/d/1BNtU5MJ6rhLIoaVKUE2wNj-IVS5Isn65/view). All model/image bytes stayed in Colab or Drive.

| Class | Correct / tested |
| --- | ---: |
| Ajanta/Ellora | 3/7 |
| Charminar | 6/6 |
| Gateway of India | 3/3 |
| Golden Temple | 2/2 |
| Hampi | 2/3 |
| Khajuraho | 3/6 |
| Konark | 2/4 |
| Mahabalipuram | 5/5 |
| Meenakshi | 3/5 |
| Mehrangarh | 1/3 |
| Mysore Palace | 2/2 |
| Qutub Minar | 4/6 |
| Sanchi | 1/3 |
| Taj Mahal | 2/2 |
| Victoria Memorial | 2/4 |

This is a small, uneven diagnostic set, selected from online photographs and checked at 800px. It is **not** a 20-class accuracy estimate, full-resolution result, or real-phone acceptance test. The earlier 4-class, 29-tile result (18/29) used even smaller contact-sheet crops and must remain separate. Do not combine their percentages or deploy this model based on them.

Next: obtain clear Red Fort photos and independent photographs of the original four classes, improve/verify weak class labels (Ajanta/Ellora, Khajuraho, Mehrangarh, Sanchi, Victoria Memorial, Badami, Amer), then run a balanced 20-class full-image plus real phone-camera evaluation in Colab before selecting any model for the APK.
