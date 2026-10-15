# Image generation setup

MOVI includes opt-in OpenAI API and local ComfyUI adapters for character reference candidates. They are not called by `movi validate`, `movi status`, or planning commands; generation runs only when explicitly requested.

## Setup in GitHub Codespaces

1. Confirm your OpenAI API account has API access and billing configured.
2. In the Codespaces terminal, set the key for the current terminal session (paste your real key locally; do not send it in chat or commit it):

```bash
export OPENAI_API_KEY="your-api-key"
```

For persistent use, add `OPENAI_API_KEY` under your repository's **Settings → Secrets and variables → Codespaces**. Reopen/restart the Codespace if needed so the environment variable is available.

## Generate Ayaan's candidate

```bash
git pull origin main
python -m pip install -e .
movi validate
movi generate character-reference Ayaan
movi assets list
```

The default model is `gpt-image-1`; you can select another supported image model explicitly with `--model MODEL_ID`. Model availability, image pricing, size support, and account access can change; check your provider dashboard before generating.

Expected output path: `assets/generated/characters/ayaan-reference-v1.png`. Generated media is gitignored by default, so it stays in your Codespace unless you intentionally choose to version or store it elsewhere. The metadata entry is saved to `assets/registry.json`; commit that registry update if you want the record shared in GitHub. Do not commit API keys.

## Approval gate

The command registers the result as `generated`, **not** `approved`. Review the left-ear notch, amber-brown fur, teal jacket, view consistency, anatomy, and expressions. Verify the provider's current terms and project usage rights before publication. Only then should the asset be approved and used as a visual reference for episode shots.

The adapter currently generates still images only. It does not generate voices, animate characters, assemble shots, or render a finished episode.

## Free local generation with ComfyUI (no image API key)

This path runs inference on your own Mac. It has no per-image cloud API fee, but needs local storage, compute, and a model checkpoint whose licence permits your intended use. The MOVI Codespace cannot access the model running on your Mac through `127.0.0.1`; run the command below in the Mac terminal where ComfyUI is running, or configure a reachable server URL carefully.

1. Install ComfyUI for macOS from [the official download page](https://www.comfy.org/download). Apple Silicon is supported. See the official [ComfyUI repository](https://github.com/Comfy-Org/ComfyUI) for setup and model instructions.
2. Download a compatible image checkpoint using ComfyUI's model manager or documented setup. Review the model licence, especially if VANAR becomes commercial.
3. Start ComfyUI and open its UI (normally `http://127.0.0.1:8188`). Build a basic text-to-image workflow with a positive CLIP text-encode node and a Save Image node.
4. Export the workflow in **API format**. Put that JSON file somewhere local and identify the positive text-encode node ID in the exported JSON; it must have `inputs.text`.
5. In the same terminal where the MOVI repository is installed, run:

```bash
movi generate character-reference Ayaan \
  --provider comfyui \
  --workflow /absolute/path/to/workflow_api.json \
  --prompt-node 6
```

Replace the example path and node ID with your actual workflow file and positive prompt node ID. If ComfyUI uses a different URL, add `--base-url http://127.0.0.1:8188` with the correct local address.

Expected output: `assets/generated/characters/ayaan-reference-v1.png`. MOVI waits for the local job, downloads the PNG, and registers it as `generated`, not `approved`. Check the image before using it in episode shots.

**Important:** the OpenAI provider remains the default, so include `--provider comfyui` to avoid API-key use. Do not expose a ComfyUI server to the public internet without proper security controls.
