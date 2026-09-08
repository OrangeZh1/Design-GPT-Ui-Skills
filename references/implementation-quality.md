# Implementation Quality Reference

Read this reference only before Phase 7 implementation or when reviewing an implemented target stack.

## Standard

Build a high-fidelity visual rebuild of the approved page images. Recreate the visible UI with the selected stack's native/basic primitives, custom styles, real data-driven components for dynamic content, and clean cropped bitmap assets where useful. This is the original HTML-style approach: visual reconstruction first, component abstraction second.

Match the generated source image at the target viewport as closely as practical:

- layout positions and spacing
- colors and gradients
- typography scale and weight
- rounded corners and shadows
- icon style and imagery
- bottom navigation and page hierarchy

## Visual Rebuild Mode

Use visual rebuild mode by default unless the user explicitly asks for image-backed pages or exact pixel equality.

In visual rebuild mode:

- Rebuild visible layout, text, cards, controls, icons, and navigation using the selected stack.
- Render dynamic regions with real components bound to data arrays or mock data, not baked into screenshots.
- Crop only complex artwork, photos, illustrations, or textures that are better kept as bitmap assets.
- Avoid cropping UI text, badges, dates, counts, menus, tab bars, or status bars into bitmap assets when they should be editable or interactive.
- Tune layout against screenshots until the result is close to the generated image.
- Do not over-abstract components if abstraction makes the visual result worse.

This is different from generic business-component scaffolding. The goal is visual reproduction, not a clean design-system demo.

## Icon Fidelity

Do not replace real icons with text symbols or crude CSS shapes. Avoid using characters such as `★`, `♡`, `⚙`, `…`, `+`, or `>` as icon substitutes unless the source image clearly uses text-symbol icons.

Use one of these icon sources:

- SVG, iconfont, or an icon library that visually matches the generated image
- clean cropped icon assets from the generated image
- regenerated clean icon assets for special brand, AI, 3D, gradient, or illustrated icons
- hand-authored SVG when it can closely match the source icon

Icons may be cropped directly from generated images when that preserves fidelity, but crop them as clean reusable icon assets, not as part of larger UI screenshots.

Use CSS shapes only for simple decorative geometry such as dividers, dots, badge backgrounds, progress bars, and simple rounded containers. Do not use crude CSS circles, squares, or lines to replace meaningful app icons.

For icon-heavy pages, create `metadata/icon-inventory.json` when practical. Record each visible icon, its implementation source, asset path or library name, and status. No visible icon should be silently omitted.

## Target Stack Primitive Strategy

For every target stack, start from the stack's native/basic primitives and custom styling. Avoid default UI libraries or prebuilt components when their built-in design language would make the result drift from the generated image.

Examples:

- `html` / `h5`: use semantic/basic HTML elements, CSS, and clean bitmap assets; avoid CSS framework defaults unless restyled to match the image.
- `vue` / `react`: use plain components composed from basic DOM elements plus CSS; avoid importing component libraries by default.
- `uniapp`: use `view`, `text`, `image`, `scroll-view`, `input`, and `textarea`; use `view + @tap` for ordinary visual buttons, and reserve `button` for platform capabilities such as share, phone auth, or customer service.
- `taro` / `wechat-miniprogram`: use platform primitives such as `View`, `Text`, `Image`, `ScrollView`, `Input`, and `Textarea`; reserve platform-special components for capabilities that require them.

When a real capability is needed, use the target stack's official API or required component, but style the visible surface to match the generated page.

## Dynamic Content

Dynamic content must be implemented as real data-driven UI in the selected stack. This includes works/history lists, template grids, style lists, message feeds, result galleries, user collections, orders, comments, and any repeated item group.

Use mock data when no backend exists. Keep the initial mock data visually close to the generated image, but structure the implementation so item count, text, image, status, and actions can change.

Only crop the item's intrinsic artwork, cover image, avatar, product photo, illustration, or texture. Render item containers, labels, badges, dates, counts, buttons, menus, selected states, empty states, and loading states with real components.

## Image-Backed Exact Mode

Use image-backed exact mode only when the user requires "一模一样", "完全一致", "100%一致", "pixel-perfect", asks for a full-image background, or prioritizes zero visible differences over editable UI.

In image-backed exact mode:

- Use the normalized generated page image itself as the locked visual layer.
- Render it at the target design size without re-composing visible UI from components.
- Place transparent interactive layers above the image for taps, inputs, navigation, uploads, and mocked actions.
- Store hit-area coordinates in `metadata/interaction-map.json`.
- Do not claim the visible UI is component-rebuilt; it is an image-backed implementation with functional overlays.

For `750x1624` mini-program-style pages, render the image at `width: 750rpx; height: 1624rpx` or the selected stack's equivalent. Use absolute transparent hit areas in the same coordinate system.

## Interaction

Visible controls should not be decorative dead elements. Give buttons, tabs, cards, list items, upload areas, inputs, menus, filters, generate actions, share actions, and profile/settings entries a handler, route, or realistic mock behavior.

Create `metadata/interaction-map.json` for interactive targets when practical. Include each important clickable/input element and its handler or destination.

In image-backed exact mode, interaction-map entries should include the source page, x/y/width/height coordinates, action type, handler, and route or mock result.

## UniApp, Taro, And WeChat Mini Program

For `750x1624` deliverables, use `750rpx` design-width logic or the selected stack's equivalent.

Use platform-appropriate primitives, for example:

- `@tap` for tap handlers
- `navigator`, `uni.navigateTo`, or `uni.switchTab` for navigation
- form bindings for inputs
- `uni.chooseImage` or a mock upload state for upload areas
- mocked generation/result states where the UI implies generation

Make primary flows click-through with mock data: enter prompt, upload or choose image, pick style, start generation, view result, open work detail, and return.

Do not implement fake OS status bars. Use safe-area and platform layout rules instead.

## Verification

Run or preview the selected target stack when practical. Capture screenshots at the target viewport and compare them against the source images. Iterate until major layout, spacing, color, typography, rounded corners, shadows, icons, imagery, and navigation match closely.

For visual rebuild mode, compare the rendered screenshot against the source image and iterate on obvious visual differences. For image-backed exact mode, any visible difference inside the app page area is a defect unless it comes from unavoidable host preview chrome or user-approved platform safe-area handling.

Check for overlap, clipping, missing images, broken Chinese text, fake system chrome, and inert primary actions.
