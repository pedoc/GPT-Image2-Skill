# GPT Image Skills

[English](README.md) | [中文](README.zh.md)

Two self-contained agent skills for image generation, editing, and prompt extraction.

| Skill | Purpose |
| --- | --- |
| [`gpt-image`](skills/gpt-image/SKILL.md) | Generate and edit images through the bundled uv script |
| [`get-prompt-from-image`](skills/get-prompt-from-image/SKILL.md) | Extract reusable prompts from user-provided images |

## Install a skill

Copy the complete `skills/gpt-image/` or `skills/get-prompt-from-image/` folder into the skills directory used by your agent runtime. Preserve `SKILL.md`, `references/`, `agents/`, and any `scripts/` files, including the script lockfile. Install either skill or both.

The image-generation skill requires `uv`, Python 3.11+, and an image-service API key. The prompt-extraction skill runs in an agent with image understanding and needs no Python setup of its own.

## Configure the image service once

Create `~/.config/gpt-image/config.toml` for the user running your agents. On Windows this is normally `C:\Users\<you>\.config\gpt-image\config.toml`. Every installed copy of this skill uses the same file, regardless of the current project. A [template](skills/gpt-image/config.example.toml) is included:

```toml
base_url = "https://gateway.example/v1"
api_key = "your-image-service-key"
model = "gpt-image-2"
timeout = 600
```

Use your gateway's API base URL, including its required prefix. The script appends `/images/generations` or `/images/edits`; the gateway must implement OpenAI Images API, including multipart uploads for edits. A text-only Chat/Responses gateway is insufficient. The saved `model` may be your gateway's exact image-model alias. `timeout` is the API request timeout in seconds.

Settings are resolved independently, from left to right:

| Setting | Command line | Image-specific environment | TOML field | Compatibility fallback |
| --- | --- | --- | --- | --- |
| API key | — | `GPT_IMAGE_API_KEY` | `api_key` | `OPENAI_API_KEY` |
| Base URL | `--base-url` | `GPT_IMAGE_BASE_URL` | `base_url` | `OPENAI_BASE_URL`, then the OpenAI API |
| Model | `--model` | `GPT_IMAGE_MODEL` | `model` | `gpt-image-2` |
| Timeout | `--timeout` | `GPT_IMAGE_TIMEOUT` | `timeout` | 600 seconds |

The saved image connection takes precedence over generic `OPENAI_*` values so the host agent's text-model credentials and address do not override it. Keep the image key and base URL together. Existing `.env` loading remains: process environment, current directory `.env`, then `~/.env`, without replacing existing variables.

Select another file with `--config /path/to/config.toml` or `GPT_IMAGE_CONFIG`; the flag wins. An explicitly selected missing file or an invalid config stops execution before any API request. An absent default file keeps the compatibility fallbacks. `--help` does not read config or send requests.

The config belongs to the user running the script; containers and remote agents use their own home directory unless you mount the file or select its path. The script does not read another agent's main-model settings or automatically read a config placed in the skill installation folder. Keep the real config outside this repository and never print its key.

## Use through an agent

Ask your agent to use `gpt-image` with the image brief, or `get-prompt-from-image` with a reference image. Runtimes supporting `$skill-name` can use `$gpt-image` and `$get-prompt-from-image`. Generation uses the saved model unless the user selects another; the skill runs its own `scripts/generate.py` directly.

Model choices include `gpt-image-2`, `gpt-image-2.5-flare`, and `gpt-image-2.5-sunburst`. Consult the skill's [model notes](skills/gpt-image/references/models.md) for parameter compatibility and validation limits.

## Run the bundled script

From the repository root:

```bash
uv run --locked skills/gpt-image/scripts/generate.py --help

# Use the saved image connection and model
uv run --locked skills/gpt-image/scripts/generate.py -p "A botanical poster"

# Generate one image
uv run --locked skills/gpt-image/scripts/generate.py \
  --model gpt-image-2.5-flare -p "A botanical poster with the title GARDEN" \
  --size portrait --quality medium -f poster.png

# Edit a user-provided reference
uv run --locked skills/gpt-image/scripts/generate.py \
  --model gpt-image-2.5-sunburst -p "Replace the sky with an aurora" \
  -i photo.jpg -f aurora.png
```

For an installed skill, substitute its actual script path. `uv` prepares dependencies from the script's inline metadata and adjacent `generate.py.lock`.

For a one-off address, pass `--base-url https://gateway.example/v1`; use `--config /path/to/config.toml` for another saved connection. Neither option changes your saved file. API requests may incur charges. Never commit credentials or private input/output images.

Additional options include repeatable `-i` references, `-m` for an alpha mask, `--format`, and `--background`. See `--help` and [SKILL.md](skills/gpt-image/SKILL.md). Successful runs print output paths; errors go to stderr. Exit codes are `0` for success, `1` for API failure, and `2` for invalid arguments or missing credentials.

## Repository layout

```text
skills/gpt-image/              Generation/editing skill, script, and references
skills/get-prompt-from-image/  Image-to-prompt skill and analysis references
tests/                        Offline script and credential tests
pyproject.toml                uv project dependencies
uv.lock                       Repository/test environment lock
```

Prompt references are text-only and loaded as needed. Provide your own input images for editing examples. Generated images and sample-run artifacts are not stored in this repository.

## Development

```bash
uv sync --locked
uv run --locked python -m unittest discover -s tests -v
uv run --locked python -m py_compile skills/gpt-image/scripts/generate.py
git diff --check
```

When changing dependencies, update both `pyproject.toml` and the script's inline metadata, then run `uv lock` and `uv lock --script skills/gpt-image/scripts/generate.py`.

See [CONTRIBUTING.md](CONTRIBUTING.md), [SECURITY.md](SECURITY.md), and [LICENSE](LICENSE).
