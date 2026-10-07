# Native Image Generation Reference

## Tool selection and scope

Use the current session's built-in image-generation/editing tool. Do not call HTTP image APIs, relay providers, credential prompts, or credential environment variables. The skill cannot expose image generation in a client that does not already provide it.

Read the live tool schema. In ChatGPT Work Mode, the tool may be exposed as `image_gen.imagegen` or `tools.image_gen__imagegen`. Use the name and parameters actually available in the host. Do not pin an underlying model or promise API-specific sizes or batching.

`runtime.local.json` contains descriptive non-secret workflow defaults. It does not implement or activate a provider.

If generation is unavailable, explain that specific limitation. Analyze/crop existing uploaded images when possible; otherwise wait for usable input. Do not replace requested generated images with code-rendered UI.

## Prompt integrity

- Exact-prompt requests: pass the user's text unchanged.
- Structured briefs: build the prompt from the product, page purpose, copy and reference design; retain the final prompt in metadata when possible.
- Preserve the approved homepage's design language across pages.
- One independently usable image per page. Request variants as separate calls if the host has no variant parameter.
- Respect the live tool's instructions for generation, edits, reference images, display and persistence.

## Reference-image handling

Pass the homepage as actual image input for every secondary page.

For Work Mode's `imagegen` schema:

- Brand-new generation: omit both `referenced_image_paths` and `num_last_images_to_include`.
- Existing local sources: inspect them using the available image viewer before editing, and pass `referenced_image_paths` when all target sources have local paths.
- Conversation-only sources: use the smallest `num_last_images_to_include` that includes **every intended reference**, up to the tool's limit (currently 5 for this schema).
- Never provide both reference mechanisms.
- If the approved homepage falls outside the accessible recent images, use an available genuine local copy or ask the user to attach it again. Never use an unrelated recent page by mistake.
- Use `transparent_background: true` only for requested transparent/cutout assets; page screenshots normally use false. Preserve existing transparency on edits unless asked to change it.

These names apply to that schema, not every image tool. Re-read another host's schema rather than inventing matching parameters.

Example for a brand-new homepage in Work Mode code mode:

```javascript
// @exec: {"yield_time_ms": 120000, "max_output_tokens": 1000}
const result = await tools.image_gen__imagegen({
  prompt: "请为校园证件照微信小程序生成一张首页界面图，主入口清晰，保留微信顶部状态栏与胶囊安全区。",
  transparent_background: false
});
generatedImage(result);
```

For secondary pages, add the actual homepage reference using the correct mechanism. The above example is not a shell command or a standalone JavaScript API client.

If the execution call yields a running cell, resume using that host's prescribed wait mechanism. Do not dump full results or base64 image bytes into logs. Return the result through the native generated-image display helper.

## Dimensions and source preservation

`750x1624` may be the intended mini-program design reference; the native tool does not necessarily offer a precise size parameter. Include the intended viewport/aspect in structured prompts without promising exact output.

Measure actual image dimensions when bytes are accessible. Record unknown dimensions as “待确认”. Do not assume source image pixels equal device CSS pixels or `rpx`.

Present native image results using the host's image display and automatic persistence. Do not download/upload a generated image merely to show or save it. A local copy is appropriate when a separately requested deliverable, such as asset cropping, requires its pixels and the host allows access.

Keep original approved sources unchanged. Normalization is optional and must be explicit:

- Prefer analysis/cropping against the original image dimensions.
- Do not blindly center-crop a UI screenshot; it may remove navigation or controls.
- If exact delivery dimensions are requested, use host-approved processing only after inspecting the content. Preserve the original and record the transform.
- `scripts/normalize_image.py` is an optional legacy geometry utility, not a generation dependency. Its cover-crop mode may remove edges and its stretch mode distorts proportions. Do not apply either automatically.

## Clean derived assets

If artwork contains baked-in editable labels/badges, first seek the original clean asset. If a replacement is needed, use the native editing tool on a separate copy, preserving the approved page.

Suggested structured prompt:

```text
请从参考图中的【{asset_subject}】制作独立素材，保留其视觉风格。
仅保留素材本身，移除属于界面的文字、角标、日期、数字、菜单、状态栏和导航。
背景要求：{transparent_or_solid_background}
这是一张派生素材，不修改已确认的页面。
```

A replacement may differ from the source; label it “重新生成/编辑的派生素材，需核对”. Exact rectangular crops use the crop utility and preserve source pixels. Background removal and artwork edits use the native image tool, subject to its live instructions.
