# Image Generation Reference

Use this reference before calling image generation for this skill. Do not re-search basic GPT Image 2 size rules unless the user asks for current official confirmation or the API behavior appears to differ.

## Route Defaults

If `runtime.local.json` exists beside `SKILL.md`, load it for local test defaults:

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

Read the API key from `api_key_env`. Never print or save the key in logs, prompts, responses, manifests, or final answers.

If the user gives a different route/model/key for the current task, that user-provided route overrides `runtime.local.json`.

## Prompt Integrity

There are two prompt modes:

1. **Exact prompt mode**: if the user says the prompt must be unchanged, send the exact text. Do not add template text, style words, negative prompts, dimensions, or quality hints unless those are already in the user's prompt.
2. **Structured workflow mode**: if the user gives product parameters, build the prompt from the skill template. Save the final prompt in metadata and report it when relevant.

## GPT Image 2 Size Rules

For direct GPT Image 2 size control, requested image dimensions must satisfy:

- max edge `<= 3840px`
- both width and height are multiples of `16`
- long-to-short ratio `<= 3:1`
- total pixels between `655,360` and `8,294,400`

Popular valid sizes:

- `1024x1024`
- `1536x1024`
- `1024x1536`
- `2048x2048`
- `2048x1152`
- `3840x2160`
- `2160x3840`
- `auto`

Also supports aspect ratio format: `1:1`, `3:2`, `2:3`, `auto`.

## WeChat Mini Program Size Policy

For a WeChat mini-program design target of `750x1624`:

1. Use image request size `752x1632` because GPT Image 2 requires multiples of 16.
2. After download, normalize the image to delivery size `750x1624` by center-cropping or resizing.
3. Save both raw and normalized images when practical:
   - `homepage-candidate-1-raw.png`
   - `homepage-candidate-1.png`
4. Prefer the bundled script:

```bash
python scripts/normalize_image.py --input homepage-candidate-1-raw.png --out homepage-candidate-1.png --size 750x1624
```

5. Later implementation in the selected target stack should treat the design width as `750rpx` or equivalent. Do not hard-code fake phone status bars.

If the relay endpoint ignores size or returns another size, still normalize to the requested delivery size and document the raw returned size.

## Async API Flow (Duomi)

The Duomi API currently only supports async image generation. The flow is:

### Step 1: Create Task

`POST {base_url}/v1/images/generations?async=true`

Headers:

```
Authorization: {api_key}
Content-Type: application/json
```

Body:

```json
{
  "model": "gpt-image-2",
  "prompt": "FINAL_PROMPT_HERE",
  "size": "752x1632",
  "quality": "medium"
}
```

Fields:

- `model` (required): model name, currently supports `gpt-image-2`
- `prompt` (required): text description, max 5000 characters
- `size` (optional): `widthxheight` (both must be multiples of 16), or ratio format `1:1`/`3:2`/`2:3`/`auto`
- `image` (optional): reference image URL, single string or array of strings
- `quality` (optional): `low`/`medium`/`high`

Response contains a task ID. Parse `id` from the response.

### Step 2: Poll Task Result

`GET {base_url}/v1/tasks/{id}`

Headers:

```
Authorization: {api_key}
```

Poll until the task status indicates completion. When complete, the response will contain image URLs in the result data.

### Step 3: Download and Normalize

Download the image from the returned URL, save the raw image, then normalize to delivery size if needed.

## Homepage Candidate Request Example

Structured prompt example:

```text
请为【AI绘图微信小程序】生成首页界面图。

应用主体：AI绘图工具
核心功能：文生图、图生图、换风格
平台类型：微信小程序
尺寸：750x1624

要求首页像一个真实可用的产品首页，有清晰的主入口、核心功能展示和自然的导航结构。
```

API request size for this example: `752x1632`.
Delivery size after normalization: `750x1624`.

## Image Reference Support

When the API supports the `image` field and a homepage reference image is available, pass the homepage image URL in the `image` field for secondary page generation:

```json
{
  "model": "gpt-image-2",
  "prompt": "PAGE_PROMPT_HERE",
  "size": "752x1632",
  "image": "https://example.com/homepage-reference.png"
}
```

Multiple reference images can be passed as an array.

## Clean Asset Regeneration Prompt

When a cropped asset contains baked-in UI chrome, regenerate a clean asset:

```text
只生成一张纯图片素材，不要任何文字、角标、日期、爱心、数字、菜单点、状态栏、底部导航或 UI 覆盖元素。
主题：{asset_subject}
风格：与首页母版保持一致
尺寸：{asset_width}x{asset_height}
```

Use component code for badges, counts, dates, menus, labels, tab bars, and headers.
