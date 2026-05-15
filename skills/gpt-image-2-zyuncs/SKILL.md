---
name: gpt-image-2-zyuncs
description: Generate/edit images with gpt-image-2-zyuncs (powered by GPT Image 2 via Zyuncs proxy, OpenAI Images API). Use for image create/modify requests incl. edits. Supports text-to-image + image editing via extra_body.images; use --input-image for edits.
---

# Cortex-19 (Zyuncs) Image Generation & Editing

- **Underlying model**: GPT Image 2 (OpenAI)
- **Proxy service**: Zyuncs (`llm.api.zyuncs.com`), OpenAI Images API
- **Model identifier**: `cortex-19`

Generate new images or edit existing ones via the Zyuncs proxy service, which forwards requests to the GPT Image 2 model. The API uses the OpenAI Images API endpoint (`/v1/images/generations`). Image editing is achieved by passing input images through the `extra_body.images` parameter (Apifox 透传参数).

**重要限制**: cortex-19 **不支持** images.edit 端点（返回 "access deny"），**不支持** chat.completions 端点（返回 502），**不支持**透明背景。图片编辑通过 `extra_body.images` 实现。

## Usage

Run the script using absolute path (do NOT cd to skill directory first):

**Generate new image:**
```bash
uv run ~/.claude/skills/gpt-image-2-zyuncs/scripts/generate_image.py --prompt "your image description" --filename "output-name.png" [选项]
```

**Edit existing image:**
```bash
uv run ~/.claude/skills/gpt-image-2-zyuncs/scripts/generate_image.py --prompt "editing instructions" --filename "output-name.png" --input-image "path/to/input.png" [选项]
```

**Options:**
- `--input-image / -i`: 输入图片路径，用于图片编辑（通过 `extra_body.images` 传递给 API）
- `--size / -s`: 图片尺寸，可选 `1024x1024` | `1024x1536` | `1536x1024`（默认 `1024x1024`）
- `--quality / -q`: 图片质量，可选 `low` | `medium` | `high` | `auto`（默认 `auto`）
- `--output-format / -of`: 输出格式，可选 `png` | `jpeg`（默认 `png`）
- `--n / -n`: 生成图片数量，可选 `1` | `2`（默认 `1`）
- `--api-key / -k`: API Key（覆盖 ZYUNCS_API_KEY 环境变量）

**Important:** Always run from the user's current working directory so images are saved where the user is working, not in the skill directory.

## Default Workflow (draft → iterate → final)

Goal: fast iteration to get the prompt right.

- Draft: quick feedback loop
  - `uv run ~/.claude/skills/gpt-image-2-zyuncs/scripts/generate_image.py --prompt "<draft prompt>" --filename "yyyy-mm-dd-hh-mm-ss-draft.png"`
- Iterate: adjust prompt in small diffs; keep filename new per run
- Final: when prompt is locked
  - `uv run ~/.claude/skills/gpt-image-2-zyuncs/scripts/generate_image.py --prompt "<final prompt>" --filename "yyyy-mm-dd-hh-mm-ss-final.png" --quality high`

## API Key

The script checks for API key in this order:
1. `--api-key` argument (use if user provided key in chat)
2. `ZYUNCS_API_KEY` environment variable

If none is available, the script exits with an error message.

## API Base URL

The default API base URL is `https://llm.api.zyuncs.com/v1`. Override it by setting the `ZYUNCS_API_BASE_URL` environment variable.

## Preflight + Common Failures (fast fixes)

- Preflight:
  - `command -v uv` (must exist)
  - `test -n "$ZYUNCS_API_KEY"` (or pass `--api-key`)
  - If editing: `test -f "path/to/input.png"`

- Common failures:
  - `Error: No API key provided.` → set `ZYUNCS_API_KEY` or pass `--api-key`
  - "502 / upstream_error" → cortex-19 不支持 chat.completions 端点，请确保使用 images.generate
  - "Unknown parameter: 'response_format'" → cortex-19 不支持 response_format 参数，已移除
  - "Transparent background is not supported" → cortex-19 不支持透明背景，移除 background=transparent
  - "Invalid value: 'hd'" → quality 参数只支持 low/medium/high/auto，不支持 standard/hd
  - "access deny / Unauthorized host" → images.edit 端点不可用，请使用 --input-image（通过 extra_body.images 编辑）
  - "Error loading input image:" → 输入图片路径错误，检查 --input-image 指向的文件是否存在
  - Empty response with no image → the model occasionally fails to generate; retry the request

## Supported Parameters

| 参数 | 可选值 | 默认值 | 说明 |
|------|--------|--------|------|
| `prompt` | 任意文本 | (必选) | 图片描述或编辑指令 |
| `input_image` | 文件路径 | (可选) | 输入图片，用于编辑（通过 extra_body.images 传递） |
| `size` | 1024x1024, 1024x1536, 1536x1024 | 1024x1024 | 图片尺寸 |
| `quality` | low, medium, high, auto | auto | 图片质量 |
| `output_format` | png, jpeg | png | 输出格式 |
| `n` | 1, 2 | 1 | 生成图片数量 |

**不支持的功能：**
- images.edit 端点（使用 `--input-image` 通过 `extra_body.images` 代替）
- chat.completions 端点
- 透明背景（background=transparent）
- response_format 参数
- webp 输出格式

## Filename Generation

Generate filenames with the pattern: `yyyy-mm-dd-hh-mm-ss-name.png`

**Format:** `{timestamp}-{descriptive-name}.png`
- Timestamp: Current date/time in format `yyyy-mm-dd-hh-mm-ss` (24-hour format)
- Name: Descriptive lowercase text with hyphens
- Keep the descriptive part concise (1-5 words typically)
- Use context from user's prompt or conversation
- If unclear, use random identifier (e.g., `x9k2`, `a7b3`)

Examples:
- Prompt "A serene Japanese garden" → `2026-05-15-14-23-05-japanese-garden.png`
- Prompt "sunset over mountains" → `2026-05-15-15-30-12-sunset-mountains.png`

## Prompt Handling

**For generation:** Pass user's image description as-is to `--prompt`. Only rework if clearly insufficient.

**For editing:** Pass editing instructions in `--prompt` (e.g., "add a rainbow in the sky", "make it look like a watercolor painting")

Preserve user's creative intent in both cases.

## Image Editing

When the user wants to modify an existing image:
1. Check if they provide an image path or reference an image in the current directory
2. Use `--input-image` parameter with the path to the image
3. The prompt should contain editing instructions (e.g., "make the sky more dramatic", "remove the person", "change to cartoon style")
4. Common editing tasks: add/remove elements, change style, adjust colors, blur background, etc.
5. Editing is implemented via `extra_body.images` parameter (Apifox 透传参数)

## Prompt Templates (high hit-rate)

Use templates when the user is vague or when edits must be precise.

- Generation template:
  - "Create an image of: <subject>. Style: <style>. Composition: <camera/shot>. Lighting: <lighting>. Background: <background>. Color palette: <palette>. Avoid: <list>."

- Editing template (preserve everything else):
  - "Change ONLY: <single change>. Keep identical: subject, composition/crop, pose, lighting, color palette, background, text, and overall style. Do not add new objects. If text exists, keep it unchanged."

## Output

- Saves to current directory (or specified path if filename includes directory)
- Script outputs the full path to each generated image
- **Do not read the image back** - just inform the user of the saved path

## Examples

**Generate new image (default quality):**
```bash
uv run ~/.claude/skills/gpt-image-2-zyuncs/scripts/generate_image.py --prompt "A serene Japanese garden with cherry blossoms" --filename "2026-05-15-14-23-05-japanese-garden.png"
```

**Generate with high quality:**
```bash
uv run ~/.claude/skills/gpt-image-2-zyuncs/scripts/generate_image.py --prompt "A photorealistic mountain landscape" --filename "2026-05-15-14-25-30-mountain.png" --quality high
```

**Generate portrait orientation:**
```bash
uv run ~/.claude/skills/gpt-image-2-zyuncs/scripts/generate_image.py --prompt "A tall lighthouse by the sea" --filename "2026-05-15-14-27-00-lighthouse.png" --size 1024x1536
```

**Generate two images:**
```bash
uv run ~/.claude/skills/gpt-image-2-zyuncs/scripts/generate_image.py --prompt "A colorful abstract pattern" --filename "2026-05-15-14-28-00-abstract.png" --n 2
```

**Edit existing image:**
```bash
uv run ~/.claude/skills/gpt-image-2-zyuncs/scripts/generate_image.py --prompt "make the sky more dramatic with storm clouds" --filename "2026-05-15-14-30-00-dramatic-sky.png" --input-image "original-photo.jpg"
```