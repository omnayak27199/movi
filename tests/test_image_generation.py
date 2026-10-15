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


if __name__ == "__main__":
    unittest.main()
