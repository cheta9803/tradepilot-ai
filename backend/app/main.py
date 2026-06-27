from fastapi import FastAPI

app = FastAPI(
    title="TradePilot AI",
    version="1.0.0",
    description="AI Powered Intraday Trading Assistant"
)


@app.get("/")
def root():
    return {
        "application": "TradePilot AI",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }