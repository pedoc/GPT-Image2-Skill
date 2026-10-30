# Security Policy

## Supported versions

This project contains lightweight agent skills and a self-contained generation script. Security fixes are handled on the `main` branch.

## Reporting a vulnerability

Please do **not** open a public issue for vulnerabilities involving secrets, credential leakage, unsafe file handling, or API misuse.

Report privately through GitHub's security advisory flow if available, or contact the repository owner through their public GitHub profile.

When reporting, include:

- A short summary of the issue.
- Reproduction steps or a minimal proof of concept.
- Impact and affected files.
- Any suggested fix, if known.

## Secret handling

- Never commit real `GPT_IMAGE_API_KEY`, `OPENAI_API_KEY`, `.env`, image config credentials, or other secrets. Keep the real `~/.config/GPT-Image2-Skill/config.toml` outside the repository and skill folder.
- Image settings resolve from explicit flags, `GPT_IMAGE_*`, then the selected TOML config before generic `OPENAI_*` fallbacks. Existing `.env` loading remains process env, then current-directory `.env`, then `~/.env`, without overriding an already-set variable. Configure the image key and base URL together to avoid mixing connections.
- Configuration parse errors must not print credential-bearing source lines. An empty `GPT_IMAGE_API_KEY` blocks fallback credentials; unsetting only `OPENAI_API_KEY` does not disable saved image credentials.
- Generated examples and issue reports should not include private prompts, private images, or API response bodies containing secrets.
