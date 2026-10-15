"""Image generation adapter for MOVI (OpenAI Images API)."""
from __future__ import annotations

import base64
import json
import os
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class ImageGenerationError(RuntimeError):
    """Raised when an image provider cannot return a usable image."""


def generate_openai_image(*, prompt: str, output_path: Path, model: str = "gpt-image-1") -> dict:
    """Generate one PNG using the OpenAI Images API; requires OPENAI_API_KEY."""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ImageGenerationError(
            "OPENAI_API_KEY is not set. Export it in this terminal; never commit API keys."
        )
    payload = {
        "model": model,
        "prompt": prompt,
        "size": "1536x1024",
        "quality": "high",
        "output_format": "png",
        "n": 1,
    }
    request = Request(
        "https://api.openai.com/v1/images/generations",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urlopen(request, timeout=180) as response:
            result = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        details = exc.read().decode("utf-8", errors="replace")[:1200]
        raise ImageGenerationError(f"Image provider returned HTTP {exc.code}: {details}") from exc
    except (URLError, TimeoutError) as exc:
        raise ImageGenerationError(f"Could not reach image provider: {exc}") from exc
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ImageGenerationError(f"Image provider returned invalid JSON: {exc}") from exc

    items = result.get("data") if isinstance(result, dict) else None
    encoded = items[0].get("b64_json") if items and isinstance(items[0], dict) else None
    if not encoded:
        raise ImageGenerationError(
            "Image provider response did not contain data[0].b64_json; no asset was saved."
        )
    try:
        image_bytes = base64.b64decode(encoded, validate=True)
    except (ValueError, base64.binascii.Error) as exc:
        raise ImageGenerationError("Image provider returned invalid base64 image data.") from exc
    if not image_bytes.startswith(b"\\x89PNG\\r\\n\\x1a\\n"):
        raise ImageGenerationError("Image provider output was not a PNG; no asset was saved.")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(image_bytes)
    return {
        "provider": "openai",
        "model": model,
        "media_type": "image/png",
        "bytes": len(image_bytes),
    }
