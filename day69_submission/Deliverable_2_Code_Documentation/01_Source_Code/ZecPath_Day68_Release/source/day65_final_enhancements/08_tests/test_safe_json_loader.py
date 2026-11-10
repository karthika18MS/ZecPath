
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


# --------------------------------------------------
# LOAD SAFE JSON LOADER MODULE
# --------------------------------------------------

module_path = (
    Path(__file__).resolve().parents[1]
    / "06_error_handling"
    / "safe_json_loader.py"
)

spec = importlib.util.spec_from_file_location(
    "safe_json_loader",
    module_path
)

if spec is None or spec.loader is None:
    raise ImportError(
        f"Unable to load safe_json_loader from: {module_path}"
    )

safe_json_loader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(safe_json_loader)

load_json_safely = safe_json_loader.load_json_safely


# --------------------------------------------------
# SAFE JSON LOADER TEST CASES
# --------------------------------------------------

class TestSafeJsonLoader(unittest.TestCase):

    def test_valid_json(self):
        """Test loading a valid JSON file."""

        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "valid.json"

            path.write_text(
                json.dumps({"candidate_id": "CAND001"}),
                encoding="utf-8"
            )

            result = load_json_safely(path)

            self.assertTrue(result["success"])
            self.assertEqual(
                result["data"]["candidate_id"],
                "CAND001"
            )
            self.assertIsNone(result["error"])

    def test_missing_file(self):
        """Test handling of a missing JSON file."""

        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "missing.json"

            result = load_json_safely(path)

            self.assertFalse(result["success"])
            self.assertIsNotNone(result["error"])
            self.assertIsNone(result["data"])

    def test_empty_file(self):
        """Test handling of an empty JSON file."""

        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "empty.json"

            path.write_text("", encoding="utf-8")

            result = load_json_safely(path)

            self.assertFalse(result["success"])
            self.assertIn(
                "empty",
                result["error"].lower()
            )

    def test_invalid_json(self):
        """Test handling of malformed JSON."""

        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "invalid.json"

            path.write_text(
                '{"candidate_id": ',
                encoding="utf-8"
            )

            result = load_json_safely(path)

            self.assertFalse(result["success"])
            self.assertIn(
                "Invalid JSON",
                result["error"]
            )

    def test_json_array(self):
        """Test loading a valid JSON array."""

        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "array.json"

            path.write_text(
                '["CAND001", "CAND002"]',
                encoding="utf-8"
            )

            result = load_json_safely(path)

            self.assertTrue(result["success"])
            self.assertEqual(
                result["data"],
                ["CAND001", "CAND002"]
            )


# --------------------------------------------------
# RUN TESTS
# --------------------------------------------------

if __name__ == "__main__":
    unittest.main(verbosity=2)
