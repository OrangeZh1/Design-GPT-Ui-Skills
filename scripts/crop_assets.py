#!/usr/bin/env python3
"""Exact pixel crops from an approved, inspected UI asset plan.

No image-generation service, credential, resize, background removal, or overwrite.
Coordinates use the decoded source file's stored pixel orientation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

from PIL import Image

KINDS = {"photo", "avatar", "cover", "illustration", "texture", "logo", "icon"}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def integer(value: Any, name: str, minimum: int = 0) -> int:
    if type(value) is not int or value < minimum:
        raise ValueError(f"{name} must be an integer >= {minimum}")
    return value


def label(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a nonempty string")
    return value


def object_value(value: Any, name: str) -> dict:
    if not isinstance(value, dict):
        raise ValueError(f"{name} must be an object")
    return value


def prepare(plan_path: Path, out_dir: Path, report_path: Path) -> tuple[dict, list[dict]]:
    """Preflight the entire plan before creating any output directories/files."""
    plan_path = plan_path.resolve()
    out_dir = out_dir.resolve()
    report_path = report_path.resolve()
    plan = object_value(json.loads(plan_path.read_text(encoding="utf-8")), "plan")
    if type(plan.get("version")) is not int or plan["version"] != 1:
        raise ValueError("plan version must be 1")
    if plan.get("approved") is not True:
        raise ValueError("the exact source image set must be approved first")
    label(plan.get("approval_note"), "approval_note")
    if not isinstance(plan.get("sources"), list) or not isinstance(plan.get("assets"), list):
        raise ValueError("sources and assets must be arrays")
    sources: dict[str, dict] = {}
    for raw in plan["sources"]:
        source = object_value(raw, "source")
        source_id = label(source.get("id"), "source id")
        if source_id in sources:
            raise ValueError(f"duplicate source id: {source_id}")
        file_name = label(source.get("file"), "source file")
        source_path = (plan_path.parent / file_name).resolve()
        width = integer(source.get("width"), "source width", 1)
        height = integer(source.get("height"), "source height", 1)
        with Image.open(source_path) as image:
            image.load()
            if image.size != (width, height):
                raise ValueError(f"source dimensions changed: {source_id}")
        sha = digest(source_path)
        expected_sha = source.get("sha256")
        if expected_sha is not None and expected_sha != sha:
            raise ValueError(f"source hash changed: {source_id}")
        sources[source_id] = {
            "id": source_id, "path": source_path, "size": (width, height), "sha256": sha
        }
    protected = {plan_path, *(source["path"] for source in sources.values())}
    if report_path in protected:
        raise ValueError("report would overwrite a plan or source")
    if report_path.exists():
        raise ValueError(f"report already exists: {report_path}")
    prepared = []
    ids: set[str] = set()
    targets: set[Path] = set()
    for raw in plan["assets"]:
        asset = object_value(raw, "asset")
        asset_id = label(asset.get("id"), "asset id")
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]*", asset_id):
            raise ValueError("asset id must use letters, digits, underscores or hyphens")
        if asset_id in ids:
            raise ValueError(f"duplicate asset id: {asset_id}")
        ids.add(asset_id)
        source_id = label(asset.get("source"), "asset source")
        if source_id not in sources:
            raise ValueError(f"unknown source: {source_id}")
        source = sources[source_id]
        if asset.get("kind") not in KINDS:
            raise ValueError(f"unsupported intrinsic asset kind: {asset_id}")
        if asset.get("contains_ui_overlay") is not False:
            raise ValueError(f"asset must be inspected as free of UI overlays: {asset_id}")
        pages = asset.get("pages")
        if not isinstance(pages, list) or not pages:
            raise ValueError("asset pages must be a nonempty array")
        for page in pages:
            label(page, "page id")
        label(asset.get("purpose"), "asset purpose")
        box = asset.get("box")
        if not isinstance(box, list) or len(box) != 4:
            raise ValueError("box must be [x, y, width, height]")
        x, y, width, height = [
            integer(value, name, minimum)
            for value, name, minimum in zip(box, ("x", "y", "width", "height"), (0, 0, 1, 1))
        ]
        source_w, source_h = source["size"]
        if x + width > source_w or y + height > source_h:
            raise ValueError(f"crop exceeds source bounds: {asset_id}")
        file_name = label(asset.get("file"), "asset file")
        relative = Path(file_name)
        if relative.is_absolute() or ".." in relative.parts or relative.suffix.lower() != ".png":
            raise ValueError("asset file must be a relative PNG path without '..'")
        target = (out_dir / relative).resolve()
        if not target.is_relative_to(out_dir):
            raise ValueError("asset path escapes output directory")
        if target in protected or target == report_path:
            raise ValueError("asset would overwrite a source, plan or report")
        if target in targets:
            raise ValueError(f"duplicate output path: {target}")
        if target.exists():
            raise ValueError(f"asset already exists: {target}")
        targets.add(target)
        prepared.append({
            "asset": asset, "source": source, "target": target,
            "pillow_box": (x, y, x + width, y + height)
        })
    return plan, prepared


def export_plan(plan_path: Path, out_dir: Path, report_path: Path, dry_run: bool = False) -> dict:
    plan_path, out_dir, report_path = map(Path, (plan_path, out_dir, report_path))
    plan, prepared = prepare(plan_path, out_dir, report_path)
    result = {
        "version": 1,
        "plan": str(plan_path.resolve()),
        "approval_note": plan["approval_note"],
        "dry_run": dry_run,
        "assets": []
    }
    # Check every source once more before the first write.
    for source in {entry["source"]["id"]: entry["source"] for entry in prepared}.values():
        if digest(source["path"]) != source["sha256"]:
            raise ValueError(f"source changed after validation: {source['id']}")
    for entry in prepared:
        asset, source, target = entry["asset"], entry["source"], entry["target"]
        record = {
            "id": asset["id"], "source": source["id"],
            "source_file": str(source["path"]), "source_sha256": source["sha256"],
            "source_size": list(source["size"]), "box": asset["box"],
            "file": str(target), "kind": asset["kind"],
            "pages": asset["pages"], "purpose": asset["purpose"],
            "pixel_size": asset["box"][2:], "visual_review": "pending"
        }
        if not dry_run:
            with Image.open(source["path"]) as image:
                cropped = image.convert("RGBA").crop(entry["pillow_box"])
            target.parent.mkdir(parents=True, exist_ok=True)
            # Exclusive create also refuses outputs created after preflight.
            with target.open("xb") as output:
                cropped.save(output, format="PNG")
            alpha_min, alpha_max = cropped.getchannel("A").getextrema()
            record["has_transparency"] = alpha_min < 255
            record["alpha_extrema"] = [alpha_min, alpha_max]
            record["output_sha256"] = digest(target)
        result["assets"].append(record)
    if not dry_run:
        report_path.parent.mkdir(parents=True, exist_ok=True)
        with report_path.open("x", encoding="utf-8") as output:
            json.dump(result, output, ensure_ascii=False, indent=2)
            output.write("\n")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", required=True, type=Path)
    parser.add_argument("--out-dir", required=True, type=Path)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    report_path = args.report or args.out_dir / "crop-results.json"
    try:
        result = export_plan(args.plan, args.out_dir, report_path, args.dry_run)
    except (ValueError, OSError, Image.DecompressionBombError) as exc:
        parser.exit(2, f"crop plan rejected: {exc}\n")
    verb = "validated" if args.dry_run else "exported"
    print(f"{verb} {len(result['assets'])} assets; visual review pending")


if __name__ == "__main__":
    main()
