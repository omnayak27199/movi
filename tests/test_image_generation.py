import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from movi.image_generation import ImageGenerationError, generate_openai_image


class ImageGenerationTests(unittest.TestCase):
    def test_missing_api_key_fails_before_network_or_file_write(self):
        with patch.dict(os.environ, {}, clear=True):
            with tempfile.TemporaryDirectory() as tmp:
                output = Path(tmp) / "candidate.png"
                with self.assertRaisesRegex(ImageGenerationError, "OPENAI_API_KEY"):
                    generate_openai_image(prompt="test", output_path=output)
                self.assertFalse(output.exists())

    def test_comfyui_workflow_replaces_prompt_without_mutating_original(self):
        from movi.image_generation import prepare_comfyui_workflow
        original = {"6": {"inputs": {"text": "old prompt", "clip": ["4", 0]}, "class_type": "CLIPTextEncode"}}
        updated = prepare_comfyui_workflow(original, "6", "new prompt")
        self.assertEqual(updated["6"]["inputs"]["text"], "new prompt")
        self.assertEqual(original["6"]["inputs"]["text"], "old prompt")

    def test_comfyui_workflow_rejects_unknown_prompt_node(self):
        from movi.image_generation import prepare_comfyui_workflow
        with self.assertRaisesRegex(ImageGenerationError, "was not found"):
            prepare_comfyui_workflow({}, "404", "prompt")


if __name__ == "__main__":
    unittest.main()
