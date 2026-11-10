
import json
from pathlib import Path
from typing import Any


def load_json_safely(file_path: str | Path) -> dict[str, Any]:
    """
    Load a JSON file safely.

    Returns:
        success: Whether loading succeeded.
        data: Loaded JSON data, or None on failure.
        error: Error description, or None on success.
        file_path: Path of the requested file.
    """

    path = Path(file_path)

    result = {
        "success": False,
        "data": None,
        "error": None,
        "file_path": str(path)
    }

    try:
        if not path.exists():
            raise FileNotFoundError("JSON file does not exist.")

        if not path.is_file():
            raise ValueError("The supplied path is not a file.")

        if path.stat().st_size == 0:
            raise ValueError("JSON file is empty.")

        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)

        result["success"] = True
        result["data"] = data

    except FileNotFoundError as exc:
        result["error"] = str(exc)

    except json.JSONDecodeError as exc:
        result["error"] = (
            f"Invalid JSON at line {exc.lineno}, "
            f"column {exc.colno}: {exc.msg}"
        )

    except PermissionError:
        result["error"] = "Permission denied while reading the file."

    except (OSError, ValueError) as exc:
        result["error"] = str(exc)

    return result
