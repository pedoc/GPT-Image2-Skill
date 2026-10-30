#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "openai>=2.32.0",
#     "python-dotenv>=1.0",
# ]
# ///
"""Generate or edit images with the skill's self-contained uv script.

Reads image-specific settings from GPT_IMAGE_* or ~/.config/gpt-image/config.toml.
Falls back to OPENAI_* from process env, ./.env, then ~/.env without replacing
an existing variable. Saves PNG/JPEG/WebP and prints output paths.
Exit codes: 0 success, 1 API error, 2 bad arguments or missing key.

Run from the repository root:
    uv run skills/gpt-image/scripts/generate.py --model MODEL_ID -p "PROMPT"

Installed skills use their runtime-provided path:
    uv run "/actual/installed/gpt-image/scripts/generate.py" -p "PROMPT"
"""
from __future__ import annotations

import argparse
import base64
import math
import os
import re
import sys
import tomllib
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from dotenv import load_dotenv
from openai import APIError, OpenAI


def _load_env_chain() -> None:
    """Resolve OPENAI_API_KEY without overriding runtime-provided env.

    Order: process env → ./.env → ~/.env. Existing process env wins so
    hosted agents or explicit shell exports are not replaced by local files.
    """
    load_dotenv(Path.cwd() / ".env", override=False)
    load_dotenv(Path.home() / ".env", override=False)


SIZE_SHORTCUTS: dict[str, str] = {
    "1k": "1024x1024",
    "2k": "2048x2048",
    "4k": "3840x2160",
    "portrait": "1024x1536",
    "landscape": "1536x1024",
    "square": "1024x1024",
    "wide": "2048x1152",
    "tall": "2160x3840",
}

DEFAULT_MODEL = "gpt-image-2"
DEFAULT_BASE_URL = "https://api.openai.com/v1"
DEFAULT_TIMEOUT = 600.0
DEFAULT_SIZE = "1024x1024"
DEFAULT_MODERATION = "low"


def positive_timeout(value: Any) -> float:
    if isinstance(value, bool):
        raise ValueError
    timeout = float(value)
    if not math.isfinite(timeout) or timeout <= 0:
        raise ValueError
    return timeout


def read_config(parser: argparse.ArgumentParser, path: Path | None) -> dict[str, Any]:
    if path is None:
        configured_path = os.environ.get("GPT_IMAGE_CONFIG")
        if configured_path is not None:
            if not configured_path.strip():
                parser.error("GPT_IMAGE_CONFIG must not be empty")
            path = Path(configured_path)
    required = path is not None
    path = path.expanduser() if path is not None else Path.home() / ".config/gpt-image/config.toml"
    try:
        config = tomllib.loads(path.read_text(encoding="utf-8-sig"))
    except FileNotFoundError:
        if required:
            parser.error(f"config file not found: {path}")
        return {}
    except (OSError, UnicodeError, tomllib.TOMLDecodeError):
        # Parser exceptions may include credential-bearing source lines.
        parser.error(f"cannot read valid TOML config: {path}")
    for name, value in config.items():
        if name not in ("api_key", "base_url", "model", "timeout"):
            parser.error(f"unknown config option: {name}")
        if name != "timeout" and (not isinstance(value, str) or not value.strip()):
            parser.error(f"config {name} must be a nonempty string")
    if "timeout" in config:
        try:
            config["timeout"] = positive_timeout(config["timeout"])
        except (TypeError, ValueError, OverflowError):
            parser.error("config timeout must be a positive finite number of seconds")
    return config


def slugify(text: str, max_len: int = 30) -> str:
    s = re.sub(r"[^\w\s-]", "", text.lower()).strip()
    s = re.sub(r"[-\s]+", "-", s)[:max_len]
    return s or "image"


def default_output_path(prompt: str, extension: str) -> Path:
    cwd = Path.cwd()
    target_dir = cwd / "fig" if (cwd / "fig").is_dir() else cwd
    stamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    return target_dir / f"{stamp}-{slugify(prompt)}.{extension}"


def resolve_size(value: str) -> str:
    return SIZE_SHORTCUTS.get(value.lower(), value)


def model_rejects_input_fidelity(model: str) -> bool:
    return re.fullmatch(r"gpt-image-2(?:-\d{4}-\d{2}-\d{2})?", model) is not None


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="generate.py",
        description="Call an OpenAI-compatible Images API (generations or edits) via the official openai Python SDK.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("-p", "--prompt", required=True, help="Text prompt / edit instruction.")
    p.add_argument(
        "-f", "--file",
        help="Output path. Auto-generated as YYYY-MM-DD-HH-MM-SS-<slug>.<ext> if omitted "
             "(written to ./fig/ if that dir exists, else ./).",
    )
    p.add_argument(
        "-i", "--image", action="append", type=Path, default=None,
        help="Reference image path. Repeat flag for multi-reference edits. "
             "Presence of any -i switches endpoint to client.images.edit().",
    )
    p.add_argument(
        "-m", "--mask", type=Path, default=None,
        help="Alpha-channel PNG mask (opaque = preserved, transparent = regenerated). "
             "Edits endpoint only; requires -i.",
    )
    p.add_argument("--config", type=Path, help="TOML config path. Default GPT_IMAGE_CONFIG or ~/.config/gpt-image/config.toml.")
    p.add_argument("--base-url", help="Images API base URL, including its API prefix (for example https://gateway.example/v1). Overrides saved settings.")
    p.add_argument("--timeout", type=float, help=f"API request timeout in seconds. Default GPT_IMAGE_TIMEOUT, config timeout, or {DEFAULT_TIMEOUT:g}.")
    p.add_argument("--model", help=f"Model ID or gateway alias. Default GPT_IMAGE_MODEL, config model, or {DEFAULT_MODEL}.")
    p.add_argument(
        "--size", default=DEFAULT_SIZE,
        help="Image size. Accepts literals (1024x1024, 1536x1024, 2048x2048, 3840x2160, "
             "any 16px-multiple up to 3840 max edge, 3:1 ratio cap) or shortcuts "
             "(1k, 2k, 4k, portrait, landscape, square, wide, tall). Default 1024x1024.",
    )
    p.add_argument(
        "--quality", default="high", choices=["auto", "low", "medium", "high", "xhigh", "max"],
        help="Rendering fidelity / budget knob. Default high; xhigh/max require GPT Image 2.5. "
             "Use low for cheap drafts, medium for normal exploration, high for final text-heavy or shipping-facing assets.",
    )
    p.add_argument("-n", "--n", type=int, default=1, help="Number of images to return. Default 1.")
    p.add_argument(
        "--background", default=None, choices=["auto", "opaque", "transparent"],
        help="`transparent` requires png or webp. Default API-side auto.",
    )
    p.add_argument(
        "--moderation", default=DEFAULT_MODERATION, choices=["auto", "low"],
        help="Generations only. Default low. Use `auto` if you want the stricter API-side default.",
    )
    p.add_argument(
        "--input-fidelity", dest="input_fidelity", default=None, choices=["low", "high"],
        help="Edits only; omitted by default. Dropped for gpt-image-2; explicit 2.5 values are passed to the API (support unverified).",
    )
    p.add_argument(
        "--format", dest="output_format", default=None,
        choices=["png", "jpeg", "webp"],
        help="Output encoding. Default png.",
    )
    p.add_argument(
        "--compression", dest="output_compression", type=int, default=None,
        help="0-100 compression level for jpeg/webp. Ignored for png.",
    )
    p.add_argument(
        "--user", default=None,
        help="Optional end-user identifier forwarded to OpenAI for abuse tracking.",
    )
    args = p.parse_args()
    _load_env_chain()
    config = read_config(p, args.config)
    args.api_key = os.environ.get("GPT_IMAGE_API_KEY", config.get("api_key", os.environ.get("OPENAI_API_KEY")))
    if args.base_url is None:
        args.base_url = os.environ.get("GPT_IMAGE_BASE_URL", config.get("base_url", os.environ.get("OPENAI_BASE_URL", DEFAULT_BASE_URL)))
    if args.model is None:
        args.model = os.environ.get("GPT_IMAGE_MODEL", config.get("model", DEFAULT_MODEL))
    if args.timeout is None:
        args.timeout = os.environ.get("GPT_IMAGE_TIMEOUT", config.get("timeout", DEFAULT_TIMEOUT))
    if not isinstance(args.model, str) or not args.model.strip():
        p.error("model must be a nonempty string")
    try:
        args.timeout = positive_timeout(args.timeout)
    except (TypeError, ValueError, OverflowError):
        p.error("timeout must be a positive finite number of seconds")
    try:
        url = urlsplit(args.base_url)
        if (any(char.isspace() for char in args.base_url)
                or url.scheme not in ("http", "https") or not url.hostname or url.port == 0
                or url.username is not None or url.password is not None or url.query or url.fragment):
            raise ValueError
    except ValueError:
        p.error("base URL must be an absolute HTTP(S) URL without credentials, query, or fragment")
    image25 = re.fullmatch(r"gpt-image-2\.5-(?:flare|sunburst)(?:-\d{4}-\d{2}-\d{2})?", args.model) is not None
    if args.quality in ("xhigh", "max") and not image25:
        p.error("--quality xhigh/max requires --model gpt-image-2.5-flare or gpt-image-2.5-sunburst")
    if args.background == "transparent" and args.output_format == "jpeg":
        p.error("--background transparent requires --format png or webp")
    if not 1 <= args.n <= 10:
        p.error("--n must be between 1 and 10")
    if args.output_compression is not None and not 0 <= args.output_compression <= 100:
        p.error("--compression must be between 0 and 100")
    if args.mask and not args.image:
        p.error("--mask requires --image (edits endpoint only)")
    size = resolve_size(args.size)
    if (image25 or model_rejects_input_fidelity(args.model)) and size != "auto":
        match = re.fullmatch(r"(\d+)x(\d+)", size)
        if not match:
            p.error("--size must be auto, a size shortcut, or WIDTHxHEIGHT")
        width, height = map(int, match.groups())
        if (min(width, height) <= 0 or max(width, height) > 3840
                or width % 16 or height % 16 or max(width, height) > 3 * min(width, height)
                or not 655360 <= width * height <= 8294400):
            p.error("--size requires 16px multiples, edges <=3840px, aspect ratio <=3:1, and 655360–8294400 pixels")
    return args


def _filter_none(d: dict[str, Any]) -> dict[str, Any]:
    """Drop keys whose value is None — SDK treats missing vs None differently."""
    return {k: v for k, v in d.items() if v is not None}


def call_generate(client: OpenAI, args: argparse.Namespace) -> Any:
    return client.images.generate(**_filter_none({
        "model": args.model,
        "prompt": args.prompt,
        "size": resolve_size(args.size),
        "quality": args.quality,
        "n": args.n,
        "background": args.background,
        "moderation": args.moderation,
        "output_format": args.output_format,
        "output_compression": args.output_compression if args.output_format in ("jpeg", "webp") else None,
        "user": args.user,
    }))


def call_edit(client: OpenAI, args: argparse.Namespace) -> Any:
    for p in args.image:
        if not p.is_file():
            print(f"error: --image not found: {p}", file=sys.stderr)
            sys.exit(2)
    if args.mask and not args.mask.is_file():
        print(f"error: --mask not found: {args.mask}", file=sys.stderr)
        sys.exit(2)

    input_fidelity = args.input_fidelity
    if input_fidelity and model_rejects_input_fidelity(args.model):
        print(
            "note: dropping --input-fidelity because gpt-image-2 rejects that parameter.",
            file=sys.stderr,
        )
        input_fidelity = None

    image_handles = [p.open("rb") for p in args.image]
    mask_handle = args.mask.open("rb") if args.mask else None
    try:
        return client.images.edit(**_filter_none({
            "model": args.model,
            "image": image_handles,
            "mask": mask_handle,
            "prompt": args.prompt,
            "size": resolve_size(args.size),
            "quality": args.quality,
            "n": args.n,
            "background": args.background,
            "input_fidelity": input_fidelity,
            "output_format": args.output_format,
            "output_compression": args.output_compression if args.output_format in ("jpeg", "webp") else None,
            "user": args.user,
        }))
    finally:
        for h in image_handles:
            h.close()
        if mask_handle:
            mask_handle.close()


def write_outputs(data: list[Any], out_path: Path, n: int) -> list[Path]:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for i, item in enumerate(data):
        b64 = getattr(item, "b64_json", None)
        url = getattr(item, "url", None)
        if b64:
            raw = base64.b64decode(b64)
        elif url:
            with urllib.request.urlopen(url, timeout=300) as r:  # noqa: S310 — OpenAI-owned host
                raw = r.read()
        else:
            print(f"error: response item {i} has neither b64_json nor url", file=sys.stderr)
            sys.exit(1)

        if n == 1:
            target = out_path
        else:
            stem = out_path.with_suffix("")
            target = stem.parent / f"{stem.name}_{i}{out_path.suffix}"
        target.write_bytes(raw)
        written.append(target)
    return written


def main() -> int:
    args = parse_args()

    if not args.api_key or not args.api_key.strip():
        print(
            "error: image API key not set. Set GPT_IMAGE_API_KEY, config api_key, or OPENAI_API_KEY.",
            file=sys.stderr,
        )
        return 2

    ext = args.output_format or "png"
    out_path = Path(args.file).expanduser().resolve() if args.file else default_output_path(args.prompt, ext)

    # Explicit connection settings keep the host agent's text-model endpoint separate.
    client = OpenAI(api_key=args.api_key, base_url=args.base_url, timeout=args.timeout, max_retries=0)

    try:
        result = call_edit(client, args) if args.image else call_generate(client, args)
    except APIError as e:
        print(f"error: {type(e).__name__}: {e}", file=sys.stderr)
        return 1

    data = result.data or []
    if not data:
        print(f"error: no image data in response: {result}", file=sys.stderr)
        return 1

    for p in write_outputs(data, out_path, args.n):
        print(p)
    return 0


if __name__ == "__main__":
    sys.exit(main())
