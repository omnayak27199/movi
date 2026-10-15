# MOVI — Animated Series Production Toolkit

**Series:** *VANAR: WILD CODE*  
**Target:** cinematic 3D animated episodes of approximately 27 minutes  
**Status:** production-planning CLI; media generation and final rendering are not yet integrated.

MOVI is a Python CLI and structured story workspace for producing a consistent long-running animated series. It keeps episode plans, character profiles, screenplay drafts, shot manifests, voice direction, music notes, and continuity data versioned in Git.

## Current commands

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\\Scripts\\activate
python -m pip install -e .

movi validate
movi plan 1
movi screenplay 1
movi storyboard 1
movi status
```

- `movi validate` checks core series JSON and the Episode 1 shot manifest.
- `movi plan N` prints the outline for episode N.
- `movi screenplay N` prints a screenplay draft when one exists.
- `movi storyboard N` prints structured shot timing, location, characters, visuals, and audio cues.
- `movi status` reports planning and media-production implementation status.
- `movi render N` is intentionally a placeholder and exits non-zero; it does not generate video.

## Current production assets

- `series/characters.json` — character identities, voice direction, and visual locks.
- `series/characters/reference-prompts.md` — character reference prompt pack; images are not generated yet.
- `series/episodes.json` — episode outlines.
- `series/screenplays/` — screenplay drafts.
- `series/storyboards/episode-001.json` — machine-readable 29-shot manifest for Episode 1.
- `series/storyboards/episode-001-shot-plan.md` — human-readable shot and animatic blueprint.
- `series/continuity.yaml` — world and story-continuity rules.
- `music/opening_theme.md` and `music/score_and_sfx_guide.md` — original theme direction and score/SFX notes.
- `docs/PROVIDERS.md` — planned provider integration boundary.
- `src/movi/` — CLI and pipeline scaffold.

## Honest status

MOVI does **not** yet generate a finished 27-minute animated MP4. Character image generation, voice recording/TTS, music generation, video generation, clip assembly, and rendered-episode QA remain unimplemented. The storyboard timings are editorial targets and must be checked in a timed animatic.

## Roadmap

1. Validate story, character, episode, and storyboard data.
2. Produce approved character reference sheets and environment keyframes.
3. Build a timed animatic and verify the episode runtime.
4. Add configurable adapters for dialogue, voice, music, shot/image generation, and video assembly.
5. Add stable asset IDs, retries, caching, continuity checks, cost limits, and provider/license tracking.
6. Add preview renders and automated QA before longer renders.

## Security and publishing

Keep provider credentials in environment variables or an untracked local config. Never commit API keys. Check licenses and usage terms for voices, music, models, and generated assets before publishing. The story is an original modern fantasy inspired by devotional themes and should portray Hanuman ji respectfully.

## License

See [LICENSE](LICENSE).
