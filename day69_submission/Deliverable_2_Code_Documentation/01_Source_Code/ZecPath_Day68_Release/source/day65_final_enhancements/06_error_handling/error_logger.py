
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional


# --------------------------------------------------
# DEFAULT LOG FILE CONFIGURATION
# --------------------------------------------------

BASE_DIRECTORY = Path(__file__).resolve().parents[1]

LOG_DIRECTORY = (
    BASE_DIRECTORY
    / "09_final_outputs"
    / "logs"
)

DEFAULT_LOG_FILE = (
    LOG_DIRECTORY / "zecpath_day65.log"
)


# --------------------------------------------------
# CENTRALIZED LOGGER CLASS
# --------------------------------------------------

class ZecPathLogger:

    def __init__(
        self,
        module_name: str = "zecpath",
        log_file: Optional[str | Path] = None
    ):
        """
        Initialize the centralized ZecPath logger.

        Args:
            module_name: Name of the module generating logs.
            log_file: Optional custom log file path.
        """

        self.module_name = module_name

        self.log_path = (
            Path(log_file)
            if log_file
            else DEFAULT_LOG_FILE
        )

        self.log_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        logger_name = f"zecpath.day65.{module_name}"

        self.logger = logging.getLogger(logger_name)

        self.logger.setLevel(logging.INFO)
        self.logger.propagate = False

        # Avoid adding duplicate handlers.
        resolved_path = str(self.log_path.resolve())

        handler_exists = any(
            getattr(handler, "baseFilename", None)
            == resolved_path
            for handler in self.logger.handlers
        )

        if not handler_exists:

            file_handler = RotatingFileHandler(
                self.log_path,
                maxBytes=2 * 1024 * 1024,
                backupCount=5,
                encoding="utf-8"
            )

            formatter = logging.Formatter(
                fmt=(
                    "%(asctime)s | "
                    "%(levelname)s | "
                    "%(name)s | "
                    "%(message)s"
                ),
                datefmt="%Y-%m-%d %H:%M:%S"
            )

            file_handler.setFormatter(formatter)

            self.logger.addHandler(file_handler)

    # --------------------------------------------------
    # INFO LOG
    # --------------------------------------------------

    def info(self, message: str) -> None:
        self.logger.info(message)

    # --------------------------------------------------
    # WARNING LOG
    # --------------------------------------------------

    def warning(self, message: str) -> None:
        self.logger.warning(message)

    # --------------------------------------------------
    # ERROR LOG
    # --------------------------------------------------

    def error(
        self,
        message: str,
        exc_info: bool = False
    ) -> None:
        self.logger.error(
            message,
            exc_info=exc_info
        )

    # --------------------------------------------------
    # EXCEPTION LOG
    # --------------------------------------------------

    def exception(self, message: str) -> None:
        """
        Record an exception with traceback.

        Call this method inside an except block.
        """
        self.logger.exception(message)


# --------------------------------------------------
# LOGGER FACTORY
# --------------------------------------------------

def get_logger(
    module_name: str = "zecpath",
    log_file: Optional[str | Path] = None
) -> ZecPathLogger:
    """
    Create and return a ZecPath logger.
    """

    return ZecPathLogger(
        module_name=module_name,
        log_file=log_file
    )


# --------------------------------------------------
# DIRECT EXECUTION TEST
# --------------------------------------------------

if __name__ == "__main__":

    logger = get_logger("error_logger_demo")

    logger.info(
        "ZecPath Day 65 logging system initialized."
    )

    logger.warning(
        "This is a sample warning message."
    )

    logger.error(
        "This is a sample error message."
    )

    try:
        result = 10 / 0

    except ZeroDivisionError:
        logger.exception(
            "Sample exception captured successfully."
        )

    print("=" * 65)
    print("ZECPath DAY 65 - CENTRALIZED ERROR LOGGER")
    print("=" * 65)

    print("INFO log recorded.")
    print("WARNING log recorded.")
    print("ERROR log recorded.")
    print("EXCEPTION log recorded.")

    print("\nLOG FILE:")
    print(DEFAULT_LOG_FILE)

    print("\nCENTRALIZED LOGGING COMPLETED")
