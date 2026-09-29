from fastapi import FastAPI

app = FastAPI(
    title="DataSentinel AI",
    description="Evidence-driven AI platform for data reliability",
    version="0.1.0",
)


@app.get("/")
def root():
    return {
        "project": "DataSentinel AI",
        "status": "running",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


