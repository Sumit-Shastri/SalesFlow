from pathlib import Path
from uuid import uuid4
import json
import shutil
import tempfile


SESSION_ROOT = Path(tempfile.gettempdir()) / "salesflow_sessions"


def create_session(filename: str, file_content: bytes) -> dict:
    """
    Create a session and store the uploaded file.
    """

    analysis_id = str(uuid4())

    session_dir = SESSION_ROOT / analysis_id
    session_dir.mkdir(parents=True, exist_ok=False)

    suffix = Path(filename).suffix.lower()
    file_path = session_dir / f"original{suffix}"

    try:
        file_path.write_bytes(file_content)

        return {
            "analysis_id": analysis_id,
            "session_dir": session_dir,
            "file_path": file_path,
        }

    except Exception:
        shutil.rmtree(session_dir, ignore_errors=True)
        raise


def get_session_file(analysis_id: str) -> Path:
    """
    Retrieve the uploaded file for an existing session.
    """

    return get_session_dir(analysis_id) / _original_file_name(analysis_id)


def get_session_dir(analysis_id: str) -> Path:
    """Return a validated session directory without exposing arbitrary paths."""
    if not analysis_id or Path(analysis_id).name != analysis_id:
        raise ValueError("Invalid analysis ID.")

    session_dir = SESSION_ROOT / analysis_id

    if not session_dir.is_dir():
        raise FileNotFoundError("Analysis session not found or expired.")

    return session_dir


def _original_file_name(analysis_id: str) -> str:
    session_dir = get_session_dir(analysis_id)
    files = list(session_dir.glob("original.*"))

    if len(files) != 1 or not files[0].is_file():
        raise FileNotFoundError("Uploaded file not found for this session.")

    return files[0].name


def get_working_file(analysis_id: str) -> Path:
    """Return the normalized copy created by the validation stage."""
    path = get_session_dir(analysis_id) / "working.csv"
    if not path.is_file():
        raise FileNotFoundError("Validate the uploaded file before cleaning it.")
    return path


def get_cleaned_file(analysis_id: str) -> Path:
    """Return the cleaned copy created by the cleaning stage."""
    path = get_session_dir(analysis_id) / "cleaned.csv"
    if not path.is_file():
        raise FileNotFoundError("Clean the uploaded file before running analysis.")
    return path


def session_path(analysis_id: str, filename: str) -> Path:
    """Build a safe, session-local path for generated workflow artifacts."""
    if Path(filename).name != filename:
        raise ValueError("Invalid generated file name.")
    return get_session_dir(analysis_id) / filename


def save_json(analysis_id: str, filename: str, value: dict) -> Path:
    path = session_path(analysis_id, filename)
    path.write_text(json.dumps(value, ensure_ascii=False, allow_nan=False), encoding="utf-8")
    return path


def load_json(analysis_id: str, filename: str) -> dict:
    path = session_path(analysis_id, filename)
    if not path.is_file():
        raise FileNotFoundError(f"{filename} has not been generated for this session.")
    return json.loads(path.read_text(encoding="utf-8"))
