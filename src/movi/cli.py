"""Command-line interface for MOVI."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]

def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise ValueError(f"Required file not found: {path}")
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in {path}: {exc}")

def validate() -> int:
    errors = []
    for rel in ("series/characters.json", "series/episodes.json"):
        try:
            data = load_json(ROOT / rel)
            if not isinstance(data, (dict, list)):
                errors.append(f"{rel}: root must be a JSON object or array")
        except ValueError as exc:
            errors.append(str(exc))
    if errors:
        print("MOVI validation failed:")
        for err in errors:
            print(f" - {err}")
        return 1
    print("MOVI validation passed: character and episode JSON files are valid.")
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
    path = ROOT / "series" / "screenplays" / f"episode-{episode_number:03d}-"
    matches = sorted((ROOT / "series" / "screenplays").glob(f"episode-{episode_number:03d}-*.md"))
    if not matches:
        print(f"No screenplay draft found for episode {episode_number}.", file=sys.stderr)
        return 2
    print(matches[0].read_text(encoding="utf-8"))
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
    sub.add_parser("validate", help="Validate core series data")
    p_plan = sub.add_parser("plan", help="Print an episode outline")
    p_plan.add_argument("episode", type=int)
    p_screenplay = sub.add_parser("screenplay", help="Print a screenplay draft")
    p_screenplay.add_argument("episode", type=int)
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
        if args.command == "render":
            return render(args.episode)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
