# Analysis-Led Asset Slicing

Read after the complete image set is approved and the eight-part analysis is complete. Section six's inventory controls the slices.

## Decide what remains an image

| Visible element | Preferred treatment |
| --- | --- |
| Product/photo/avatar/cover/illustration/texture | Crop intrinsic artwork if clean |
| Brand logo or distinctive illustrated icon | Original SVG/transparent asset, or clean crop |
| Ordinary functional icon | Matching icon library or clean SVG |
| Text, counts, dates, badges, prices | Editable text/components |
| Buttons, cards, fields, navigation | Real layout/components and styles |
| OS status bar, home indicator, WeChat capsule | Host platform chrome; no app asset |
| Whole page | Reference only, unless explicitly requested static output |

Do not slice every rectangle into a bitmap UI. One asset may serve multiple pages; match actual imagery before deduplicating.

## Inspect and measure

1. Preserve approved originals and record the actual version. Inspect the whole set, then each needed crop in detail.
2. Decode local sources and measure their pixel dimensions. Coordinates are in the **stored, decoded image**, not CSS pixels, preview display pixels or an imagined 750-wide canvas.
3. For EXIF-oriented uploads, create and inspect an orientation-normalized source first if needed; record it as a distinct source with new dimensions/hash. The crop script does not rotate sources.
4. Crop boxes use `[x, y, width, height]`, integer pixels, origin at top-left. Require positive width/height and bounds fully inside the source. Do not clamp invalid boxes or silently add padding.
5. Inspect for embedded text, badges, shadows from neighboring UI, navigation, and device chrome. Crop only clean intrinsic artwork.
6. Estimate boxes only as a starting point, inspect actual pixels before export, and refine visually. Do not mark “已核对” without seeing the region.
7. If no clean region exists, continue other assets and mark this one “待原始素材” or “需编辑派生素材”. Native image edits occur on a separate copy and must be labelled.

A rectangular crop preserves existing alpha; it does **not** remove a background. Saving RGBA PNG alone does not make an opaque screenshot transparent. Seek genuine transparent originals or use the native image tool for explicitly requested background removal. Never claim a replacement is an exact extracted original.

## Crop-plan schema

Use `metadata/crop-plan.json`. Only add approval after the user approves the exact source set. Fill actual filenames, dimensions and coordinates after inspection; the following is an illustrative schema, not a completed crop plan.

```json
{
  "version": 1,
  "approved": true,
  "approval_note": "Record the user's actual approval of these source versions here",
  "sources": [
    {
      "id": "P01",
      "file": "../source/homepage.png",
      "width": 750,
      "height": 1624
    }
  ],
  "assets": [
    {
      "id": "A001",
      "source": "P01",
      "file": "home/hero-art.png",
      "box": [40, 200, 300, 240],
      "kind": "illustration",
      "pages": ["P01"],
      "purpose": "Homepage hero artwork",
      "contains_ui_overlay": false
    }
  ]
}
```

- Source paths resolve relative to the plan's directory. Absolute local sources are also accepted.
- Required dimensions detect plans made for a different screenshot size.
- Optional source `sha256` detects a changed same-size image. Prefer it when source bytes are available; retain version information in the approval manifest.
- `kind` is one of `photo`, `avatar`, `cover`, `illustration`, `texture`, `logo`, `icon`.
- Asset paths are relative PNG paths within the output directory.
- `contains_ui_overlay: false` is an inspected assertion by the agent, not an automatic image classification.
- Script approval fields document upstream authorization; the script cannot independently prove what the user approved.
- Do not put CSS-only/library-only/pending assets in the export plan; keep them in the full inventory.

## Exact crop utility

Needs Python 3.10+ and Pillow. Install Pillow only if it is missing in the actual execution environment.

```bash
python -m pip install Pillow
python scripts/crop_assets.py --plan output/page-set/demo/metadata/crop-plan.json --out-dir output/page-set/demo/assets --report output/page-set/demo/metadata/crop-results.json --dry-run
python scripts/crop_assets.py --plan output/page-set/demo/metadata/crop-plan.json --out-dir output/page-set/demo/assets --report output/page-set/demo/metadata/crop-results.json
```

The script validates all plans before writing, refuses out-of-bounds coordinates and path traversal, protects source files and existing outputs, preserves crop pixels without resizing, and writes source/output SHA-256 plus measured dimensions. Dry-run validates only and creates no files.

The output reports `visual_review: "pending"`; exporting pixels is not visual QA. It reports real alpha transparency using pixel alpha extrema.

If a run is interrupted, inspect partial output and use a new empty output location for the next attempt; the utility intentionally does not overwrite existing files. Do not delete approved sources to rerun.

If there is no local image byte access or execution tool, give the analysis and inventory, report that actual export is pending, and request the required original files or continue when the host provides them. Never invent output files.

## Review and deliver

Inspect every actual crop with the image viewer, compare it to the approved page, and verify:

- intended subject is complete; no accidental cut-off or adjacent UI;
- no baked-in editable text/badges/device chrome;
- dimensions and image ratio fit the planned component;
- reused assets truly match across pages;
- transparency is genuine where required, otherwise mark unresolved;
- source version and file mapping agree with the approval manifest.

Update asset inventory and crop-results with the **actual** visual review. Mark replacements as derived and keep their relation to the original. Deliver clean PNGs, the inventory and coordinate/source mapping; add a ZIP/contact sheet only if requested or useful and actually created. Keep structural UI and CSS/icon-library items documented even though they are not bitmap files.
