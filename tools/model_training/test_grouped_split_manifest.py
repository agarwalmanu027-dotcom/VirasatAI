"""Focused tests for source-group leakage protection."""

import unittest

from grouped_split_manifest import propose


def row(label, name, visual_hash, old_split):
    return {"label": label, "raw_name": name, "file_id": label + name,
            "sha256": name, "dhash": hex(visual_hash), "split": old_split}


class GroupedSplitTests(unittest.TestCase):
    def test_edited_copy_stays_in_one_split(self):
        rows = [row("charminar", "colour", 0, "test"),
                row("charminar", "bw", 1, "train"),
                row("charminar", "other1", 0xffffffffffffffff, "train"),
                row("charminar", "other2", 0xaaaaaaaaaaaaaaaa, "train"),
                row("charminar", "other3", 0x5555555555555555, "train")]
        proposed, summary, pairs = propose(rows)
        self.assertEqual(proposed[0]["source_group"], proposed[1]["source_group"])
        self.assertEqual(proposed[0]["split"], proposed[1]["split"])
        self.assertEqual(summary["old_cross_split_near_pairs"], 1)
        self.assertEqual(len(pairs), 1)
        self.assertEqual({r["split"] for r in proposed}, {"train", "val", "test"})

    def test_same_hash_different_classes_is_not_automatically_merged(self):
        rows = []
        for label in ("badami", "mahabalipuram"):
            for i, value in enumerate((0, 0xffffffffffffffff,
                                       0xaaaaaaaaaaaaaaaa, 0x5555555555555555)):
                rows.append(row(label, f"{label}_{i}", value, "train"))
        proposed, summary, _ = propose(rows)
        self.assertEqual(summary["candidate_source_groups"], 8)
        self.assertEqual(len(proposed), 8)

    def test_review_can_exclude_false_positive_and_force_edited_copy(self):
        rows = [row("fort", "unrelated_a", 0, "test"),
                row("fort", "unrelated_b", 1, "train"),
                row("fort", "edited_a", 0xffffffffffffffff, "test"),
                row("fort", "edited_b", 0xaaaaaaaaaaaaaaaa, "train"),
                row("fort", "other", 0x5555555555555555, "train")]
        reviewed = {"reviewed_dhash_false_positive": [["unrelated_a", "unrelated_b"]],
                    "reviewed_same_source_or_session": [["edited_a", "edited_b"]]}
        proposed, summary, _ = propose(rows, reviewed=reviewed)
        self.assertNotEqual(proposed[0]["source_group"], proposed[1]["source_group"])
        self.assertEqual(proposed[2]["source_group"], proposed[3]["source_group"])
        self.assertEqual(summary["candidate_source_groups"], 4)

    def test_transitive_grouping_cannot_merge_reviewed_false_positive(self):
        rows = [row("fort", "a", 0, "train"),
                row("fort", "b", 1, "val"),
                row("fort", "c", 2, "test")]
        reviewed = {"reviewed_dhash_false_positive": [["a", "c"]],
                    "reviewed_same_source_or_session": [["a", "b"], ["b", "c"]]}
        with self.assertRaisesRegex(ValueError, "Conflicting review decisions"):
            propose(rows, reviewed=reviewed)


if __name__ == "__main__":
    unittest.main()
