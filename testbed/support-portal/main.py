"""
Support Portal — Customer Support Reply Generator
A FastAPI service that uses OpenAI GPT to generate customer support responses.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from routes.support import router as support_router
from routes.health import router as health_router

load_dotenv()

app = FastAPI(
    title="Support Portal API",
    description="AI-powered customer support reply generator",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(support_router, prefix="/api/v1/support", tags=["support"])
app.include_router(health_router, prefix="/health", tags=["health"])


@app.get("/")
async def root():
    return {"service": "support-portal", "version": "1.0.0"}
