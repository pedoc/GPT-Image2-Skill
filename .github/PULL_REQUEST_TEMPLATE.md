## Summary

<!-- Describe the resulting behavior and affected skills or references. Link relevant issues. -->

## Type of change

- [ ] Skill instructions or metadata
- [ ] Script behavior
- [ ] Prompt reference
- [ ] Documentation or maintenance

## Checklist

- [ ] Updated bilingual usage instructions when applicable
- [ ] Preserved prompt attribution and reference index consistency
- [ ] Checked local Markdown links; no generated images or sample artifacts added

## Verification

- [ ] `uv sync --locked`
- [ ] `uv run --locked python -m unittest discover -s tests -v`
- [ ] `uv run --locked python -m py_compile skills/gpt-image/scripts/generate.py`
- [ ] `uv run --locked skills/gpt-image/scripts/generate.py --help`
- [ ] `git diff --check`

## Notes

<!-- Explain dependency changes, compatibility limits, or remaining validation. -->
