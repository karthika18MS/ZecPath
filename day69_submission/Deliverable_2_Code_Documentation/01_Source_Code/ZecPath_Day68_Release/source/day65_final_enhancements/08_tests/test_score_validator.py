
import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

SIMULATION_ROOT = (
    PROJECT_ROOT
    / "day63_demo_dataset"
    / "06_end_to_end_simulation"
)

sys.path.insert(0, str(SIMULATION_ROOT))

from validators.score_validator import ScoreValidator


WEIGHTS = {
    "ats": 0.15,
    "hr": 0.15,
    "aptitude": 0.15,
    "technical": 0.25,
    "machine_test": 0.30,
}


class TestScoreValidator(unittest.TestCase):

    def test_valid_score(self):
        result = ScoreValidator.validate_score(85)
        self.assertTrue(result["valid"])

    def test_score_above_100(self):
        result = ScoreValidator.validate_score(105)
        self.assertFalse(result["valid"])

    def test_negative_score(self):
        result = ScoreValidator.validate_score(-5)
        self.assertFalse(result["valid"])

    def test_boolean_score(self):
        result = ScoreValidator.validate_score(True)
        self.assertFalse(result["valid"])

    def test_missing_score(self):
        result = ScoreValidator.validate_score(None)
        self.assertEqual(result["status"], "MISSING")

    def test_valid_weights(self):
        result = ScoreValidator.validate_weights(WEIGHTS)
        self.assertTrue(result["valid"])

    def test_invalid_weights(self):
        invalid_weights = dict(WEIGHTS)
        invalid_weights["ats"] = 0.50

        result = ScoreValidator.validate_weights(invalid_weights)
        self.assertFalse(result["valid"])

    def test_nan_score(self):
        result = ScoreValidator.validate_score(float("nan"))
        self.assertFalse(result["valid"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
