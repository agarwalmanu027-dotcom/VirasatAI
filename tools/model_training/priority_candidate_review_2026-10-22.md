# Priority training candidate review (22 October 2026)

Seven private Commons contact sheets were visually inspected. Sixty images with
potentially useful monument views were shortlisted in
`priority_candidate_shortlist_2026-10-22.csv` (Badami 9, Sanchi 12, Mysore 9,
Red Fort 9, Jaisalmer 3, Hampi 13, Konark 5). The selected indices exist in
the corresponding source manifests and all have a recorded permitted license.

This is a **candidate shortlist**, not 60 confirmed new training photos.
`train_reviewed_v2_with_priority_colab.py` rechecks Commons source hashes,
current licenses, dimensions and dHash proximity to the old dataset and to
other candidates before adding any photo to the training directory. It leaves
the existing validation and 456-photo development-test split unchanged and
saves an accepted/rejected source audit. A different model can only be compared
after the resulting metrics are available.

The contact sheets also contained clear exclusions: a PDF cover in Badami,
generic isolated statues and Stupa 3 in Sanchi, a signboard and model of a gate
in Red Fort, a floor detail and Kot Diji Fort in Jaisalmer, a signboard in
Hampi, and near-repeat wheel close-ups in Konark. These were not shortlisted.
Some retained site interiors and partial carvings remain difficult for a
non-visitor to identify; source titles help with site identity, but title-only
verification is imperfect. Their inclusion must not be used as evidence that
an arbitrary tiny fragment can be recognized reliably.

The reviewed development test has already guided candidate selection. A new
independent phone-photo holdout is required for any final accuracy claim. The
historical 78.51% app experiment used a different, leakage-affected split;
current comparable baselines are MobileNetV2 68.86% and EfficientNetV2-S
67.32% on the 456-photo development test.

## Completed MobileNetV2 follow-up

The user ran the prepared Colab script on 22 October. All 3,074 non-augmented
source photos were restored and all 60 shortlisted Commons images passed the
runtime source-hash, license and dHash checks. Training had 2,215 photos;
validation and development test remained 463 and 456. The script completed
15 frozen and 15 fine-tuning epochs. Saved artifacts are in the private Drive
folder https://drive.google.com/drive/folders/1iAFklkBqVpNwRmFskqSpFjvx9wdmvPJE .

On the same 456-photo development test, the previous MobileNetV2 scored
314/456 = 68.86%, macro F1 66.50%; the priority-photo version scored
313/456 = 68.64%, macro F1 66.56%. Badami rose from 3/8 to 5/8, Red Fort
from 8/22 to 9/22 and Mehrangarh from 20/27 to 21/27. Amer fell from 15/26
to 13/26; Golden Temple, Hampi and Mahabalipuram each fell by one correct
photo. Other classes were unchanged. Small class denominators make these
per-class changes uncertain. The new model is not an overall improvement and
must not replace the app model. Google auth/httplib2 timeout lines in the log
were warnings; they did not stop training or artifact upload.
