
import importlib.util
import tempfile
import unittest
from pathlib import Path


# --------------------------------------------------
# LOAD ERROR LOGGER MODULE
# --------------------------------------------------

module_path = (
    Path(__file__).resolve().parents[1]
    / "06_error_handling"
    / "error_logger.py"
)

spec = importlib.util.spec_from_file_location(
    "error_logger",
    module_path
)

if spec is None or spec.loader is None:
    raise ImportError(
        f"Unable to load error_logger from: {module_path}"
    )

error_logger_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(error_logger_module)

get_logger = error_logger_module.get_logger


# --------------------------------------------------
# TEST CLASS
# --------------------------------------------------

class TestZecPathLogger(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()

        self.log_file = (
            Path(self.temp_dir.name) / "test_zecpath.log"
        )

        self.logger = get_logger(
            module_name="test_module",
            log_file=self.log_file
        )

    def tearDown(self):
        # Close handlers to release the temporary log file.
        for handler in self.logger.logger.handlers[:]:
            handler.flush()
            handler.close()
            self.logger.logger.removeHandler(handler)

        self.temp_dir.cleanup()

    def read_log(self):
        return self.log_file.read_text(
            encoding="utf-8"
        )

    def test_info_logging(self):
        self.logger.info("Test information message")

        content = self.read_log()

        self.assertIn("INFO", content)
        self.assertIn("Test information message", content)

    def test_warning_logging(self):
        self.logger.warning("Test warning message")

        content = self.read_log()

        self.assertIn("WARNING", content)
        self.assertIn("Test warning message", content)

    def test_error_logging(self):
        self.logger.error("Test error message")

        content = self.read_log()

        self.assertIn("ERROR", content)
        self.assertIn("Test error message", content)

    def test_exception_logging(self):
        try:
            raise ValueError("Sample test exception")

        except ValueError:
            self.logger.exception(
                "Exception test message"
            )

        content = self.read_log()

        self.assertIn("ERROR", content)
        self.assertIn("Exception test message", content)
        self.assertIn("Traceback", content)
        self.assertIn("ValueError", content)

    def test_module_name_logging(self):
        self.logger.info("Module verification")

        content = self.read_log()

        self.assertIn(
            "zecpath.day65.test_module",
            content
        )


# --------------------------------------------------
# RUN TESTS
# --------------------------------------------------

if __name__ == "__main__":
    unittest.main(verbosity=2)
