# Changelog

## Unreleased

- Removed the tracked image gallery, sample records, and plugin packaging; kept self-contained skills and text-only prompt references. Reduced the bilingual READMEs to installation, usage, and development instructions.
- Replaced the standalone CLI package and launcher fallback chain with one self-contained `skills/gpt-image/scripts/generate.py` entrypoint. Run it with `uv run`; the `gpt-image` console command is no longer provided.
- Added uv-managed repository and script lockfiles, a Python version pin, and offline coverage for running a copied script outside the checkout.
- Simplified the skill runbook to invoke its bundled script directly, preserving model selection, credentials, API flags, and no-retry behavior.
- Added safer install and API-key guidance: avoid blind reinstall/overwrite, keep global/shared installs opt-in, and never write secrets unless explicitly requested.
- Updated cross-agent installation wording for Codex, OpenClaw, Claude Code, and manual skill runtimes.

## v0.2.0 — 2026-04-25

This release collects the recent documentation, gallery, skill, and discoverability updates after the initial public release.

### Highlights

- **Full split Reference Gallery Atlas** — expanded the skill references into category-level `gallery-*.md` files so agents can load the relevant prompt slice without filling the context window.
- **README selected showcase refresh** — compacted the README into representative visual panels while keeping the full 162-prompt catalog in the Reference Gallery.
- **New and reorganized gallery material** — added/updated examples for research paper figures, scientific education, screen photography, gaming HUDs, events maps, beauty/lifestyle, cinematic references, and more.
- **Codex installation clarity** — clarified that `$skill-installer` is a built-in Codex skill-management helper and added a manual Codex fallback path.
- **Bilingual README navigation** — added visible English / 中文 switching near the README top.
- **SEO and discovery polish** — added natural search terms, expanded package/plugin keywords, GitHub topics, and Star History.

### Merged PRs

- #1 — Sync the full prompt gallery into the skill reference atlas
- #3 — Polish README showcase and sync split gallery atlas
- #4 — Add README language switch
- #5 — Clarify Codex skill installation
- #6 — Improve README SEO and add star history
