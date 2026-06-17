from fastapi import FastAPI

from app.database import Base, engine
from app.routers.weather import router as weather_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Weather Backend API",
    description="""
Backend technical assessment for AI Engineer Intern.

Built by Aldenir Flauzino.

This API allows users to search weather by location and date range,
validate location data, retrieve real weather information from Open-Meteo,
store results in SQLite, perform CRUD operations, and export saved data.

About Product Manager Accelerator:
Product Manager Accelerator supports professionals interested in product
management and technology careers through practical learning, mentorship,
and career development.
""",
    version="1.0.0",
)

app.include_router(weather_router)


@app.get("/")
def root():
    return {
        "message": "Weather Backend API",
        "built_by": "Aldenir Flauzino",
        "assessment_completed": "Tech Assessment #2 - Backend Engineers",
        "docs": "/docs",
    }


@app.get("/health")
def health_check():
    return {"status": "ok"}