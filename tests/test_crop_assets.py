"""Validate pixel fidelity, provenance, preflight and output protection."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

from PIL import Image

SPEC = importlib.util.spec_from_file_location(
    "crop_assets", Path(__file__).resolve().parents[1] / "scripts" / "crop_assets.py"
)
crop_assets = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(crop_assets)


class CropAssetsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / "source.png"
        self.image = Image.new("RGBA", (8, 6))
        self.image.putdata([
            (x * 20, y * 30, 90, 0 if (x, y) == (2, 1) else 255)
            for y in range(6) for x in range(8)
        ])
        self.image.save(self.source)
        self.plan_path = self.root / "plan.json"
        self.out = self.root / "assets"
        self.report = self.root / "crop-results.json"
        self.plan = {
            "version": 1, "approved": True, "approval_note": "Approved test fixture",
            "sources": [{"id": "P01", "file": "source.png", "width": 8, "height": 6}],
            "assets": [{
                "id": "A001", "source": "P01", "file": "home/art.png",
                "box": [2, 1, 3, 2], "kind": "illustration",
                "pages": ["P01", "P02"], "purpose": "Shared artwork",
                "contains_ui_overlay": False
            }]
        }

    def run_plan(self, dry_run=False):
        self.plan_path.write_text(json.dumps(self.plan), encoding="utf-8")
        return crop_assets.export_plan(self.plan_path, self.out, self.report, dry_run)

    def assert_rejected_without_outputs(self):
        with self.assertRaises(ValueError):
            self.run_plan()
        self.assertFalse(self.out.exists())
        self.assertFalse(self.report.exists())

    def test_exact_pixels_alpha_dimensions_and_hashes(self):
        source_bytes = self.source.read_bytes()
        result = self.run_plan()
        target = self.out / "home" / "art.png"
        with Image.open(target) as actual:
            expected = self.image.crop((2, 1, 5, 3))
            self.assertEqual(actual.size, (3, 2))
            self.assertEqual(actual.tobytes(), expected.tobytes())
        record = result["assets"][0]
        self.assertTrue(record["has_transparency"])
        self.assertEqual(record["visual_review"], "pending")
        self.assertEqual(record["source_sha256"], hashlib.sha256(source_bytes).hexdigest())
        self.assertEqual(record["output_sha256"], hashlib.sha256(target.read_bytes()).hexdigest())
        self.assertEqual(self.source.read_bytes(), source_bytes)
        self.assertEqual(json.loads(self.report.read_text()), result)

    def test_dry_run_creates_nothing(self):
        result = self.run_plan(dry_run=True)
        self.assertTrue(result["dry_run"])
        self.assertFalse(self.out.exists())
        self.assertFalse(self.report.exists())
        self.assertNotIn("output_sha256", result["assets"][0])

    def test_opaque_pixels_do_not_claim_transparency(self):
        self.plan["assets"][0]["box"] = [4, 3, 2, 2]
        result = self.run_plan()
        self.assertFalse(result["assets"][0]["has_transparency"])

    def test_unapproved_set_rejected(self):
        self.plan["approved"] = False
        self.assert_rejected_without_outputs()

    def test_invalid_boxes_rejected(self):
        for box in ([-1, 0, 2, 2], [7, 5, 2, 2], [0, 0, 0, 1], [True, 0, 1, 1], [0, 0, 1.5, 1]):
            with self.subTest(box=box):
                self.plan["assets"][0]["box"] = box
                self.assert_rejected_without_outputs()

    def test_stale_dimensions_or_hash_rejected(self):
        self.plan["sources"][0]["width"] = 9
        self.assert_rejected_without_outputs()
        self.plan["sources"][0]["width"] = 8
        self.plan["sources"][0]["sha256"] = "0" * 64
        self.assert_rejected_without_outputs()

    def test_path_traversal_absolute_paths_and_wrong_format_rejected(self):
        for file_name in ("../escape.png", str(self.root / "escape.png"), "art.jpg"):
            with self.subTest(file_name=file_name):
                self.plan["assets"][0]["file"] = file_name
                self.assert_rejected_without_outputs()

    def test_ui_overlay_rejected(self):
        self.plan["assets"][0]["contains_ui_overlay"] = True
        self.assert_rejected_without_outputs()

    def test_invalid_later_asset_prevents_earlier_exports(self):
        later = dict(self.plan["assets"][0], id="A002", file="later.png", box=[7, 5, 2, 2])
        self.plan["assets"].append(later)
        self.assert_rejected_without_outputs()

    def test_duplicate_paths_rejected(self):
        self.plan["assets"].append(dict(self.plan["assets"][0], id="A002"))
        self.assert_rejected_without_outputs()

    def test_source_and_existing_outputs_protected(self):
        self.plan_path.write_text(json.dumps(self.plan), encoding="utf-8")
        with self.assertRaises(ValueError):
            crop_assets.export_plan(self.plan_path, self.out, self.source)
        self.run_plan()
        target = self.out / "home" / "art.png"
        original = target.read_bytes()
        with self.assertRaises(ValueError):
            self.run_plan()
        self.assertEqual(target.read_bytes(), original)

    def test_symlink_escape_rejected(self):
        self.out.mkdir()
        outside = self.root / "outside"
        outside.mkdir()
        (self.out / "home").symlink_to(outside, target_is_directory=True)
        with self.assertRaises(ValueError):
            self.run_plan()
        self.assertFalse((outside / "art.png").exists())
        self.assertFalse(self.report.exists())


if __name__ == "__main__":
    unittest.main()
