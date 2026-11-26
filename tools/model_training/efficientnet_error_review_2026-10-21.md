# EfficientNetV2-S development-test error review — 21 October 2026

The user's Colab run made ten contact sheets in private Drive folder `1a53qqqXSIxpG0EGC_DL31ZV4iFUJQsj4`. All ten sheets were visually inspected. This is a development-test audit, not a new independent test. The model missed 149/456 photos; seven wrong guesses had probability >=0.50 and none reached 0.90. These probabilities alone do not establish a safe operating threshold, because correct predictions must also be measured at each threshold.

Most errors involve valid-looking but visually generic partial views: carvings, stone corridors, arches, fort walls, interior rooms and distant buildings. These details recur across several monument groups. In particular, Hampi (16 wrong), Konark (15), Jaisalmer Fort (12), Red Fort (12), City Palace Udaipur (12), Khajuraho (12) and Mehrangarh Fort (10) account for many failures. A classifier cannot reliably infer a specific site from an undistinctive fragment alone; app behavior should abstain or request another view when evidence is insufficient.

Source/label review flags, not deletion or relabel decisions:

- `amer_fort_124.jpg` (sheet 09, row 1 column 2): mostly a child, with little identifiable monument evidence. Verify whether it belongs in monument-recognition data.
- `sanchi_stupa_206.jpg` (sheet 04, row 3 column 1) and `sanchi_stupa_194.jpg` (sheet 09, row 3 column 4): show temple/ruin structures rather than an identifiable view of the Great Stupa. Check whether the class intentionally means the wider Sanchi site or the stupa itself.
- `jaisalmer_fort_241.jpg` (sheet 02, row 1 column 2): heavily carved dark stone interior looks unlike the usual Jaisalmer Fort views in this dataset. Confirm the exact source and site before changing its label.
- Existing quality flags in `split_audit_2026-10-21.md` still need disposition.

Do not train on or select another model by repeatedly using these 456 development-test photos. After source verification and new, diverse training photos are added, keep a separate set of independently sourced real phone photos untouched for the final 90% target. For new training data, prioritize distinct, verified views of weak classes: whole-site context, side/entrance/interior views, and characteristic partial details. Avoid screenshot-of-screen images, watermarks, maps, unrelated people, near-duplicate downloads and images of nearby places under a main-monument label.
