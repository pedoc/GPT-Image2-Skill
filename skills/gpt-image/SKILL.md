---
name: gpt-image
description: "Generate or edit images with GPT Image 2 or 2.5 through the bundled uv script, saved image-service connection, and Reference Gallery. Use for image requests including imprecise 'GPT 2.5' model names, posters, typography, reference edits, and inpainting."
metadata: {"openclaw":{"requires":{"bins":["uv"]},"primaryEnv":"OPENAI_API_KEY","homepage":"https://github.com/wuyoscar/gpt_image_2_skill"}}
---

# gpt-image

Generate/edit with the prompt library and bundled `scripts/generate.py`. Requires `uv` and Python 3.11+; script dependencies are declared inline. Do not reimplement image API code.

## Operating loop

1. **Classify request and resolve model**: `generate`, `edit`, `inpaint`, or `multi-reference`; identify asset type, exact text, aspect ratio, references, safety constraints, and budget/quality. Apply the model-choice rules below before any API call.
2. **Choose the reference path**: Image 2 keeps the gallery-first workflow below. For 2.5, a precise brief needs no reference loading; otherwise choose one short task slice.
3. **Refine only as needed**: preserve the brief. Add a specific gallery case, craft section or template only to fill a concrete gap; do not load them as a bundle for 2.5.
4. **Confer when useful**: before costly/ambiguous/high-polish calls, present 1–3 matched directions plus planned size/quality; ask at most one concise question at a time. Skip long discussion for precise “generate now” requests with a resolved model.
5. **Execute the bundled script**: resolve the installed skill's actual script path. Pass `--model` for the user's explicit model choice; otherwise let the script use its configured/default model. Check reference/mask paths and agreed flags. Do not probe or install a separate CLI, overwrite skills, modify config/`.env`, or write API keys for normal image requests.
6. **Report**: output file path(s), key flags, and one concise refinement suggestion if useful.

Fast path: confirmed 2.5 model + precise prompt + “generate now” → bundled script, without a mandatory reference/craft pass. Do not reconfirm an exact valid model.

## Model choice and prompt adaptation

| Choice | API model ID | Suggested use |
|---|---|---|
| Flare | `gpt-image-2.5-flare` | Fast general generation and drafts |
| Sunburst | `gpt-image-2.5-sunburst` | Precise reference edits and detailed control |
| Image 2 | `gpt-image-2` | Existing Image 2 workflows and compatibility |

- If the user does not specify a model, omit `--model` to use the configured/default model. If the user supplies an ambiguous name (such as “GPT 2.5”) or a probable typo, ask one clear question offering **Flare, Sunburst, and Image 2**, then wait. Do not treat `gpt-image-2.5` as an official API model ID.
- Use an exact supported model ID, an unambiguous choice from this menu, or the user's already confirmed choice for the current task without asking again. If the user explicitly says “you choose,” explain the pick briefly and proceed; consider their task and budget rather than always selecting the most expensive settings.
- Pass an explicitly chosen ID through `--model`. Preserve an exact gateway model alias configured or supplied by the user; do not replace it with an official ID. The script defaults to `gpt-image-2` only when no model is configured.
- Keep model confirmation, cost discussion, and API flags separate from the final image prompt. Use the model-specific reference path below only when it helps the task. Preserve the user's exact text, intended content, reference identity, and edit invariants; obtain confirmation before material prompt changes.
- Generate one image unless the user requested more. Do not silently switch models, change material prompt content, or run multiple model/prompt variants or comparisons. Ask before additional paid variants. For an authorized same-prompt comparison, keep the prompt, size, and quality identical unless the user asks to vary them.
- Consult `references/models.md` when parameter support or validation status needs checking. On an invalid-model, access/403, quota, or policy failure, report the failure and stop; do not switch models or rewrite the prompt to retry automatically.

## Run the bundled script

```bash
uv run "/actual/installed/gpt-image/scripts/generate.py" -p "PROMPT" [--model MODEL_ID] [-f OUT] [-i REF...] [-m MASK] [options]
```

Replace the example path with the installed skill's actual location; no standard `SKILL_DIR` environment variable is assumed. The script contains the complete implementation and works when only this skill folder is copied; it needs no repository package or PATH command. `uv` prepares dependencies from its inline metadata and adjacent lockfile.

## Saved image connection

The script automatically reads `~/.config/gpt-image/config.toml` for the user running the agent. This location is independent of the agent's project and skill installation directory. Use the bundled `config.example.toml` as a setup template; never overwrite a real config during image requests or display its credential contents.

```toml
base_url = "https://gateway.example/v1"
api_key = "your-image-service-key"
model = "gpt-image-2"
timeout = 600
```

Precedence per field: explicit `--base-url` / `--model` / `--timeout` → `GPT_IMAGE_BASE_URL` / `GPT_IMAGE_MODEL` / `GPT_IMAGE_TIMEOUT` → matching TOML field → compatibility defaults. Key precedence: `GPT_IMAGE_API_KEY` → TOML `api_key` → `OPENAI_API_KEY`. Base URL falls back to `OPENAI_BASE_URL`, then the official OpenAI API. Model defaults to `gpt-image-2`; API request timeout defaults to 600 seconds. Existing env values are kept while loading current-directory `.env`, then `~/.env`.

`--config PATH` overrides `GPT_IMAGE_CONFIG` and the default config path. Explicitly selected missing files and invalid config stop execution; a missing default file permits compatibility fallbacks. The script does not import the host agent's main-model settings. Containers and remote agents need the config in their own user directory or an explicitly selected path.

A custom base URL must include the gateway's API prefix, for example `/v1`. The SDK appends `/images/generations` or `/images/edits`. The service must support OpenAI Images API, including multipart edits; Chat/Responses compatibility alone is insufficient. Settings resolve independently, so configure the image key and address together. Gateway aliases use the gateway's parameter contract; do not assume an alias proves support for model-specific quality levels.

## Key and cost rules

- Use the configured image key and base URL as one connection. Image-specific settings take precedence over generic `OPENAI_*` settings; requests may bill the selected image service.
- If host/runtime has native platform-managed image generation and the user wants that path, use the host tool instead of this script.
- If no image API key is configured, report the missing key or use host-native generation when requested; do not write secrets.
- If the user wants to avoid local-key use, do not run this script. Unsetting only `OPENAI_API_KEY` does not disable saved image credentials. An explicitly empty `GPT_IMAGE_API_KEY` blocks fallback keys.
- Never print secret values.

## Flags

| Flag | Values | Use |
|---|---|---|
| `-p, --prompt` | string | Required prompt/edit instruction |
| `-f, --file` | path | Output path; auto-named if omitted |
| `-i, --image` | repeatable path | Use edits endpoint; supports multiple references |
| `-m, --mask` | PNG path | Inpaint with alpha mask; requires `-i` |
| `--config` | TOML path | Select another image connection; missing explicit files fail |
| `--base-url` | HTTP(S) API base URL | Override the saved gateway for this request |
| `--timeout` | positive seconds | Override the API request timeout |
| `--model` | official image model ID or exact gateway alias | Override the configured/default model |
| `--size` | `1k`, `2k`, `4k`, `portrait`, `landscape`, `square`, `wide`, `tall`, or literal | Canvas size |
| `--quality` | `low`, `medium`, `high`, `auto`; 2.5 also `xhigh`, `max` | Cost/quality dial; check model-specific limits |
| `-n, --n` | integer | Number of images |
| `--background` | `auto`, `opaque`; 2.5 also `transparent` | Transparency requires PNG or WebP, not JPEG |
| `--input-fidelity` | `low`, `high`; omitted by default | Edit-only; explicit 2.5 values are forwarded to the API, not assumed supported |
| `--moderation` | `auto`, `low` | Generation moderation setting |
| `--format` | `png`, `jpeg`, `webp` | Output encoding |
| `--compression` | `0-100` | JPEG/WebP compression |
| `--user` | string | Optional end-user identifier |

Quality starting points (not guarantees; keep the user's agreed setting). For 2.5, these take precedence over fixed quality advice in older craft references:
- `low`: cheap drafts and broad exploration; multiple variants require user authorization.
- `medium`: normal exploration, style probing, balanced cost.
- `high`: script default and a candidate for final assets, dense text, diagrams and UI. On 2.5, evaluate against the task requirements; do not assume `medium` fails or a higher setting always wins.
- `xhigh` / `max`: 2.5-only options for higher-quality work; discuss the cost trade-off before increasing an already agreed quality. Do not use them automatically for budget-conscious requests.

Size policy:
- default/social square: `1k` / `1024x1024`
- poster/mobile/beauty: `portrait`
- landscape/gameplay/photo: `landscape`
- print/paper figure: `2k`
- widescreen hero: `4k`
- vertical story/banner: `tall`

## Endpoint routing

| Mode | Trigger | Endpoint |
|---|---|---|
| Text-to-image | no `-i` | `{base_url}/images/generations` |
| Reference edit | one or more `-i` | `{base_url}/images/edits` |
| Inpaint | `-i` + `-m` | `{base_url}/images/edits` with mask |

Surface API errors verbatim enough for debugging; exit codes: `0` success, `1` API/refusal, `2` bad args/missing key.

## Reference loading

- **Image 2**: open `references/gallery.md`, then one matching `references/gallery-*.md` category and its actual prompt text. Read only relevant sections of `references/craft.md` or the historical `references/openai-cookbook.md` when needed.
- **Image 2.5**: no mandatory references for a precise brief. If guidance is needed, choose **one** directly: `references/openai-image-2.5-generation.md` (photo/product/illustration), `references/openai-image-2.5-layout-and-text.md` (text/UI/diagrams/panels), or `references/openai-image-2.5-editing.md` (references/masks/translation).
- **Other questions**: `references/openai-image-2.5.md` is an optional index; `references/openai-image-2.5-migration.md` covers migration/comparison; `references/models.md` owns current API parameters and validation status.
- **Extra inspiration only**: gallery cases, a targeted craft section, or `references/templates-gpt-image-2.5.md` (community adaptations, not verified outputs). Do not preload them or the old Cookbook for 2.5.

Load the smallest useful slice, not both model routes. Add a second task slice only for a genuine hybrid. Historical examples do not override current API notes or the user's model/settings.

## Verification

- Before API call: respect the configured connection/model or the user's explicit overrides; check endpoint mode, size, quality, output path, and required reference/mask files. Do not print the config's secret contents. Omit `--input-fidelity` unless explicitly needed; do not assume 2.5 always uses or accepts `high`.
- After execution: report path(s) printed by the script and surface stderr on failure.
- For edits/inpaints: verify `-i` paths exist; verify `-m` exists when used.

Preserve `Curated` vs `Author + Source` metadata when adapting examples. Add new prompts to the matching reference category. For edit examples, obtain the input image from the user.
