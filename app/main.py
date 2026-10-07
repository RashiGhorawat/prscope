from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.pr_routes import router as pr_router
from app.routes.dashboard_routes import router as dashboard_router


app = FastAPI(
    title="PRScope",
    description="AI-Powered Pull Request Risk Analyzer",
    version="1.0.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {"message": "PRScope API is running"}


@app.get("/health")
def health():
    return {"status": "healthy"}


app.include_router(pr_router)
app.include_router(dashboard_router)