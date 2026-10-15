# MOVI — Animated Series Production Toolkit

**Series:** *VANAR: WILD CODE*  
**Target:** cinematic 3D animated episodes of approximately 27 minutes  
**Status:** production-planning CLI; media generation and final rendering are not yet integrated.

MOVI is a Python CLI and structured story workspace for producing a consistent long-running animated series. It keeps episode plans, character profiles, screenplay drafts, shot manifests, production asset metadata, voice direction, music notes, and continuity data versioned in Git.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\\Scripts\\activate
python -m pip install -e .

movi validate
movi plan 1
movi screenplay 1
movi storyboard 1
movi status
movi assets list
```

## Commands

- `movi validate` checks core series JSON, Episode 1's shot manifest, and asset registry.
- `movi plan N` prints the outline for episode N.
- `movi screenplay N` prints a screenplay draft when one exists.
- `movi storyboard N` prints structured shot timing, location, characters, visuals, and audio cues.
- `movi status` reports planning and media-production implementation status.
- `movi assets list` lists registered production assets.
- `movi assets register` registers a planned/generated/approved asset with provenance and licensing metadata.
- `movi render N` is intentionally a placeholder and exits non-zero; it does not generate video.

### Register a planned character reference

```bash
movi assets register \\
  --id char-ayaan-ref-v1 \\
  --type character_reference \\
  --path assets/characters/ayaan/reference-v1.png \\
  --status planned \\
  --provider example-provider \\
  --model example-model \\
  --prompt "Use the approved Ayaan character reference prompt." \\
  --license-note "Review provider terms before publication" \\
  --episode 1
```

The planned path does not need to exist until the asset is generated. To mark an asset `generated` or `approved`, the file must exist in the repository workspace. An approved asset also needs an explicit license note. Do not commit API keys or private credentials.

## Production assets

- `series/characters.json` — character identities, voice direction, and visual locks.
- `series/characters/reference-prompts.md` — character reference prompt pack; images are not generated yet.
- `series/episodes.json` — episode outlines.
- `series/screenplays/` — screenplay drafts.
- `series/storyboards/episode-001.json` — machine-readable 29-shot manifest.
- `series/storyboards/episode-001-shot-plan.md` — human-readable shot and animatic blueprint.
- `assets/registry.json` — asset IDs, paths, generation provenance, approval and licensing notes.
- `series/continuity.yaml` — world and story-continuity rules.
- `music/` — original theme direction and score/SFX notes.
- `docs/PROVIDERS.md` — planned provider integration boundary.
- `src/movi/` — CLI and pipeline scaffold.

## Honest status

MOVI does **not** yet generate a finished 27-minute animated MP4. Character image generation, voice recording/TTS, music generation, video generation, clip assembly, and rendered-episode QA remain unimplemented. Storyboard timings are editorial targets and must be checked in a timed animatic.

## Roadmap

1. Validate story, character, episode, and storyboard data.
2. Track all planned/generated assets and their licensing/provenance.
3. Produce approved character reference sheets and environment keyframes.
4. Build a timed animatic and verify runtime.
5. Add configurable adapters for dialogue, voice, music, shot/image generation, and video assembly.
6. Add retries, caching, continuity checks, cost limits, and preview-render QA.

## Security and publishing

Keep provider credentials in environment variables or an untracked local config. Never commit API keys. Check licenses and usage terms for voices, music, models, and generated assets before publishing. The story is an original modern fantasy inspired by devotional themes and should portray Hanuman ji respectfully.

## License

See [LICENSE](LICENSE).
