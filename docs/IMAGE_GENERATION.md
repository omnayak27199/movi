# Image generation setup

MOVI now includes an opt-in OpenAI Images API adapter for character reference candidates. It is not called by `movi validate`, `movi status`, or any planning command; it runs only when explicitly requested.

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
