---
name: generate-pages-from-homepage
description: Generate coherent UI page images with the current ChatGPT/Codex session's built-in image generation tool, without requesting API keys. Use an approved homepage as the visual master. After the user confirms the complete image set, inspect all images, produce an eight-part UI/UX development handoff and crop clean reusable assets. Also use for approved uploaded UI sets, screenshot analysis, asset slicing, and optional implementation in a user-selected stack. Triggers include “生成一套小程序页面”, “首页作为母版生成套图”, “直接用 ChatGPT 生图”, “整套 UI 拆解”, “分析 UI 图片”, “裁图”, “切图”, and “turn the approved UI images into code”.
---

# Generate Pages From Homepage

## Purpose and capability boundary

Act as a senior UI/UX designer and frontend engineer. Follow this sequence:

1. Collect the product brief, or inspect the user's uploaded image set.
2. Generate homepage candidates using the session's **built-in image generation tool** when a visual master is missing.
3. Use the selected homepage to generate the remaining independent page images.
4. Present the complete set and wait for the user's approval of that set.
5. Inspect **all** approved images before analyzing any individual page.
6. Produce the eight-part development handoff in `references/ui-analysis.md`.
7. Crop clean bitmap assets according to that handoff and `references/asset-slicing.md`.
8. Implement only when the user requests code and has selected a technology stack.

This skill guides an agent; it is not an image API client and cannot grant image-generation capability to a host that lacks it. Do not request an API key, inspect credential environment variables, call a relay service, or send HTTP image-generation requests. If the host has no built-in image tool, explain the limitation and continue with any supplied images. Otherwise wait for usable images; do not substitute hand-coded screenshots or claim generation occurred.

The default post-approval deliverable is the development handoff and requested asset slices, without application code. An explicit “只要图片” request limits the deliverable to images. Existing approved uploaded images can enter directly at the whole-set inspection stage without generating a new homepage.

Read `references/image-generation.md` before generation, `references/ui-analysis.md` before analysis, `references/asset-slicing.md` before cropping, and `references/implementation-quality.md` only before implementation.

## Inputs and defaults

Collect or infer:

- Product: `app_name`, `subject`, `platform`, `core_features`.
- Design: optional `style`, homepage reference, page list, page requirements, and exact copy.
- Device: requested viewport, delivery dimensions, device preset, safe areas, and platform chrome.
- Source set: images and their versions, page/state identifiers, whether the user has approved this exact set.
- Deliverable: images only, analysis, analysis plus slices, or implementation.
- Implementation: optional target stack, existing project conventions, and known business rules.

Ask only about missing information that blocks the current step. Infer conservative defaults and mark assumptions. Do not ask for a stack merely to analyze or crop images; use stack-neutral implementation guidance until code is requested.

For a WeChat mini-program, `750x1624` is a suggested **design reference**, not a guarantee of image-tool output. Record the actual returned dimensions when measurable. Do not assume a model name, a multiples-of-16 rule, a size parameter, an `n` parameter, an API response, or exact native output dimensions.

If the user supplied an exact prompt and asked for no changes, pass it unchanged. For structured briefs, compose the final prompt transparently and keep it in metadata when a filesystem is available.

## Native image generation

Use the actual built-in image tool exposed by the current host. In ChatGPT Work Mode this may be `image_gen.imagegen` / `tools.image_gen__imagegen`; other hosts may expose a different native tool. Read its schema and follow its generation, editing, reference-image, display, and persistence rules. A JSON provider setting alone is not a callable tool.

For each secondary page, pass the approved homepage as an **actual image reference**, not only a textual description. If reference images are not accessible, resolve that before calling the tool.

`runtime.local.json`, if read, contains non-secret workflow defaults only. It must never select a relay, endpoint, credential, or fixed model.

Generate one independent image per page. Homepage variants are alternatives, not additional product pages. If the user supplies a collage, inspect the whole collage, then split its pages with verified bounds; do not divide it into equal cells without checking the actual layout.

## Mobile safe areas and platform chrome

Generated images may include OS/platform chrome to communicate the intended device:

- iOS: reserve status-bar/notch or Dynamic Island space and bottom home-indicator space.
- WeChat mini-program: include the status bar and upper-right capsule unless the user requests a pure content canvas. Keep custom navigation and controls clear of the capsule.
- H5: include phone chrome only when a phone screenshot/mockup is requested.

Apply the same treatment across the image set. Do not invent exact system dimensions from a screenshot.

In runnable apps, use native safe-area APIs or CSS `env(safe-area-inset-*)`; let the platform draw its own status bar and capsule. WeChat implementations may use a `750rpx` design-width mapping. OS chrome is reference context, not a crop asset or app component.

## Phase 1 — Brief or source-set intake

For generation requests, collect product goals and core flows. Do not invent printing, delivery, payment, memberships, or unrelated pages unless the brief supports them.

For uploaded UI sets, inventory every supplied file first. Identify missing or unreadable images without pretending to have seen them. If the user already says the set is approved or explicitly authorizes analysis/cropping of that exact set, record that authorization and continue. Otherwise present an inventory/overview for confirmation before the post-approval work.

## Phase 2 — Homepage candidates

If no approved homepage exists, generate candidates with the native tool.

Suggested structured prompt:

```text
请为【{app_name}】生成首页界面图。
应用主体：{subject}
核心功能：{core_features}
平台类型：{platform}
参考视口与比例：{design_reference}
安全区与平台组件：{platform_requirements}
要求：首页有清晰的主要入口、核心功能和自然导航，呈现真实可用的产品界面。
```

Include optional style/device lines only when specified. Do not silently invent a style label.

Present candidates through the host's native image display. Ask the user to choose the visual master; prior explicit permission to auto-select may satisfy this homepage choice. This does **not** approve a later, unseen full page set.

Allowed work: images, prompts, candidate inventory and metadata. Do not write application code.

## Phase 3 — Page planning and generation

After homepage selection, infer the necessary pages if the user did not provide a list. Work from the actual core flow, normally around 4–8 core pages when appropriate, without adding filler.

Record page IDs, purpose, expected operations, and the distinction between pages, states, dialogs, and partial views.

Suggested page prompt, with the homepage attached as a real reference:

```text
请参考提供的【{app_name}】首页，为同一产品生成【{page_name}】页面。
页面用途：{purpose}
页面功能与文案：{requirements}
参考视口与比例：{design_reference}
安全区与平台组件：{platform_requirements}
延续首页的颜色、排版、组件、图标和导航语言；布局应服务本页用途。
```

Inspect outputs for unreadable copy, inconsistent styling, overlaps, missing controls and safe-area collisions. Fix obvious defects before requesting approval. Keep the actual source version available; do not overwrite an approved version with an unapproved revision.

## Phase 4 — Whole-set approval

Present all page images and their IDs. Ask once for confirmation of the **complete current set**, making the next step explicit: eight-part UI analysis and asset cropping.

If the user requests revisions, revise affected images, update their source IDs/versions, and obtain approval for the revised set. Homepage selection alone, silence, elapsed time, or a generated image's existence is not whole-set approval.

Record approval in `metadata/manifest.json` when possible: approved image IDs/versions, source files, actual pixel sizes, and the user's approval message or an equivalent explicit authorization. Do not fabricate approvals, hashes, paths or sizes.

## Phase 5 — Whole-set inspection and eight-part handoff

After approval, view every image at overview scale and inspect readable detail before writing individual-page analysis. Reuse the approved sources, not drafts.

Follow `references/ui-analysis.md` **in this exact output order**:

1. 一、整套 UI 概览
2. 二、逐页结构拆解
3. 三、公共组件与页面差异
4. 四、视觉规范提取
5. 五、交互与状态
6. 六、素材清单
7. 七、响应式与实现建议
8. 八、最终交付清单

Use real page IDs and visible elements. Required page table:

`页面｜区域｜组件｜内容｜布局与样式｜交互｜确认程度`

Required evidence labels: **明确可见、估算、推测、待确认、建议补充**. A row can have mixed labels, for example “内容明确可见；尺寸估算；跳转推测”. Keep observations and proposed improvements separate. Complete what is determinable first, then collect key unresolved questions.

Do not claim screenshot pixels are CSS pixels, infer exact fonts from appearance, or treat a visible button as proof of a backend/payment/business rule.

When file tools are available, save `analysis/ui-handoff.md`, `metadata/design-tokens.json`, `metadata/page-relations.json` and `metadata/asset-inventory.json`. Use the host's prescribed persistent storage; in existing Git projects use repository conventions. If file tools are absent, provide the handoff inline and clearly distinguish proposed filenames from saved files.

## Phase 6 — Analysis-led asset cropping

The asset inventory from section six determines what to crop. Read `references/asset-slicing.md`.

- Crop intrinsic imagery: photos, covers, illustrations, textures and special brand artwork.
- Rebuild editable text, cards, buttons, fields, counts, badges and navigation with components.
- Reuse matching icons from a consistent library where appropriate. Special illustrated/brand icons may need clean independent assets.
- Keep full-page crops only as reference pages or explicitly requested static reproductions.
- Check the exact source image version and pixel dimensions before measuring crop boxes.
- Exclude embedded UI text/chrome from reusable artwork. If impossible, mark “待原始素材” or edit a separate copy with the native image tool and label it as a derived asset.
- Do not claim that a rectangular crop removed a background or created genuine transparency.

Where a local source and Python/Pillow execution are available, use `scripts/crop_assets.py` with `metadata/crop-plan.json`. This script performs exact rectangular crops only; it does not generate or edit artwork. Read the exported crops, compare them to the source, and record review results.

If images exist only in the conversation and the host does not expose their bytes, request the required source files for cropping. Continue the available analysis meanwhile. Do not claim exported PNGs exist when they do not.

## Phase 7 — Optional implementation

Write application code only after the approved handoff/crops and an implementation request with a specified target stack. If the stack is missing, ask then; analysis and slices must not be blocked by that question.

Read `references/implementation-quality.md`. Preserve the source design language, build actual interactive components and data-driven repeated content, and use clean bitmap assets for intrinsic artwork.

Similar structure suggests reuse, but appearance alone does not establish the same behavior. Separate functionally different components where needed. Keep business rules and guessed interactions marked until specified.

Use full-page image-backed interaction overlays only when the user explicitly asks for that implementation strategy. “高保真” or “一模一样” alone does not mean flattening a runnable application into screenshots.

Preview at the measured reference viewport where possible. Verify the main flow, responsive behavior, safe areas, no overlaps, readable Chinese copy, missing assets and interactive controls. Report tests actually run and remaining limitations.

## Suggested output organization

```text
output/page-set/{slug}/
  source/                   # approved page references, preserving originals
  analysis/ui-handoff.md    # eight sections
  assets/                   # clean intrinsic artwork only
  metadata/
    manifest.json
    design-tokens.json
    page-relations.json
    asset-inventory.json
    crop-plan.json
    crop-results.json
  implementation/{stack}/   # only if requested
  screenshots/              # implementation verification if available
```

Use existing project conventions when applicable. Suggested paths are not evidence of saved files.

## Final checks

- Native generation uses no API key, endpoint, relay or invented tool parameters.
- Homepage selection and complete-set approval are distinct and recorded accurately.
- Every supplied/approved image has been inspected or listed as unavailable.
- Page/state/dialog IDs are consistent across the analysis, relations and assets.
- All eight sections are present and describe actual UI elements.
- Numeric estimates and inferred flows/business rules have explicit confidence labels.
- Design Tokens cover colors, type, spacing, radii, shadows, borders and component sizes, with evidence.
- Missing states/screens and proposed improvements are separate from visible facts.
- Every crop maps to a reviewed source version, valid bounds, page IDs and asset purpose.
- Text and controls remain editable in implementation; bitmap crops contain clean intrinsic artwork.
- Transparent assets are genuine, or their need is marked unresolved.
- Deliver only files that exist, report verification actually performed, and list key pending questions together.
