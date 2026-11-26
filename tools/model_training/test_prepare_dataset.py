"""Small safety checks for dataset splitting and cross-class duplicate detection."""

import tempfile
import unittest
from pathlib import Path

from PIL import Image

from prepare_dataset import assign_splits, inspect


class DatasetPreparationTest(unittest.TestCase):
    def test_split_keeps_each_class_and_no_exact_duplicate_cross_class(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for label, colour in (("taj_mahal", 30), ("qutub_minar", 130)):
                folder = root / label
                folder.mkdir()
                for number in range(10):
                    Image.new("RGB", (240, 250), (colour, number * 10, 30)).save(
                        folder / f"{number}.png"
                    )
            classes, rejected, duplicates = inspect(root, 224)
            self.assertEqual({k: len(v) for k, v in classes.items()},
                             {"qutub_minar": 10, "taj_mahal": 10})
            self.assertEqual(rejected, [])
            self.assertEqual(duplicates, [])
            rows = assign_splits(classes, 42)
            for label in classes:
                self.assertEqual({row["split"] for row in rows if row["label"] == label},
                                 {"train", "val", "test"})
            # A mislabeled copy must be visible in the audit rather than used as training data.
            (root / "qutub_minar" / "wrong.png").write_bytes(
                (root / "taj_mahal" / "0.png").read_bytes()
            )
            _, _, duplicates = inspect(root, 224)
            self.assertTrue(any(item["class"] != item["first_class"] for item in duplicates))


if __name__ == "__main__":
    unittest.main()
