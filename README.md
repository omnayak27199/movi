# MOVI — Animated Series Production Toolkit

**Series:** *VANAR: WILD CODE*  
**Target:** cinematic 3D animated episodes of approximately 27 minutes  
**Status:** starter scaffold. Planning and validation come first; rendering adapters are not yet implemented.

MOVI is a Python CLI and structured story workspace for producing a consistent long-running animated series. It keeps episode plans, character profiles, voice direction, music notes, and continuity data versioned in Git.

## Current scope

- Structured character and episode data.
- Persistent world and story-continuity notes.
- Opening-theme and score/SFX direction.
- CLI interface for planning and validating episode data.
- Provider interface scaffolding for future text, voice, music, and animation integrations.
- GitHub Actions validation workflow.

## Honest status

This repository does **not** yet generate a finished 27-minute animated MP4. The render command remains a scaffold until provider adapters, credentials, orchestration, asset management, and video assembly are implemented and tested. We will build this incrementally and verify each milestone.

## Quick start

Requires Python 3.11+.

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\\Scripts\\activate
python -m pip install -e .
movi validate
movi plan 1
```

Alternatively:

```bash
PYTHONPATH=src python -m movi.cli validate
PYTHONPATH=src python -m movi.cli plan 1
```

## Repository layout

- `series/characters.json` — character identities and performance guidance.
- `series/episodes.json` — episode plan data.
- `series/continuity.yaml` — world and story continuity.
- `music/opening_theme.md` — original theme direction.
- `music/score_and_sfx_guide.md` — score and sound-design notes.
- `docs/PROVIDERS.md` — provider architecture.
- `src/movi/` — CLI and pipeline scaffold.
- `scripts/` — convenience scripts.

## Roadmap

1. Validate story, character, episode, and continuity data.
2. Expand outlines into scene-by-scene scripts with timing targets.
3. Add adapters for dialogue, suitable TTS, music, shot/image generation, and video assembly.
4. Add stable asset IDs, retries, caching, continuity checks, and cost limits.
5. Add preview renders and automated QA before longer renders.

## Security and publishing

Keep provider credentials in environment variables or an untracked local config. Never commit API keys. Check licenses and usage terms for voices, music, models, and generated assets before publishing. The story is an original modern fantasy inspired by devotional themes and should portray Hanuman ji respectfully.

## License

See [LICENSE](LICENSE).
