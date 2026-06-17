import csv
import io
import json
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import WeatherRequest
from app.schemas import WeatherResponse, WeatherSearchCreate, WeatherUpdate
from app.services.weather_service import fetch_weather, resolve_location

router = APIRouter(prefix="/weather", tags=["Weather"])


@router.post("/search", response_model=WeatherResponse)
def create_weather_request(payload: WeatherSearchCreate, db: Session = Depends(get_db)):
    location = resolve_location(payload.location)

    weather_data = fetch_weather(
        latitude=location["latitude"],
        longitude=location["longitude"],
        start_date=payload.start_date,
        end_date=payload.end_date,
    )

    maps_url = (
        f"https://www.google.com/maps/search/?api=1"
        f"&query={location['latitude']},{location['longitude']}"
    )

    youtube_url = (
        "https://www.youtube.com/results?"
        f"search_query=weather+travel+guide+{payload.location.replace(' ', '+')}"
    )

    weather_data["location_context"] = {
        "google_maps_url": maps_url,
        "youtube_search_url": youtube_url,
        "description": "Additional location context generated from the resolved latitude and longitude."
    }

    record = WeatherRequest(
        location_input=payload.location,
        resolved_name=location["name"],
        country=location["country"],
        latitude=location["latitude"],
        longitude=location["longitude"],
        start_date=payload.start_date,
        end_date=payload.end_date,
        weather_data=weather_data,
        notes=payload.notes,
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    return record


@router.get("/history", response_model=List[WeatherResponse])
def list_weather_requests(db: Session = Depends(get_db)):
    return db.query(WeatherRequest).order_by(WeatherRequest.created_at.desc()).all()


@router.get("/history/{record_id}", response_model=WeatherResponse)
def get_weather_request(record_id: int, db: Session = Depends(get_db)):
    record = db.query(WeatherRequest).filter(WeatherRequest.id == record_id).first()

    if not record:
        raise HTTPException(status_code=404, detail="Weather record not found")

    return record


@router.patch("/history/{record_id}", response_model=WeatherResponse)
def update_weather_request(
    record_id: int,
    payload: WeatherUpdate,
    db: Session = Depends(get_db),
):
    record = db.query(WeatherRequest).filter(WeatherRequest.id == record_id).first()

    if not record:
        raise HTTPException(status_code=404, detail="Weather record not found")

    if payload.notes is not None:
        record.notes = payload.notes

    db.commit()
    db.refresh(record)

    return record


@router.delete("/history/{record_id}")
def delete_weather_request(record_id: int, db: Session = Depends(get_db)):
    record = db.query(WeatherRequest).filter(WeatherRequest.id == record_id).first()

    if not record:
        raise HTTPException(status_code=404, detail="Weather record not found")

    db.delete(record)
    db.commit()

    return {"message": "Weather record deleted successfully", "id": record_id}


@router.get("/export/json")
def export_json(db: Session = Depends(get_db)):
    records = db.query(WeatherRequest).order_by(WeatherRequest.created_at.desc()).all()

    data = [
        {
            "id": record.id,
            "location_input": record.location_input,
            "resolved_name": record.resolved_name,
            "country": record.country,
            "latitude": record.latitude,
            "longitude": record.longitude,
            "start_date": record.start_date.isoformat(),
            "end_date": record.end_date.isoformat(),
            "weather_data": record.weather_data,
            "notes": record.notes,
            "created_at": record.created_at.isoformat() if record.created_at else None,
        }
        for record in records
    ]

    return Response(
        content=json.dumps(data, indent=2),
        media_type="application/json",
        headers={"Content-Disposition": "attachment; filename=weather_export.json"},
    )


@router.get("/export/csv")
def export_csv(db: Session = Depends(get_db)):
    records = db.query(WeatherRequest).order_by(WeatherRequest.created_at.desc()).all()

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "id",
        "location_input",
        "resolved_name",
        "country",
        "latitude",
        "longitude",
        "start_date",
        "end_date",
        "notes",
        "created_at",
    ])

    for record in records:
        writer.writerow([
            record.id,
            record.location_input,
            record.resolved_name,
            record.country,
            record.latitude,
            record.longitude,
            record.start_date,
            record.end_date,
            record.notes,
            record.created_at,
        ])

    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=weather_export.csv"},
    )