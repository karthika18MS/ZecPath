"""Focused tests for Day 63 JD skill coverage and spelling aliases."""

import importlib.util
import sys
import types
import unittest
from pathlib import Path


PROJECT = Path(__file__).resolve().parent
fake_package = types.ModuleType("day18_optimization")
fake_engine = types.ModuleType("day18_optimization.optimized_ats_engine")
fake_engine.SKILL_WEIGHT = 0.35
fake_package.optimized_ats_engine = fake_engine
sys.modules.setdefault("day18_optimization", fake_package)
sys.modules.setdefault("day18_optimization.optimized_ats_engine", fake_engine)

pipeline_path = next(
    path
    for path in (
        PROJECT / "day63_ats_scoring_pipeline.py",
        PROJECT / "ats_scoring_pipeline.py",
    )
    if path.is_file()
)
spec = importlib.util.spec_from_file_location("day63_ats_scoring_pipeline", pipeline_path)
pipeline = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pipeline)


class Day63SkillValidationTests(unittest.TestCase):
    def test_all_mandatory_requirements_are_scored(self):
        jd = {
            "mandatory_skills": ["React.js", "Node.js", "Express.js", "MongoDB", "JavaScript"],
            "preferred_skills": ["Git", "REST API Development"],
        }
        resume = "React, Node.js and MongoDB; Git and REST APIs."
        result = pipeline.evaluate_jd_skills(jd, resume)

        self.assertEqual(result["required_skills"], jd["mandatory_skills"])
        self.assertEqual(result["matched_skills"], ["React.js", "Node.js", "MongoDB"])
        self.assertEqual(result["missing_skills"], ["Express.js", "JavaScript"])
        self.assertEqual(result["score"], 60.0)
        self.assertEqual(result["matched_preferred_skills"], ["Git", "REST API Development"])

    def test_does_not_match_partial_skill_names(self):
        result = pipeline.evaluate_jd_skills(
            {"mandatory_skills": ["Java"], "preferred_skills": []},
            "Experienced with JavaScript only.",
        )
        self.assertEqual(result["missing_skills"], ["Java"])
        self.assertEqual(result["score"], 0.0)


if __name__ == "__main__":
    unittest.main()
