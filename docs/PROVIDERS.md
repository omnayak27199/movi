# Provider integration plan

MOVI separates story planning from media generation so that providers can be swapped without rewriting the series bible.

## Planned stages

1. **Script:** expand episode beats into timed scenes, dialogue, action, and shot lists.
2. **Voice:** generate or record dialogue using voices that are licensed and approved for the project.
3. **Sound:** create or license score, ambience, Foley, and effects.
4. **Visuals:** create approved character references and shot assets with stable character/style references.
5. **Assembly:** compose shots, dialogue, ambience, subtitles, transitions, and credits into a reviewable cut.
6. **QA:** verify duration, missing assets, audio peaks, subtitle timing, continuity, and policy/licensing checks.

## Provider contract

Each adapter should accept structured input and return a result with:
- provider/model identifier;
- asset path or URI;
- duration and media metadata when relevant;
- estimated/actual cost when available;
- retryable error details;
- license and provenance metadata.

Never store API keys in source control. Load secrets from environment variables or an ignored local configuration file.

## Current status

These are design requirements, not implemented integrations. `movi render N` intentionally reports that rendering is not configured; it must not pretend to have produced a video. Build and test one stage at a time, starting with complete screenplay generation and a low-cost animatic.
