from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.upload import router as upload_router
from app.api.workflow import router as workflow_router

app = FastAPI(
    title="SalesFlow API",
    description="Backend API for the SalesFlow sales analytics platform.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload_router)
app.include_router(workflow_router)


@app.get("/")
def root():
    return {
        "message": "Welcome to SalesFlow API",
        "status": "running",
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}
