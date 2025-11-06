"""
Pydantic models for request/response validation
"""
from typing import List
from pydantic import BaseModel, Field, field_validator
from datetime import time


class CalculateRequest(BaseModel):
    """Request model for sleep cycle calculation"""

    wake_time: str = Field(
        ...,
        description="Wake up time in HH:MM format (24-hour)",
        examples=["07:30", "06:00", "08:45"]
    )
    sleep_latency_min: int = Field(
        default=15,
        ge=0,
        le=60,
        description="Minutes it takes to fall asleep (0-60)"
    )
    cycle_length_min: int = Field(
        default=90,
        ge=60,
        le=110,
        description="Duration of one sleep cycle in minutes (60-110)"
    )
    min_cycles: int = Field(
        default=4,
        ge=1,
        le=10,
        description="Minimum number of sleep cycles to calculate"
    )
    max_cycles: int = Field(
        default=6,
        ge=1,
        le=10,
        description="Maximum number of sleep cycles to calculate"
    )

    @field_validator("wake_time")
    @classmethod
    def validate_time_format(cls, v: str) -> str:
        """Validate time is in HH:MM format"""
        try:
            hours, minutes = v.split(":")
            h, m = int(hours), int(minutes)
            if not (0 <= h <= 23 and 0 <= m <= 59):
                raise ValueError("Hours must be 0-23 and minutes must be 0-59")
            # Return normalized format (e.g., "7:30" -> "07:30")
            return f"{h:02d}:{m:02d}"
        except (ValueError, AttributeError) as e:
            raise ValueError(
                f"wake_time must be in HH:MM format (24-hour). Got: {v}"
            ) from e

    @field_validator("max_cycles")
    @classmethod
    def validate_cycle_range(cls, v: int, info) -> int:
        """Ensure max_cycles >= min_cycles"""
        if "min_cycles" in info.data and v < info.data["min_cycles"]:
            raise ValueError("max_cycles must be >= min_cycles")
        return v


class SleepOption(BaseModel):
    """A single bedtime option based on number of cycles"""

    cycles: int = Field(..., description="Number of sleep cycles")
    bedtime: str = Field(..., description="Suggested bedtime in HH:MM format")
    total_sleep_hours: float = Field(..., description="Total sleep time in decimal hours")
    total_sleep_minutes: int = Field(..., description="Total sleep time in minutes")
    recommended: bool = Field(
        default=False,
        description="Whether this option meets recommended sleep duration (≥7h)"
    )
    note: str = Field(..., description="Explanation of the calculation")


class CalculateResponse(BaseModel):
    """Response model for sleep cycle calculation"""

    wake_time: str = Field(..., description="The wake time provided")
    options: List[SleepOption] = Field(
        ...,
        description="List of bedtime options, ordered by number of cycles (descending)"
    )
    parameters: dict = Field(
        ...,
        description="The parameters used for calculation"
    )


class PreferencesRequest(BaseModel):
    """User preferences for default calculation parameters"""

    sleep_latency_min: int = Field(
        default=15,
        ge=0,
        le=60,
        description="Default minutes to fall asleep"
    )
    cycle_length_min: int = Field(
        default=90,
        ge=60,
        le=110,
        description="Default sleep cycle duration"
    )
    min_cycles: int = Field(
        default=4,
        ge=1,
        le=10,
        description="Default minimum cycles"
    )
    max_cycles: int = Field(
        default=6,
        ge=1,
        le=10,
        description="Default maximum cycles"
    )

    @field_validator("max_cycles")
    @classmethod
    def validate_cycle_range(cls, v: int, info) -> int:
        """Ensure max_cycles >= min_cycles"""
        if "min_cycles" in info.data and v < info.data["min_cycles"]:
            raise ValueError("max_cycles must be >= min_cycles")
        return v


class PreferencesResponse(BaseModel):
    """Response after saving preferences"""

    message: str = Field(..., description="Success message")
    preferences: PreferencesRequest = Field(..., description="Saved preferences")


class HealthResponse(BaseModel):
    """Health check response"""

    status: str = Field(..., description="API status")
    version: str = Field(..., description="API version")
