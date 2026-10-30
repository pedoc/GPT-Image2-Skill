# GPT Image Skills

[English](README.md) | [中文](README.zh.md)

Two self-contained agent skills for image generation, editing, and prompt extraction.

| Skill | Purpose |
| --- | --- |
| [`gpt-image`](skills/gpt-image/SKILL.md) | Generate and edit images through the bundled uv script |
| [`get-prompt-from-image`](skills/get-prompt-from-image/SKILL.md) | Extract reusable prompts from user-provided images |

## Install a skill

Copy the complete `skills/gpt-image/` or `skills/get-prompt-from-image/` folder into the skills directory used by your agent runtime. Preserve `SKILL.md`, `references/`, `agents/`, and any `scripts/` files, including the script lockfile. Install either skill or both.

The image-generation skill requires `uv`, Python 3.11+, and `OPENAI_API_KEY`. The prompt-extraction skill runs in an agent with image understanding and needs no Python setup of its own.

## Use through an agent

Invoke `$gpt-image` with the image brief, or `$get-prompt-from-image` with a reference image. The generation skill resolves the chosen model and runs its own `scripts/generate.py` directly.

Model choices include `gpt-image-2`, `gpt-image-2.5-flare`, and `gpt-image-2.5-sunburst`. Consult the skill's [model notes](skills/gpt-image/references/models.md) for parameter compatibility and validation limits.

## Run the bundled script

From the repository root:

```bash
uv run --locked skills/gpt-image/scripts/generate.py --help

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

Set `OPENAI_API_KEY` in your environment. The script checks process variables, the working directory's `.env`, then `~/.env`, keeping existing variables. API requests may incur charges. Never commit credentials or private input/output images.

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
