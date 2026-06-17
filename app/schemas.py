from datetime import date, datetime
from typing import Any, Optional

from pydantic import BaseModel, Field, model_validator


class WeatherSearchCreate(BaseModel):
    location: str = Field(..., min_length=2, examples=["Vancouver"])
    start_date: date
    end_date: date
    notes: Optional[str] = None

    @model_validator(mode="after")
    def validate_date_range(self):
        if self.end_date < self.start_date:
            raise ValueError("end_date must be greater than or equal to start_date")

        days = (self.end_date - self.start_date).days
        if days > 16:
            raise ValueError("Date range cannot be greater than 16 days for this demo")

        return self


class WeatherUpdate(BaseModel):
    notes: Optional[str] = None


class WeatherResponse(BaseModel):
    id: int
    location_input: str
    resolved_name: str
    country: Optional[str]
    latitude: float
    longitude: float
    start_date: date
    end_date: date
    weather_data: Any
    notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True