import json
from pathlib import Path


class OptimizationReportGenerator:

    def __init__(
        self,
        output_path
    ):

        self.output_path = Path(
            output_path
        )

    # =========================================================
    # GENERATE REPORT
    # =========================================================

    def generate(
        self,
        analysis
    ):

        self.output_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        with open(
            self.output_path,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                analysis,
                file,
                indent=4
            )

        return self.output_path