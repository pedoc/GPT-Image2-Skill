---
name: gpt-image
description: "Generate or edit images with GPT Image 2 or 2.5 through the bundled uv script and Reference Gallery. Use for image requests including imprecise 'GPT 2.5' model names, posters, typography, reference edits, and inpainting; resolve the model choice before generation."
metadata: {"openclaw":{"requires":{"bins":["uv"]},"primaryEnv":"OPENAI_API_KEY","homepage":"https://github.com/wuyoscar/gpt_image_2_skill"}}
---

# gpt-image

Generate/edit with the prompt library and bundled `scripts/generate.py`. Requires `uv` and Python 3.11+; script dependencies are declared inline. Do not reimplement image API code.

## Operating loop

1. **Classify request and resolve model**: `generate`, `edit`, `inpaint`, or `multi-reference`; identify asset type, exact text, aspect ratio, references, safety constraints, and budget/quality. Apply the model-choice rules below before any API call.
2. **Choose the reference path**: Image 2 keeps the gallery-first workflow below. For 2.5, a precise brief needs no reference loading; otherwise choose one short task slice.
3. **Refine only as needed**: preserve the brief. Add a specific gallery case, craft section or template only to fill a concrete gap; do not load them as a bundle for 2.5.
4. **Confer when useful**: before costly/ambiguous/high-polish calls, present 1–3 matched directions plus planned size/quality; ask at most one concise question at a time. Skip long discussion for precise “generate now” requests with a resolved model.
5. **Execute the bundled script**: use the runtime-provided skill path and an explicit `--model`. Check reference/mask paths and agreed flags. Do not probe or install a separate CLI, overwrite skills, modify `.env`, or write API keys for normal image requests.
6. **Report**: output file path(s), key flags, and one concise refinement suggestion if useful.

Fast path: confirmed 2.5 model + precise prompt + “generate now” → bundled script, without a mandatory reference/craft pass. Do not reconfirm an exact valid model.

## Model choice and prompt adaptation

| Choice | API model ID | Suggested use |
|---|---|---|
| Flare | `gpt-image-2.5-flare` | Fast general generation and drafts |
| Sunburst | `gpt-image-2.5-sunburst` | Precise reference edits and detailed control |
| Image 2 | `gpt-image-2` | Existing Image 2 workflows and compatibility |

- If the model is absent, ambiguous (such as “GPT 2.5”), or misspelled, ask one clear question offering **Flare, Sunburst, and Image 2** with these trade-offs, then wait. For a typo, suggest the likely intended choice without silently correcting it. Do not treat `gpt-image-2.5` as an API model ID.
- Use an exact supported model ID, an unambiguous choice from this menu, or the user's already confirmed choice for the current task without asking again. If the user explicitly says “you choose,” explain the pick briefly and proceed; consider their task and budget rather than always selecting the most expensive settings.
- Always pass the chosen ID through `--model`. The script retains `gpt-image-2` as its default; the agent must still resolve the user's choice.
- Keep model confirmation, cost discussion, and API flags separate from the final image prompt. Use the model-specific reference path below only when it helps the task. Preserve the user's exact text, intended content, reference identity, and edit invariants; obtain confirmation before material prompt changes.
- Generate one image unless the user requested more. Do not silently switch models, change material prompt content, or run multiple model/prompt variants or comparisons. Ask before additional paid variants. For an authorized same-prompt comparison, keep the prompt, size, and quality identical unless the user asks to vary them.
- Consult `references/models.md` when parameter support or validation status needs checking. On an invalid-model, access/403, quota, or policy failure, report the failure and stop; do not switch models or rewrite the prompt to retry automatically.

## Run the bundled script

```bash
uv run "$SKILL_DIR/scripts/generate.py" --model MODEL_ID -p "PROMPT" [-f OUT] [-i REF...] [-m MASK] [options]
```

`SKILL_DIR` is the installed skill folder supplied by the runtime. The script contains the complete implementation and works when only this skill folder is copied; it needs no repository package or PATH command. `uv` prepares dependencies from its inline metadata and adjacent lockfile.

## Key and cost rules

- The script reads `OPENAI_API_KEY` from process env, then `.env`, then `~/.env` without overriding existing env; successful API calls may bill the user’s OpenAI account.
- If host/runtime has native platform-managed image generation and the user wants that path, use the host tool instead of this script.
- If `OPENAI_API_KEY` is unset, report missing key or use host-native generation when requested; do not write secrets.
- If user wants to avoid local-key use, respect `unset OPENAI_API_KEY`; if a key exists in `.env`/`~/.env`, tell them to remove/rename it for the session rather than working around it.
- Never print secret values.

## Flags

| Flag | Values | Use |
|---|---|---|
| `-p, --prompt` | string | Required prompt/edit instruction |
| `-f, --file` | path | Output path; auto-named if omitted |
| `-i, --image` | repeatable path | Use edits endpoint; supports multiple references |
| `-m, --mask` | PNG path | Inpaint with alpha mask; requires `-i` |
| `--model` | `gpt-image-2`, `gpt-image-2.5-flare`, `gpt-image-2.5-sunburst` | Agent must pass the resolved choice explicitly |
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
| Text-to-image | no `-i` | `/v1/images/generations` |
| Reference edit | one or more `-i` | `/v1/images/edits` |
| Inpaint | `-i` + `-m` | `/v1/images/edits` with mask |

Surface API errors verbatim enough for debugging; exit codes: `0` success, `1` API/refusal, `2` bad args/missing key.

## Reference loading

- **Image 2**: open `references/gallery.md`, then one matching `references/gallery-*.md` category and its actual prompt text. Read only relevant sections of `references/craft.md` or the historical `references/openai-cookbook.md` when needed.
- **Image 2.5**: no mandatory references for a precise brief. If guidance is needed, choose **one** directly: `references/openai-image-2.5-generation.md` (photo/product/illustration), `references/openai-image-2.5-layout-and-text.md` (text/UI/diagrams/panels), or `references/openai-image-2.5-editing.md` (references/masks/translation).
- **Other questions**: `references/openai-image-2.5.md` is an optional index; `references/openai-image-2.5-migration.md` covers migration/comparison; `references/models.md` owns current API parameters and validation status.
- **Extra inspiration only**: gallery cases, a targeted craft section, or `references/templates-gpt-image-2.5.md` (community adaptations, not verified outputs). Do not preload them or the old Cookbook for 2.5.

Load the smallest useful slice, not both model routes. Add a second task slice only for a genuine hybrid. Historical examples do not override current API notes or the user's model/settings.

## Verification

- Before API call: check the resolved model and explicit `--model`, endpoint mode, size, quality, output path, and required reference/mask files. Omit `--input-fidelity` unless explicitly needed; do not assume 2.5 always uses or accepts `high`.
- After execution: report path(s) printed by the script and surface stderr on failure.
- For edits/inpaints: verify `-i` paths exist; verify `-m` exists when used.

Preserve `Curated` vs `Author + Source` metadata when adapting examples. Add new prompts to the matching reference category. For edit examples, obtain the input image from the user.
