---
name: generate-pages-from-homepage
description: Use when Codex needs to create a coherent multi-page mobile UI image set or implementation for an app, H5, website, or WeChat mini-program by first generating or using a homepage image as the visual master, handling mobile safe areas, iPhone status bars, WeChat mini-program capsules, then generating each page from the homepage reference and optionally implementing the result in HTML, H5, Vue, React, UniApp, Taro, or native WeChat mini-program. Trigger for requests like “生成一套移动端页面”, “生成苹果手机 UI”, “iPhone 17 Pro Max 页面”, “生成一套小程序页面”, “小程序胶囊要有”, “先生成首页再生成其它页面”, “首页作为母版生成套图”, “AI自己规划需要哪些页面”, “根据首页生成创作页/我的页/详情页”, “batch generate page images from a homepage reference”, “转成可运行项目”, or “turn the generated page images into code”.
---

# Generate Pages From Homepage

## Purpose

Create a complete UI page-set workflow:

1. Generate homepage candidates when no homepage image exists.
2. Let the user pick the homepage visual master.
3. Infer the product’s necessary pages if the user did not provide a page list.
4. Generate each page from the homepage reference.
5. Ask for the implementation target before writing code unless the user already specified it.
6. Implement in the selected target stack when requested.

The key principle: keep the prompt natural and parameterized. Do not over-specify design tokens unless the user asks for strict consistency checks.

Important order constraint: image generation comes before implementation. Do not create HTML/CSS/Vue/React/UniApp/Taro/mini-program files as a substitute for homepage candidates. Do not hand-code a homepage first and then use that code-rendered page as the visual master unless the user explicitly asks for code-first design.

## API Route And Prompt Integrity

If the user provides a specific model route, relay provider, base URL, endpoint, or model name, use that route exactly unless it cannot support the requested operation. Do not silently switch between a relay service, the official OpenAI endpoint, the built-in image tool, or a different model.

For example, if the user says to use a specific relay endpoint with `gpt-image-2`, keep using that relay route for image generation calls. If the workflow later needs image-reference/edit support and the relay endpoint does not support image input, stop and explain the limitation instead of quietly changing providers.

Do not store API keys, bearer tokens, relay credentials, or user secrets in `SKILL.md`. For local testing, use `runtime.local.json` for non-secret route defaults and store secrets in environment variables whenever possible.

If `runtime.local.json` exists beside `SKILL.md`, load it before image-generation calls. Supported fields:

```json
{
  "provider": "duomi",
  "base_url": "https://duomiapi.com",
  "create_endpoint": "/v1/images/generations",
  "poll_endpoint": "/v1/tasks/{id}",
  "async": true,
  "model": "gpt-image-2",
  "api_key_env": "DUOMI_API_KEY"
}
```

If `api_key_env` is set, read the API key from that environment variable. Do not print the key in logs or final responses.

Before calling image generation, read `references/image-generation.md` for route defaults, GPT Image 2 size constraints, relay request examples, and image normalization rules.

Use `scripts/normalize_image.py` to normalize raw generated images to exact delivery dimensions, for example `752x1632` raw/request images to `750x1624` deliverables.

Never secretly rewrite a prompt. Follow these rules:

- If the user says the prompt must be unchanged, send the exact prompt text as the image-generation prompt. Do not add template lines, quality words, style words, negative prompts, or hidden prompt augmentation.
- If this skill generates a prompt from structured user parameters, it may use the templates below, but report the final prompt or save it in metadata.
- If a prompt is modified for clarity, say that it was modified before the call when the user cares about prompt transparency.
- Keep the API payload, returned response, and final prompt metadata where practical so the user can audit what was sent.

## Inputs

Collect or infer these values:

- `app_name`: product/app name, for example `AI绘图微信小程序`.
- `subject`: what the app is about, for example `AI绘图工具`.
- `platform`: mini-program, mobile app, website, dashboard, landing page, etc.
- `core_features`: main things the product can do.
- `style`: optional user style words. If missing before homepage generation, let the homepage candidates explore freely instead of inventing a style label.
- `width` and `height`: requested delivery size. If missing and a homepage exists, use the homepage dimensions.
- `image_request_width` and `image_request_height`: image-generation request size after GPT Image 2 normalization. For WeChat mini-program `750x1624`, request `752x1632` and normalize the downloaded image to `750x1624`.
- `device_preset`: optional target device, for example `iPhone 17 Pro Max`, `iPhone Pro Max`, `WeChat mini-program`, or `generic mobile`.
- `platform_chrome`: whether generated page images should show OS/platform chrome such as iOS status bar or WeChat capsule. For mobile UI image sets, default to `visible`; for runnable implementation, default to the target platform's native chrome.
- `safe_area_policy`: optional; default to reserving realistic top and bottom safe areas for mobile pages.
- `homepage_image`: optional approved homepage image used as the visual reference.
- `page_count` or `page_list`: optional; if missing, infer the complete page set.
- `page_requirements`: optional per-page modules, actions, copy, and constraints.
- `output_target`: optional target artifact, for example `image-set`, `html`, `h5`, `vue`, `react`, `uniapp`, `taro`, or `wechat-miniprogram`.

Ask only when a missing value blocks safe execution. Otherwise infer conservatively from the homepage image and user request.

For WeChat mini-program workflows, default to delivery size `750x1624` when the user does not specify size. Because GPT Image 2 requires multiples of 16, request `752x1632`, then crop or resize the downloaded image to `750x1624`. Generated mini-program page images should include the WeChat status bar and top-right capsule unless the user asks for a pure content canvas. Later implementation in the selected target stack should use a `750rpx` design-width mapping or the equivalent pattern for that stack.

For iPhone mobile app workflows, if the user asks for `iPhone 17 Pro Max` or an Apple Pro Max mobile UI and does not provide an exact size, use a Pro Max portrait canvas and clearly record the chosen delivery size in metadata. If the image route has strict size constraints, choose the nearest supported portrait size, then normalize or document the actual output. Generated iPhone page images should include a realistic iOS status bar and reserve the top safe area; do not place app titles, back buttons, search bars, or primary actions under the status bar or Dynamic Island area.

If the user asks for a usable project or implementation, ask which target technology stack to use before building unless the user already specified one. Do not assume HTML, UniApp, H5, Vue, React, Taro, or native WeChat mini-program by default.

If `output_target` is missing, the default deliverable is `image-set` only. Do not proceed to HTML/CSS or any runnable code implementation without an explicit target stack.

If the user asks to generate homepage candidates, call the configured image generation route for the candidates. If image generation is unavailable or the configured relay cannot perform the requested generation, stop and explain the blocker. Do not fall back to building a code mockup.

## Mobile Safe Areas And Platform Chrome

For mobile UI image generation, distinguish between image deliverables and runnable implementation:

- `image-set` deliverables should look like real phone screenshots or design mockups. Include platform chrome when the platform implies it.
- Runnable target-stack implementations should not hard-code fake OS chrome inside app content unless the user explicitly wants a screenshot simulator or static visual rebuild. Use native safe-area APIs, CSS env variables, `rpx`, or framework conventions instead.

Default chrome rules:

- iOS app / iPhone Pro Max / iPhone 17 Pro Max: show a clean iOS status bar in generated page images. Reserve top safe area for the status bar and Dynamic Island/notch region, then place the app navigation/header below it. Reserve bottom safe area for home indicator spacing when the page has bottom tabs or fixed bottom actions.
- WeChat mini-program: show the status bar and top-right capsule in generated page images. Reserve enough top space so the custom navigation title, back/home buttons, search field, or page actions do not collide with the capsule. Keep tappable controls away from the capsule hit area.
- Generic mobile H5/app: include a status bar only when the user asks for a phone screenshot/mockup. Otherwise reserve safe top spacing only if the visual style needs a native-app frame.

Safe-area prompt requirements for generated images:

- Keep all important UI inside the safe content area.
- Top status/capsule area must not overlap text, icons, search boxes, tabs, banners, or cards.
- Fixed bottom tab bars and bottom CTA buttons must sit above the home indicator safe area.
- If using a custom navigation bar, make it visually separate from the status/capsule area.
- Apply the same safe-area and platform-chrome treatment to homepage and all secondary pages.

When creating prompts, add one short line such as:

```text
移动端安全区：生成真实手机截图效果，保留顶部状态栏安全区和底部 Home Indicator 安全区，页面内容不得与系统状态栏重叠。
```

For WeChat mini-program prompts, add:

```text
小程序顶部规范：包含微信状态栏和右上角胶囊按钮，导航标题和页面操作需避开胶囊区域。
```

For iPhone Pro Max prompts, add:

```text
iPhone 顶部规范：包含真实 iOS 状态栏，顶部内容避开 Dynamic Island/状态栏区域，底部固定操作避开 Home Indicator。
```

## Homepage First

If the user has not provided an approved homepage image, generate homepage candidates first. Do not generate the rest of the page set until the user selects a homepage, unless they explicitly ask for fully automatic generation.

Homepage candidates are generated images, not hand-built HTML screenshots. In this phase, only create image files, prompt/response metadata, lightweight manifests needed to track candidates, and normalized image copies.

Use this homepage prompt shape:

```text
请为【{app_name}】生成首页界面图。

应用主体：{subject}
核心功能：{core_features}
目标风格：{style}
平台类型：{platform}
设备规范：{device_preset}
尺寸：{width}x{height}
安全区与平台组件：{safe_area_and_platform_chrome_requirements}

要求首页像一个真实可用的产品首页，有清晰的主入口、核心功能展示和自然的导航结构。
```

If `style` is omitted for homepage generation, remove the `目标风格` line rather than filling it with generic words such as “高级”, “轻科技”, or “现代简洁”. If `device_preset` is omitted, remove the `设备规范` line. Always keep the `安全区与平台组件` line for mobile app, H5 phone mockup, and mini-program image generation. Generate several homepage candidates when the user wants exploration. Use one image per candidate or `n` variants for the same homepage prompt, depending on the API path.

If the delivery size is `750x1624`, request `752x1632` from GPT Image 2 and normalize the returned candidate to `750x1624` before showing it to the user.

If the user explicitly provides an exact prompt for homepage generation and asks for no changes, send that prompt exactly.

## Infer Needed Pages

If the user does not name the pages, infer a useful complete product page set. Think from user goals and product flows, not from generic templates.

Create a manifest before generating secondary pages:

```json
{
  "app_name": "...",
  "subject": "...",
  "platform": "...",
  "device_preset": "iPhone 17 Pro Max",
  "platform_chrome": "visible",
  "safe_area_policy": "reserve top status/capsule area and bottom home indicator area",
  "delivery_size": "750x1624",
  "image_request_size": "752x1632",
  "homepage_image": "...",
  "pages": [
    {
      "page_name": "图生图创作",
      "purpose": "让用户上传图片并输入修改需求",
      "page_requirements": "上传图片、输入修改要求、选择风格、开始生成",
      "priority": "core"
    }
  ]
}
```

Page selection heuristics:

- Include pages required to complete the product’s primary workflow.
- For creator tools, consider creation/input, style/template selection, generation progress/result, works/history, detail/share, and profile/settings.
- For commerce, consider home, category/listing, product detail, cart, checkout, order, and profile.
- For dashboards, consider overview, list/table, detail, create/edit, settings, and account.
- Prefer 4-8 core pages for a normal page set unless the user gives a different count.
- Avoid generating pages that do not serve a real workflow just to fill a quota.

## Reference Page Prompt Template

After the homepage is approved, use this compact template for each target page:

```text
这是一张【{app_name}】的首页。请参考这张首页，为【{app_name}】生成【{page_name}】页面。

应用主体：{subject}
页面功能：{page_requirements}
目标风格：{style}
设备规范：{device_preset}
尺寸：{width}x{height}
安全区与平台组件：{safe_area_and_platform_chrome_requirements}

要求页面像同一个小程序里的新页面，而不是复制首页。
```

Adapt wording naturally:

- If the product is not a mini-program, replace `小程序` with `应用`, `网站`, `后台`, or the user’s platform.
- If `style` is omitted for reference-page generation, use `目标风格：延续首页观感`.
- If `device_preset` is omitted, remove the `设备规范` line, but keep safe-area/platform-chrome requirements for mobile image generation.
- If the user gives exact text that must appear in the image, include it in `页面功能` or an extra short `页面文案` line.
- If the user explicitly says not to modify a prompt, send their prompt exactly and do not use this template.

## Phase Gates

Follow these phases strictly. Do not skip a gate unless the user explicitly asks for full automation and provides the missing decision.

### Phase 1: Collect Inputs

Collect or infer app parameters, delivery size, device preset, platform chrome, safe-area policy, and route configuration. For WeChat mini-program requests, default to delivery size `750x1624` and image request size `752x1632`.

Allowed outputs: notes, planned prompt text, metadata paths.

Forbidden outputs: generated implementation files.

### Phase 2: Generate Homepage Candidates

Generate homepage candidate images using the configured image generation route. Read `references/image-generation.md` before the call. Save raw responses, raw images when available, and normalized delivery-size candidates.

When the image request size differs from delivery size, normalize each returned candidate with `scripts/normalize_image.py` before presenting it for selection.

Allowed outputs: homepage candidate images, prompt/response metadata, candidate manifest including device preset, platform chrome, and safe-area policy.

Forbidden outputs: page-set manifest for secondary pages, HTML/CSS, framework files, hand-coded homepage screenshots, or any target-stack implementation.

Mandatory stop: after homepage candidates are generated, stop and ask the user to choose the homepage visual master. Do not infer secondary pages and do not generate other pages before the user selects a homepage, unless the user explicitly requested fully automatic selection.

### Phase 3: User Selects Homepage

Wait for the user to select one homepage candidate, or use the exact homepage image they provided. If the user has not selected a homepage and did not authorize auto-selection, do not continue.

Allowed outputs: selected homepage path and short confirmation.

Forbidden outputs: generated secondary page images or implementation files.

### Phase 4: Infer Page Manifest

After homepage selection, infer the complete product page set if the user did not provide one. Create or update the manifest with delivery size, image request size, device preset, platform chrome, safe-area policy, selected homepage, pages, page purpose, and page requirements.

Allowed outputs: manifest JSON and explanation of the inferred pages.

Forbidden outputs: implementation files.

### Phase 5: Generate Page Images

Generate one independent image per target page while passing the selected homepage as the visual reference when the API route supports image input. Normalize returned images to delivery size.

When the image request size differs from delivery size, keep the raw returned image and normalize a delivery copy with `scripts/normalize_image.py`.

Allowed outputs: page images, prompt/response metadata, updated manifest.

Forbidden outputs: implementation files.

Stop after this phase if `output_target` is missing.

### Phase 6: Ask Target Stack

If the user wants implementation and `output_target` is missing, ask which target technology stack to use. Do not default to HTML.

Ask:

```text
你希望最终实现成哪种技术栈？例如：静态 HTML、H5、Vue、React、UniApp、Taro、原生微信小程序。你也可以选择只生成图片套图。
```

### Phase 7: Implement Selected Target Stack

Only this phase may write `.html`, `.css`, `.vue`, `.jsx`, `.tsx`, `pages.json`, mini-program page files, framework scaffolds, route files, components, mock data, and target-stack assets.

For true product workflows, prefer multiple independent page requests or Batch jobs over a single collage image. Use `n` only for variants of the same page.

## Implementation Target Workflow

Before this section, confirm `output_target`. If it is not specified, ask the user:

```text
你希望最终实现成哪种技术栈？例如：静态 HTML、H5、Vue、React、UniApp、Taro、原生微信小程序。你也可以选择只生成图片套图。
```

Use the generated images as visual references, but choose the build strategy from the selected target technology stack:

- `image-set`: generate only the page images and metadata.
- `html`: create a high-fidelity visual rebuild from the generated images using HTML/CSS plus clean cropped assets.
- `h5`, `vue`, `react`, `uniapp`, `taro`, `wechat-miniprogram`: create a runnable high-fidelity visual rebuild in the selected stack with pages, routes/config, mock data, and behavior appropriate to that stack.

Default implementation standard: build a high-fidelity visual rebuild like the original HTML approach: recreate the visible UI with the selected stack's native/basic primitives, custom styles, text, icons, and clean cropped visual assets; render dynamic content with real data-driven components; then add real interactions where the UI implies behavior.

Do not treat this as generic business-component scaffolding or default UI-library assembly. Visual fidelity comes before abstraction. Use full-page image-backed implementation only when the user explicitly requires exact pixel equality or asks for image-backed pages.

Before Phase 7 implementation, read `references/implementation-quality.md` for stack-specific fidelity, interaction, screenshot, and verification guidance.

## Image-To-Selected-Stack Recreation Workflow

When converting a generated page image into the selected target stack:

1. Visually decompose the page into structure: header, navigation, cards, buttons, lists, media, tab bar, modals, repeated modules, and artwork.
2. Rebuild visible layout, text, cards, controls, icons, and navigation with the selected stack's layout/style system.
3. Render dynamic content such as lists, grids, feeds, histories, templates, works, messages, and repeated items with real components and mock/data arrays.
4. Crop complex illustrations, thumbnails, product photos, or decorative art into `assets/` only when they should remain bitmap artwork.
5. Preserve UTF-8 in all source files; for HTML outputs, include `<meta charset="UTF-8">`.
6. Keep shared visual patterns, behavior, navigation, and mock data consistent across pages.
7. Render, screenshot, compare with the source image, and iterate on obvious mismatches when practical.

## Asset And Text Separation

Before cropping image assets from generated pages, inspect whether the crop already contains UI text, badges, dates, icons, like counts, status bars, tab bars, or other overlay chrome.

- If the overlay should be editable target-stack component text, do not crop it into the image asset.
- If a clean crop is impossible because the generated image baked text/icons into the artwork, regenerate or edit that small asset as a clean image instead of stacking new HTML text on top of dirty pixels.
- For repeated media cards, prefer clean artwork assets plus component-rendered badges, dates, counts, and menus.
- For generated mobile UI images, include platform chrome when the prompt/manifest requires it: iOS status bar for iPhone mockups, WeChat status bar plus capsule for mini-program mockups. For runnable target-stack implementations, do not hard-code fake OS status bars unless the user explicitly wants a static screenshot simulator. Let the real device, browser preview frame, WeChat Developer Tools, or host platform provide status bars, and implement only the app's own navigation/header plus safe-area spacing.
- For runnable target stacks, use the stack-appropriate responsive layout constraints: for example `rpx` and safe-area handling in mini-program/UniApp targets, or `%`, `fr`, flex/grid, and viewport units in web targets. Fixed pixel canvases are acceptable only when the user explicitly asks for static screenshot reproduction.

## File Organization

Prefer this structure for multi-page work:

```text
output/page-set/{slug}/
  source/
    homepage-candidate-1-raw.png
    homepage-candidate-1.png
    homepage.png
    page-name.png
  implementation/{output_target}/
    ...
  screenshots/
    page-name.png
  metadata/
    manifest.json
    page-name-response.json
```

If working inside an existing repo, follow its asset and page conventions instead.

## Quality Checks

Before final delivery:

- Verify a homepage visual master was selected or state that automatic selection was used.
- Verify the inferred page set covers the core product workflow.
- Verify every generated page has the requested size or document the actual returned size.
- Verify mobile image pages reserve the correct top and bottom safe areas for the target device.
- Verify iPhone image pages include an iOS status bar when requested and no content collides with the status bar, Dynamic Island area, or home indicator.
- Verify WeChat mini-program image pages include the status bar and top-right capsule when requested and no navigation/search/action controls collide with the capsule.
- Check that each page looks like the same app, not a copied homepage.
- Check visible required modules and key text.
- Check that icons are not missing and are not replaced with text symbols or crude CSS shapes.
- For selected target-stack implementations, follow `references/implementation-quality.md` and verify visual fidelity mode, primary interactions, screenshots, and platform-specific preview behavior when practical.
- Verify no major overlap, clipping, missing images, broken Chinese text, unwanted hard-coded system chrome in runnable implementations, or inert primary actions.
- Report saved paths for images, implementation files, screenshots, and metadata.
