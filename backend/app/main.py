from fastapi import FastAPI

app = FastAPI(
    title="SalesFlow API",
    description="Backend API for the SalesFlow sales analytics platform.",
    version="1.0.0",
)


@app.get("/")
def root():
    return {
        "message": "Welcome to SalesFlow API",
        "status": "running",
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
    }