# Contributing

This repository contains two agent skills, a self-contained generation script, and text-only prompt references. Use Python 3.11+ and `uv` for development.

## Scope and structure

- Keep generation logic in `skills/gpt-image/scripts/generate.py`; do not introduce a separate CLI package or command-discovery chain.
- Update generation instructions in `skills/gpt-image/SKILL.md` and prompt-extraction instructions in `skills/get-prompt-from-image/SKILL.md`.
- Keep detailed guidance and reusable prompts in the relevant skill's `references/` directory. Load references only when needed.
- Keep installation and usage instructions aligned in `README.md` and `README.zh.md`.

## Prompt references

Add prompts to the matching `skills/gpt-image/references/gallery-*.md` category. Keep prompts concrete, reusable, and consistent with the user's intended medium and layout.

Preserve `Curated` or `Author + Source` attribution. Keep existing entry identifiers stable; when moving or adding entries, update `references/gallery.md` ranges and counts. Editing examples must describe the required user-provided input.

Do not add generated images, sample-run artifacts, image previews, or links to local image collections. Prompt examples belong in the skill references rather than the README.

## Environment and dependencies

```bash
uv sync --locked
```

`uv.lock` fixes the repository/test environment. The generation script declares its own dependencies inline and carries `generate.py.lock` so a copied skill works independently. Update both dependency declarations when changing requirements, then run:

```bash
uv lock
uv lock --script skills/gpt-image/scripts/generate.py
uv sync --locked
```

## Verification

```bash
uv run --locked python -m unittest discover -s tests -v
uv run --locked python -m py_compile skills/gpt-image/scripts/generate.py
uv run --locked skills/gpt-image/scripts/generate.py --help
git diff --check
```

Tests use `unittest`, temporary directories, fake credentials, and simulated HTTP transports. Add regression coverage for changed behavior and keep tests offline. The copied-script test verifies operation outside the repository. A live generation check requires separate authorization; never represent offline tests as visual-quality validation.

Check that local Markdown links resolve and no deleted asset paths remain. Keep credentials and private images out of commits and issue reports.

## Pull requests

Use `.github/PULL_REQUEST_TEMPLATE.md`. Describe the resulting behavior, affected skills/references, verification performed, and relevant issues. Attribute external prompts and explain any behavior or dependency changes.

## 中文说明

仅维护 Skill、自带脚本和纯文本参考资料，不提交生成图片或样张记录。依赖统一使用 uv 管理；改动后完成离线测试、链接与格式检查。涉及安装和使用方式时同步两份 README，外部提示词保留来源署名。
