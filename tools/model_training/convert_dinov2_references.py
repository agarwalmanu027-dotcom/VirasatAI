"""Convert the evaluated Colab reference bank into simple Flutter assets."""

from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / "frontend_recovered" / "assets" / "models"
SOURCE = ASSETS / "monument_references.npz"


def main() -> None:
    with np.load(SOURCE) as bank:
        embeddings = bank["embeddings"]
        class_ids = bank["class_ids"]
        labels = bank["labels"].tolist()
    expected_labels = (ASSETS / "dinov2_labels.txt").read_text(encoding="utf-8").splitlines()
    assert embeddings.shape == (2155, 384)
    assert class_ids.shape == (2155,)
    assert labels == expected_labels and len(labels) == 20
    assert class_ids.min() == 0 and class_ids.max() == 19
    assert np.allclose(np.linalg.norm(embeddings, axis=1), 1, atol=1e-4)
    embeddings.astype("<f4").tofile(ASSETS / "dinov2_references.f32")
    class_ids.astype("u1").tofile(ASSETS / "dinov2_reference_ids.u8")
    print("REFERENCE_ASSETS_READY", embeddings.shape, len(labels))


if __name__ == "__main__":
    main()
