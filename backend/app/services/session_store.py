from pathlib import Path
from uuid import uuid4
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

    if not analysis_id or Path(analysis_id).name != analysis_id:
        raise ValueError("Invalid analysis ID.")

    session_dir = SESSION_ROOT / analysis_id

    if not session_dir.is_dir():
        raise FileNotFoundError("Analysis session not found or expired.")

    files = list(session_dir.glob("original.*"))

    if len(files) != 1 or not files[0].is_file():
        raise FileNotFoundError("Uploaded file not found for this session.")

    return files[0]