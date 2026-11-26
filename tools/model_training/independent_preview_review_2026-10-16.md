# Independent web-preview check (16 October 2026)

The user requested Colab-only evaluation. No model or test image was downloaded
to the laptop. In the existing [Colab notebook](https://colab.research.google.com/drive/1mfwQrJM8lYUqTr8r3lfShLzTDCJ1H96-?authuser=1), the new [candidate review folder](https://drive.google.com/drive/folders/1HYRw4IoU2uF2nVaYnKLY-k6dBplddkVj) contains four contact sheets and a manifest. Candidate generation excluded the prior 3,141-image manifest by perceptual near-match checks, and excluded all previously reviewed Commons titles/SHA-1s. The 48 candidates were manually reviewed by contact sheet. The evaluation selection rejected non-distinctive street scenes, inscriptions, a mural, a sculpture, and ambiguous details.

The [saved metrics](https://drive.google.com/file/d/1zLSPASCZZkftCbAZh_ZsKAUAjEH2v6Hv/view) compare the original transfer model against the focused fine-tune, on the **same 29 selected images**. The inputs were 210x180 contact-sheet tiles cropped and resized to 160x160. They were not full-resolution originals or phone photos.

| Class | Reviewed inputs | Original correct | Focused correct |
| --- | ---: | ---: | ---: |
| Badami Cave Temples | 8 | 2 | 2 |
| City Palace Udaipur | 11 | 11 | 11 |
| Jaisalmer Fort | 2 | 1 | 1 |
| Amer Fort | 8 | 4 | 3 |
| **Total** | **29** | **18 (62.1%)** | **17 (58.6%)** |

This is a diagnostic check of four weak classes, **not** an overall 20-class
accuracy estimate. Jaisalmer's candidate category mostly yielded ordinary
streets and signs; only two images were unambiguous enough to include. Badami
and Amer remain weak, and the focused version still does not replace the
original candidate. Neither should be integrated into the APK yet. Next:
review and strengthen source labels, collect diverse verified views of Badami
and Amer, obtain a larger independent full-resolution set covering all 20
classes, and test real phone-camera photos before an integration decision.

Colab code: `independent_online_test_colab.py` prepared review sheets;
`score_independent_review_colab.py` scored the selected previews. No schedule
was made.
