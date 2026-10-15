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
    except ValueError as exc:
        errors.append(str(exc))
    if errors:
        print("MOVI validation failed:")
        for err in errors:
            print(f" - {err}")
        return 1
    print("MOVI validation passed: character, episode, and Episode 1 storyboard data are valid.")
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

def render(episode_number: int) -> int:
    print("Rendering is not configured yet.")
    print("No video has been generated. Configure and implement provider adapters first.")
    print(f"Requested episode: {episode_number}")
    print("See docs/PROVIDERS.md for the planned integration boundary.")
    return 3

def main() -> int:
    parser = argparse.ArgumentParser(prog="movi", description="MOVI animated-series toolkit")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("validate", help="Validate core series and storyboard data")
    p_plan = sub.add_parser("plan", help="Print an episode outline")
    p_plan.add_argument("episode", type=int)
    p_screenplay = sub.add_parser("screenplay", help="Print a screenplay draft")
    p_screenplay.add_argument("episode", type=int)
    p_storyboard = sub.add_parser("storyboard", help="Print a structured shot plan")
    p_storyboard.add_argument("episode", type=int)
    sub.add_parser("status", help="Show which production stages are implemented")
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
        if args.command == "render":
            return render(args.episode)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
