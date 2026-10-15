import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class SeriesDataTests(unittest.TestCase):
    def test_characters_file_is_valid_and_has_characters(self):
        data = json.loads((ROOT / "series/characters.json").read_text(encoding="utf-8"))
        self.assertTrue(data["characters"])
        ids = [item["id"] for item in data["characters"]]
        self.assertEqual(len(ids), len(set(ids)))

    def test_episode_numbers_are_unique_and_have_scene_beats(self):
        data = json.loads((ROOT / "series/episodes.json").read_text(encoding="utf-8"))
        episodes = data["episodes"]
        numbers = [item["number"] for item in episodes]
        self.assertEqual(len(numbers), len(set(numbers)))
        self.assertTrue(all(item["scenes"] for item in episodes))
        self.assertTrue(all(scene.get("beat") for ep in episodes for scene in ep["scenes"]))

if __name__ == "__main__":
    unittest.main()
