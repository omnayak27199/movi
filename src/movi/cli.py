"""Command-line interface for MOVI."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
import sys

from movi.image_generation import ImageGenerationError, generate_openai_image

ROOT = Path(__file__).resolve().parents[2]
ASSET_REGISTRY = ROOT / "assets" / "registry.json"
ASSET_TYPES = {
    "character_reference", "environment_keyframe", "shot_image",
    "voice", "music", "sfx", "video", "other",
}
ASSET_STATUSES = {"planned", "generated", "approved", "rejected"}


def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise ValueError(f"Required file not found: {path}")
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in {path}: {exc}")


def save_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def validate() -> int:
    errors = []
    for rel in ("series/characters.json", "series/episodes.json"):
        try:
            data = load_json(ROOT / rel)
            if not isinstance(data, (dict, list)):
                errors.append(f"{rel}: root must be a JSON object or array")
        except (ValueError, ImageGenerationError) as exc:
            errors.append(str(exc))

    storyboard_path = ROOT / "series/storyboards/episode-001.json"
    try:
        data = load_json(storyboard_path)
        shots = data.get("shots", [])
        if not shots:
            errors.append("series/storyboards/episode-001.json: no shots defined")
        ids = [shot.get("id") for shot in shots]
        if len(ids) != len(set(ids)):
            errors.append("series/storyboards/episode-001.json: shot IDs must be unique")
        for shot in shots:
            for field in ("id", "title", "start", "end", "visual"):
                if not shot.get(field):
                    errors.append(f"series/storyboards/episode-001.json: shot missing {field}")
    except (ValueError, AttributeError) as exc:
        errors.append(str(exc))

    try:
        registry = load_json(ASSET_REGISTRY)
        assets = registry.get("assets", [])
        if not isinstance(assets, list):
            errors.append("assets/registry.json: 'assets' must be an array")
        else:
            ids = [asset.get("id") for asset in assets]
            if len(ids) != len(set(ids)):
                errors.append("assets/registry.json: asset IDs must be unique")
            required = ("id", "type", "path", "status", "license_note")
            for asset in assets:
                for field in required:
                    if not asset.get(field):
                        errors.append(f"assets/registry.json: asset missing {field}")
                if asset.get("type") not in ASSET_TYPES:
                    errors.append(f"assets/registry.json: unsupported asset type for {asset.get('id')}")
                if asset.get("status") not in ASSET_STATUSES:
                    errors.append(f"assets/registry.json: unsupported status for {asset.get('id')}")
    except (ValueError, AttributeError) as exc:
        errors.append(str(exc))

    if errors:
        print("MOVI validation failed:")
        for err in errors:
            print(f" - {err}")
        return 1
    print("MOVI validation passed: series, storyboard, and asset registry data are valid.")
    return 0


def plan(episode_number: int) -> int:
    data = load_json(ROOT / "series/episodes.json")
    episodes = data.get("episodes", []) if isinstance(data, dict) else data
    episode = next((e for e in episodes if e.get("number") == episode_number), None)
    if episode is None:
        print(f"Episode {episode_number} was not found in series/episodes.json.", file=sys.stderr)
        return 2
    print(f"# Episode {episode.get('number')}: {episode.get('title', 'Untitled')}")
    print(f"Target runtime: {episode.get('target_minutes', 27)} minutes")
    print(f"Logline: {episode.get('logline', 'Not written yet')}")
    for idx, scene in enumerate(episode.get("scenes", []), 1):
        print(f"\n{idx}. {scene.get('title', 'Scene')}")
        print(f"   Location: {scene.get('location', 'TBD')}")
        print(f"   Beat: {scene.get('beat', 'TBD')}")
    return 0


def screenplay(episode_number: int) -> int:
    folder = ROOT / "series" / "screenplays"
    matches = sorted(folder.glob(f"episode-{episode_number:03d}-*.md"))
    if not matches:
        print(f"No screenplay draft found for episode {episode_number}.", file=sys.stderr)
        return 2
    print(matches[0].read_text(encoding="utf-8"))
    return 0


def storyboard(episode_number: int) -> int:
    path = ROOT / "series" / "storyboards" / f"episode-{episode_number:03d}.json"
    try:
        data = load_json(path)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    print(f"# Episode {data.get('episode')}: {data.get('title', 'Untitled')}")
    print(f"Status: {data.get('status', 'unknown')}")
    print(f"Target runtime: {data.get('target_minutes', 27)} minutes")
    print(f"Planned shots: {len(data.get('shots', []))}")
    for shot in data.get("shots", []):
        characters = ", ".join(shot.get("characters", [])) or "environment"
        print(f"\n{shot.get('id')} [{shot.get('start')}–{shot.get('end')}] {shot.get('title')}")
        print(f"  Location: {shot.get('location', 'TBD')}")
        print(f"  Characters: {characters}")
        print(f"  Visual: {shot.get('visual', 'TBD')}")
        audio = shot.get("audio", [])
        if audio:
            print(f"  Audio: {'; '.join(audio)}")
    print("\nNote: planned timings are not validated against a rendered animatic.")
    return 0


def pipeline_status() -> int:
    stages = [
        ("story data and outline", True, "JSON data and episode outline"),
        ("screenplay drafts", True, "Episode 1 draft exists; timing is unverified"),
        ("shot manifest", True, "Episode 1 has a structured 29-shot plan"),
        ("asset registry", True, "Metadata registry exists; no media files are implied"),
        ("character reference images", False, "Prompts exist; images are not generated/approved"),
        ("voice generation/recording", False, "Not integrated"),
        ("music and sound generation", False, "Guides exist; generation/assembly not integrated"),
        ("visual shot generation", False, "Provider adapter not integrated"),
        ("video assembly", False, "Not implemented"),
        ("rendered episode QA", False, "No rendered episode exists"),
    ]
    print("# MOVI pipeline status")
    for name, done, detail in stages:
        print(f"[{'x' if done else ' '}] {name}: {detail}")
    print("\nA checked stage means its planning/scaffold exists, not that a finished episode has been produced.")
    return 0


def list_assets() -> int:
    registry = load_json(ASSET_REGISTRY)
    assets = registry.get("assets", [])
    if not assets:
        print("Asset registry is empty. Register planned assets with: movi assets register --help")
        return 0
    print(f"# MOVI assets ({len(assets)})")
    for asset in assets:
        print(f"{asset['id']} [{asset['status']}] {asset['type']}")
        print(f"  Path: {asset['path']}")
        print(f"  Provider/model: {asset.get('provider') or '—'} / {asset.get('model') or '—'}")
        print(f"  License: {asset.get('license_note', 'Unspecified')}")
    return 0


def register_asset(args: argparse.Namespace) -> int:
    if args.asset_type not in ASSET_TYPES:
        print(f"Unsupported type: {args.asset_type}", file=sys.stderr)
        return 2
    if args.status not in ASSET_STATUSES:
        print(f"Unsupported status: {args.status}", file=sys.stderr)
        return 2

    relative = PurePosixPath(args.path)
    if relative.is_absolute() or ".." in relative.parts or not args.path.strip():
        print("Asset path must be a non-empty repository-relative path without '..'.", file=sys.stderr)
        return 2
    if args.status in {"generated", "approved"} and not (ROOT / Path(*relative.parts)).is_file():
        print(f"Cannot mark asset {args.status}: file does not exist at {args.path}", file=sys.stderr)
        return 2
    if args.status == "approved" and args.license_note == "Unspecified; review before publication":
        print("Approved assets need an explicit --license-note.", file=sys.stderr)
        return 2

    registry = load_json(ASSET_REGISTRY)
    assets = registry.setdefault("assets", [])
    if any(asset.get("id") == args.asset_id for asset in assets):
        print(f"Asset ID already exists: {args.asset_id}", file=sys.stderr)
        return 2

    asset = {
        "id": args.asset_id,
        "type": args.asset_type,
        "path": relative.as_posix(),
        "status": args.status,
        "provider": args.provider or None,
        "model": args.model or None,
        "license_note": args.license_note,
        "prompt": args.prompt or None,
        "episode": args.episode,
        "shot_id": args.shot_id or None,
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "notes": args.notes or None,
    }
    assets.append(asset)
    save_json(ASSET_REGISTRY, registry)
    print(f"Registered asset {args.asset_id} [{args.status}] in assets/registry.json")
    return 0



def generate_character_reference(character_name: str, model: str) -> int:
    prompt_file = ROOT / "series" / "characters" / "reference_prompts.json"
    prompts = load_json(prompt_file)
    characters = prompts.get("characters", {})
    canonical = next((name for name in characters if name.casefold() == character_name.casefold()), None)
    if canonical is None:
        available = ", ".join(characters)
        print(f"Unknown character: {character_name}. Available: {available}", file=sys.stderr)
        return 2
    spec = characters[canonical]
    output_path = ROOT / "assets" / "generated" / "characters" / f"{canonical.lower()}-reference-v1.png"
    relative_path = output_path.relative_to(ROOT).as_posix()
    registry = load_json(ASSET_REGISTRY)
    assets = registry.setdefault("assets", [])
    asset_id = spec["asset_id"]
    if any(asset.get("id") == asset_id for asset in assets):
        print(f"Asset ID already exists: {asset_id}. Remove/revise the registry entry before regenerating.", file=sys.stderr)
        return 2
    print(f"Generating reference for {canonical} with OpenAI model {model}...")
    result = generate_openai_image(prompt=spec["prompt"], output_path=output_path, model=model)
    assets.append({
        "id": asset_id,
        "type": "character_reference",
        "path": relative_path,
        "status": "generated",
        "provider": result["provider"],
        "model": result["model"],
        "license_note": "Generated via OpenAI API; verify current account terms and usage rights before publication.",
        "prompt": spec["prompt"],
        "episode": 1,
        "shot_id": None,
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "notes": "Candidate only. Human visual consistency and quality review required before approval.",
    })
    save_json(ASSET_REGISTRY, registry)
    print(f"Generated candidate: {relative_path} ({result['bytes']} bytes)")
    print(f"Registered as {asset_id} [generated], not approved.")
    print("Review the image and verify provider terms before using it in episode shots.")
    return 0


def render(episode_number: int) -> int:
    print("Rendering is not configured yet.")
    print("No video has been generated. Configure and implement provider adapters first.")
    print(f"Requested episode: {episode_number}")
    print("See docs/PROVIDERS.md for the planned integration boundary.")
    return 3


def main() -> int:
    parser = argparse.ArgumentParser(prog="movi", description="MOVI animated-series toolkit")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("validate", help="Validate series, storyboard, and asset registry data")
    p_plan = sub.add_parser("plan", help="Print an episode outline")
    p_plan.add_argument("episode", type=int)
    p_screenplay = sub.add_parser("screenplay", help="Print a screenplay draft")
    p_screenplay.add_argument("episode", type=int)
    p_storyboard = sub.add_parser("storyboard", help="Print a structured shot plan")
    p_storyboard.add_argument("episode", type=int)
    sub.add_parser("status", help="Show which production stages are implemented")

    p_assets = sub.add_parser("assets", help="Manage production asset metadata")
    assets_sub = p_assets.add_subparsers(dest="assets_command", required=True)
    assets_sub.add_parser("list", help="List registered assets")
    p_register = assets_sub.add_parser("register", help="Register a planned or generated asset")
    p_register.add_argument("--id", dest="asset_id", required=True, help="Stable unique asset ID")
    p_register.add_argument("--type", dest="asset_type", required=True, choices=sorted(ASSET_TYPES))
    p_register.add_argument("--path", required=True, help="Repository-relative asset path")
    p_register.add_argument("--status", choices=sorted(ASSET_STATUSES), default="planned")
    p_register.add_argument("--provider", default="")
    p_register.add_argument("--model", default="")
    p_register.add_argument("--license-note", default="Unspecified; review before publication")
    p_register.add_argument("--prompt", default="")
    p_register.add_argument("--episode", type=int, default=1)
    p_register.add_argument("--shot-id", default="")
    p_register.add_argument("--notes", default="")


    p_generate = sub.add_parser("generate", help="Generate a production asset using a configured provider")
    generate_sub = p_generate.add_subparsers(dest="generate_command", required=True)
    p_character = generate_sub.add_parser("character-reference", help="Generate a candidate character reference image")
    p_character.add_argument("character", help="Character name from reference_prompts.json")
    p_character.add_argument("--provider", choices=["openai"], default="openai")
    p_character.add_argument("--model", default="gpt-image-1")

    p_render = sub.add_parser("render", help="Render an episode (not yet implemented)")
    p_render.add_argument("episode", type=int)
    args = parser.parse_args()
    try:
        if args.command == "validate":
            return validate()
        if args.command == "plan":
            return plan(args.episode)
        if args.command == "screenplay":
            return screenplay(args.episode)
        if args.command == "storyboard":
            return storyboard(args.episode)
        if args.command == "status":
            return pipeline_status()
        if args.command == "assets":
            if args.assets_command == "list":
                return list_assets()
            if args.assets_command == "register":
                return register_asset(args)
        if args.command == "generate" and args.generate_command == "character-reference":
            return generate_character_reference(args.character, args.model)
        if args.command == "render":
            return render(args.episode)
    except (ValueError, ImageGenerationError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
