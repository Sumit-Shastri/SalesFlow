from pathlib import Path

import pandas as pd
from fastapi import APIRouter, File, HTTPException, UploadFile

from app.services.loader import load_sales_file
from app.services.session_store import create_session

router = APIRouter(prefix="/api", tags=["Sales Data"])


@router.post("/upload")
async def upload_sales_file(file: UploadFile = File(...)):

    filename = file.filename or ""

    if Path(filename).suffix.lower() not in {
        ".csv", ".xlsx", ".xls"
    }:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file format. Upload CSV or Excel."
        )

    session = None

    try:
        # Starlette has already spooled the multipart upload to a temporary
        # file. Reading that handle directly avoids a Python 3.14 threadpool
        # compatibility hang while preserving the same uploaded bytes.
        file_content = file.file.read()

        # Store the uploaded file for subsequent workflow stages.
        session = create_session(filename, file_content)

        # Load the stored file to generate the preview.
        df = load_sales_file(str(session["file_path"]))

        if df.empty:
            raise ValueError(
                "The file contains no sales records."
            )

        return {
            "analysis_id": session["analysis_id"],
            "message": (
                "File uploaded successfully. "
                "Preview your data before validation."
            ),
            "filename": filename,
            "total_records": len(df),
            "columns": df.columns.tolist(),
            # Pandas represents blank CSV cells as NaN, which strict JSON
            # responses cannot encode. The upload stage only converts those
            # display values to null; validation and cleaning remain unchanged.
            "preview": df.head(5).astype(object).where(pd.notna(df.head(5)), None).to_dict(orient="records")
        }

    except (ValueError, FileNotFoundError) as exc:
        # Remove the session if the uploaded file cannot be used.
        if session:
            import shutil
            shutil.rmtree(session["session_dir"], ignore_errors=True)

        raise HTTPException(
            status_code=400,
            detail=str(exc)
        ) from exc

    except Exception as exc:
        if session:
            import shutil
            shutil.rmtree(session["session_dir"], ignore_errors=True)

        raise HTTPException(
            status_code=500,
            detail="Unable to read the uploaded file."
        ) from exc

    finally:
        file.file.close()
