import json
import os

from communication_scorer import CommunicationScorer


def main():

    scorer = CommunicationScorer()

    sample_responses = [
        {
            "sample_id": "COMM_001",
            "candidate_id": "candidate_006",
            "question_id": "HR_TEAM_001",
            "type": "strong_response",
            "response": (
                "During my final-year project, I worked with "
                "three team members. First, I handled the "
                "backend development using Python and Django. "
                "Then, I coordinated with the frontend team "
                "to integrate the APIs. Finally, we successfully "
                "completed the project together."
            )
        },
        {
            "sample_id": "COMM_002",
            "candidate_id": "candidate_007",
            "question_id": "HR_TEAM_001",
            "type": "simple_response",
            "response": (
                "I worked on a project with my team."
            )
        },
        {
            "sample_id": "COMM_003",
            "candidate_id": "candidate_008",
            "question_id": "HR_TEAM_001",
            "type": "filler_words",
            "response": (
                "Um, I think, uh, I worked with a team "
                "and, um, we developed a project together."
            )
        },
        {
            "sample_id": "COMM_004",
            "candidate_id": "candidate_009",
            "question_id": "HR_TEAM_001",
            "type": "poor_structure",
            "response": (
                "I worked project team backend and then "
                "some testing and yes it was good."
            )
        },
        {
            "sample_id": "COMM_005",
            "candidate_id": "candidate_010",
            "question_id": "HR_TEAM_001",
            "type": "short_response",
            "response": "Yes, I did."
        }
    ]

    results = []

    for sample in sample_responses:

        result = scorer.analyze_response(
            candidate_id=sample["candidate_id"],
            question_id=sample["question_id"],
            response=sample["response"]
        )

        result["sample_id"] = sample["sample_id"]
        result["sample_type"] = sample["type"]

        results.append(result)

    results_dir = os.path.join(
        os.path.dirname(__file__),
        "results"
    )

    os.makedirs(results_dir, exist_ok=True)

    output_file = os.path.join(
        results_dir,
        "sample_communication_outputs.json"
    )

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            results,
            file,
            indent=4
        )

    print("DAY 35 — SAMPLE COMMUNICATION OUTPUTS")
    print("=" * 50)

    for result in results:

        print(
            f"\n{result['sample_id']} — "
            f"{result['sample_type']}"
        )

        print(
            f"Candidate: "
            f"{result['candidate_id']}"
        )

        print(
            f"Word Count: "
            f"{result['word_count']}"
        )

        print(
            f"Fluency: "
            f"{result['fluency_score']}"
        )

        print(
            f"Grammar: "
            f"{result['grammar_score']}"
        )

        print(
            f"Vocabulary: "
            f"{result['vocabulary_score']}"
        )

        print(
            f"Clarity: "
            f"{result['clarity_score']}"
        )

        print(
            f"Structure: "
            f"{result['structure_score']}"
        )

        print(
            f"Filler Words: "
            f"{result['filler_word_count']}"
        )

        print(
            f"Communication Score: "
            f"{result['communication_score']}/100"
        )

    print("\n" + "=" * 50)
    print(
        f"Saved Results: {output_file}"
    )


if __name__ == "__main__":
    main()