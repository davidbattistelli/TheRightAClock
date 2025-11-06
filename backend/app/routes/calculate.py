"""
Sleep cycle calculation endpoints
"""
from fastapi import APIRouter, HTTPException, status
from typing import List
from app.models import CalculateRequest, CalculateResponse, SleepOption
from app.calculator import SleepCycleCalculator


router = APIRouter()
calculator = SleepCycleCalculator()


@router.post(
    "/calculate",
    response_model=CalculateResponse,
    status_code=status.HTTP_200_OK,
    summary="Calculate optimal bedtimes",
    description=(
        "Calculate optimal bedtimes based on your wake time and sleep cycle preferences. "
        "Returns multiple options with different numbers of sleep cycles."
    ),
    responses={
        200: {
            "description": "Successfully calculated bedtime options",
            "content": {
                "application/json": {
                    "example": {
                        "wake_time": "07:30",
                        "options": [
                            {
                                "cycles": 6,
                                "bedtime": "22:45",
                                "total_sleep_hours": 8.75,
                                "total_sleep_minutes": 525,
                                "recommended": False,
                                "note": "6 cycles = 9h 0m (540 min) + 15 min to fall asleep = 9h 15m total"
                            },
                            {
                                "cycles": 5,
                                "bedtime": "00:15",
                                "total_sleep_hours": 7.25,
                                "total_sleep_minutes": 435,
                                "recommended": True,
                                "note": "5 cycles = 7h 30m (450 min) + 15 min to fall asleep = 7h 45m total"
                            }
                        ],
                        "parameters": {
                            "sleep_latency_min": 15,
                            "cycle_length_min": 90
                        }
                    }
                }
            }
        },
        422: {
            "description": "Validation error - invalid input parameters"
        },
        500: {
            "description": "Internal server error"
        }
    }
)
async def calculate_bedtimes(request: CalculateRequest) -> CalculateResponse:
    """
    Calculate optimal bedtimes based on sleep cycles.

    This endpoint takes your desired wake time and calculates multiple bedtime
    options based on complete sleep cycles. Each option shows:
    - Number of sleep cycles
    - Suggested bedtime
    - Total sleep duration
    - Whether it meets the recommended 7+ hours
    - Explanatory note

    **Parameters:**
    - **wake_time**: Your desired wake-up time in HH:MM format (24-hour)
    - **sleep_latency_min**: How long it typically takes you to fall asleep (0-60 minutes)
    - **cycle_length_min**: Your sleep cycle duration (typically 60-110 minutes, default 90)
    - **min_cycles**: Minimum number of cycles to show (1-10)
    - **max_cycles**: Maximum number of cycles to show (1-10)

    **Returns:**
    A list of bedtime options sorted by number of cycles (most sleep first).

    **Example:**
    If you want to wake at 07:30 with default settings, you'll get options
    for 4, 5, and 6 complete sleep cycles, with bedtimes like 00:45, 23:15, and 21:45.
    """
    try:
        # Calculate options using the core algorithm
        options = calculator.calculate(
            wake_time=request.wake_time,
            sleep_latency_min=request.sleep_latency_min,
            cycle_length_min=request.cycle_length_min,
            min_cycles=request.min_cycles,
            max_cycles=request.max_cycles
        )

        # Convert calculator SleepOptions to API SleepOptions (same structure)
        api_options = [
            SleepOption(
                cycles=opt.cycles,
                bedtime=opt.bedtime,
                total_sleep_hours=opt.total_sleep_hours,
                total_sleep_minutes=opt.total_sleep_minutes,
                recommended=opt.recommended,
                note=opt.note
            )
            for opt in options
        ]

        # Build response
        return CalculateResponse(
            wake_time=request.wake_time,
            options=api_options,
            parameters={
                "sleep_latency_min": request.sleep_latency_min,
                "cycle_length_min": request.cycle_length_min
            }
        )

    except ValueError as e:
        # Validation error from calculator
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        ) from e
    except Exception as e:
        # Unexpected error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        ) from e


@router.get(
    "/calculate/quick",
    response_model=CalculateResponse,
    summary="Quick calculation with defaults",
    description=(
        "Quick bedtime calculation with default parameters. "
        "Just provide wake_time as a query parameter."
    )
)
async def quick_calculate(wake_time: str) -> CalculateResponse:
    """
    Quick calculation endpoint with default parameters.

    Use this for a simple calculation without having to provide all parameters.
    Uses defaults: 15 min sleep latency, 90 min cycles, 4-6 cycle range.

    **Parameters:**
    - **wake_time**: Your desired wake-up time in HH:MM format (e.g., "07:30")

    **Example:**
    GET /api/v1/calculate/quick?wake_time=07:30
    """
    request = CalculateRequest(wake_time=wake_time)
    return await calculate_bedtimes(request)
