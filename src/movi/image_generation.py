"""Image-generation adapters for MOVI."""
from __future__ import annotations

import base64
import json
import os
import time
import uuid
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


class ImageGenerationError(RuntimeError):
    """Raised when an image provider cannot return a usable image."""


def _request_json(url: str, *, payload: dict | None = None, timeout: int = 30) -> dict:
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    headers = {"Content-Type": "application/json"} if payload is not None else {}
    request = Request(url, data=data, headers=headers, method="POST" if payload is not None else "GET")
    try:
        with urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        details = exc.read().decode("utf-8", errors="replace")[:1200]
        raise ImageGenerationError(f"Image provider returned HTTP {exc.code}: {details}") from exc
    except (URLError, TimeoutError) as exc:
        raise ImageGenerationError(f"Could not reach image provider at {url}: {exc}") from exc
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ImageGenerationError(f"Image provider returned invalid JSON: {exc}") from exc


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
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
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
    if not image_bytes.startswith(b"\x89PNG\r\n\x1a\n"):
        raise ImageGenerationError("Image provider output was not a PNG; no asset was saved.")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(image_bytes)
    return {"provider": "openai", "model": model, "media_type": "image/png", "bytes": len(image_bytes)}


def prepare_comfyui_workflow(workflow: dict, prompt_node: str, prompt: str) -> dict:
    """Copy an API-format ComfyUI workflow and replace a text encoder's prompt."""
    copied = json.loads(json.dumps(workflow))
    node = copied.get(str(prompt_node))
    if not isinstance(node, dict):
        raise ImageGenerationError(
            f"ComfyUI prompt node {prompt_node!r} was not found. Export an API workflow and set --prompt-node."
        )
    inputs = node.get("inputs")
    if not isinstance(inputs, dict) or "text" not in inputs:
        raise ImageGenerationError(
            f"ComfyUI node {prompt_node!r} has no 'inputs.text'. Select a positive CLIP Text Encode node."
        )
    inputs["text"] = prompt
    return copied


def generate_comfyui_image(
    *, prompt: str, output_path: Path, workflow_path: Path, prompt_node: str,
    base_url: str = "http://127.0.0.1:8188", timeout_seconds: int = 300,
) -> dict:
    """Generate an image through a locally running ComfyUI server; no cloud API key needed."""
    try:
        workflow = json.loads(workflow_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ImageGenerationError(f"ComfyUI workflow file not found: {workflow_path}") from exc
    except json.JSONDecodeError as exc:
        raise ImageGenerationError(f"Invalid ComfyUI workflow JSON: {exc}") from exc
    if not isinstance(workflow, dict):
        raise ImageGenerationError("ComfyUI workflow must be an API-format JSON object.")
    workflow = prepare_comfyui_workflow(workflow, prompt_node, prompt)
    client_id = str(uuid.uuid4())
    base_url = base_url.rstrip("/")
    queued = _request_json(
        f"{base_url}/prompt",
        payload={"prompt": workflow, "client_id": client_id},
        timeout=30,
    )
    prompt_id = queued.get("prompt_id")
    if not prompt_id:
        raise ImageGenerationError(f"ComfyUI did not return prompt_id: {queued}")
    deadline = time.monotonic() + timeout_seconds
    history = None
    while time.monotonic() < deadline:
        response = _request_json(f"{base_url}/history/{prompt_id}", timeout=30)
        history = response.get(prompt_id)
        if history:
            break
        time.sleep(1.5)
    if not history:
        raise ImageGenerationError(f"Timed out waiting for ComfyUI job {prompt_id}.")
    outputs = history.get("outputs", {})
    image_info = next(
        (image for output in outputs.values() for image in output.get("images", [])),
        None,
    )
    if not image_info:
        raise ImageGenerationError(
            "ComfyUI job completed without an image output. Ensure the workflow contains a Save Image node."
        )
    query = urlencode({
        "filename": image_info["filename"],
        "subfolder": image_info.get("subfolder", ""),
        "type": image_info.get("type", "output"),
    })
    try:
        with urlopen(f"{base_url}/view?{query}", timeout=60) as response:
            image_bytes = response.read()
    except (HTTPError, URLError, TimeoutError) as exc:
        raise ImageGenerationError(f"Could not download generated image from ComfyUI: {exc}") from exc
    if not image_bytes.startswith(b"\x89PNG\r\n\x1a\n"):
        raise ImageGenerationError("ComfyUI output was not a PNG; no asset was saved.")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(image_bytes)
    return {
        "provider": "comfyui-local",
        "model": image_info.get("type", "local-workflow"),
        "media_type": "image/png",
        "bytes": len(image_bytes),
        "prompt_id": prompt_id,
    }
