---
name: nano-banana-pro-zyuncs
description: Generate/edit images with nano-banana-pro-zyuncs (powered by Gemini 3.1 Flash Image via Zyuncs proxy, OpenAI-compatible API). Use for image create/modify requests incl. edits. Supports text-to-image + image-to-image editing; use --input-image for edits.
---

# Nano Banana Pro (Zyuncs) Image Generation & Editing

- **Underlying model**: Gemini 3.1 Flash Image (Google)
- **Proxy service**: Zyuncs (`llm.api.zyuncs.com`), OpenAI-compatible API
- **Model identifier**: `lyra-flash-12`

Generate new images or edit existing ones via the Zyuncs proxy service, which forwards requests to the Gemini 3.1 Flash Image model. The API is OpenAI-compatible, so the script uses the OpenAI Python SDK as its client.

## Usage

Run the script using absolute path (do NOT cd to skill directory first):

**Generate new image:**
```bash
uv run ~/.claude/skills/zyuncs-lyra-flash-1.0.0/scripts/generate_image.py --prompt "your image description" --filename "output-name.png" [--api-key KEY]
```

**Edit existing image:**
```bash
uv run ~/.claude/skills/zyuncs-lyra-flash-1.0.0/scripts/generate_image.py --prompt "editing instructions" --filename "output-name.png" --input-image "path/to/input.png" [--api-key KEY]
```

**Important:** Always run from the user's current working directory so images are saved where the user is working, not in the skill directory.

## Default Workflow (draft → iterate → final)

Goal: fast iteration to get the prompt right.

- Draft: quick feedback loop
  - `uv run ~/.claude/skills/zyuncs-lyra-flash-1.0.0/scripts/generate_image.py --prompt "<draft prompt>" --filename "yyyy-mm-dd-hh-mm-ss-draft.png"`
- Iterate: adjust prompt in small diffs; keep filename new per run
  - If editing: keep the same `--input-image` for every iteration until you're happy.
- Final: when prompt is locked
  - `uv run ~/.claude/skills/zyuncs-lyra-flash-1.0.0/scripts/generate_image.py --prompt "<final prompt>" --filename "yyyy-mm-dd-hh-mm-ss-final.png"`

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
  - `Error loading input image:` → wrong path / unreadable file; verify `--input-image` points to a real image
  - "quota/permission/403" style API errors → wrong key, no access, or quota exceeded; try a different key/account
  - Empty response with no image → the model occasionally fails to generate an image; retry the request

## Filename Generation

Generate filenames with the pattern: `yyyy-mm-dd-hh-mm-ss-name.png`

**Format:** `{timestamp}-{descriptive-name}.png`
- Timestamp: Current date/time in format `yyyy-mm-dd-hh-mm-ss` (24-hour format)
- Name: Descriptive lowercase text with hyphens
- Keep the descriptive part concise (1-5 words typically)
- Use context from user's prompt or conversation
- If unclear, use random identifier (e.g., `x9k2`, `a7b3`)

Examples:
- Prompt "A serene Japanese garden" → `2026-03-13-14-23-05-japanese-garden.png`
- Prompt "sunset over mountains" → `2026-03-13-15-30-12-sunset-mountains.png`
- Prompt "create an image of a robot" → `2026-03-13-16-45-33-robot.png`
- Unclear context → `2026-03-13-17-12-48-x9k2.png`

## Image Editing

When the user wants to modify an existing image:
1. Check if they provide an image path or reference an image in the current directory
2. Use `--input-image` parameter with the path to the image
3. The prompt should contain editing instructions (e.g., "make the sky more dramatic", "remove the person", "change to cartoon style")
4. Common editing tasks: add/remove elements, change style, adjust colors, blur background, etc.

## Prompt Handling

**For generation:** Pass user's image description as-is to `--prompt`. Only rework if clearly insufficient.

**For editing:** Pass editing instructions in `--prompt` (e.g., "add a rainbow in the sky", "make it look like a watercolor painting")

Preserve user's creative intent in both cases.

## Prompt Templates (high hit-rate)

Use templates when the user is vague or when edits must be precise.

- Generation template:
  - "Create an image of: <subject>. Style: <style>. Composition: <camera/shot>. Lighting: <lighting>. Background: <background>. Color palette: <palette>. Avoid: <list>."

- Editing template (preserve everything else):
  - "Change ONLY: <single change>. Keep identical: subject, composition/crop, pose, lighting, color palette, background, text, and overall style. Do not add new objects. If text exists, keep it unchanged."

## Output

- Saves PNG to current directory (or specified path if filename includes directory)
- Script outputs the full path to the generated image
- **Do not read the image back** - just inform the user of the saved path

## Examples

**Generate new image:**
```bash
uv run ~/.claude/skills/zyuncs-lyra-flash-1.0.0/scripts/generate_image.py --prompt "A serene Japanese garden with cherry blossoms" --filename "2026-03-13-14-23-05-japanese-garden.png"
```

**Edit existing image:**
```bash
uv run ~/.claude/skills/zyuncs-lyra-flash-1.0.0/scripts/generate_image.py --prompt "make the sky more dramatic with storm clouds" --filename "2026-03-13-14-25-30-dramatic-sky.png" --input-image "original-photo.jpg"
```
