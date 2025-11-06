"""
User preferences endpoints

For MVP, preferences are stored in memory (not persisted).
In production, these would be stored in a database with user authentication.
"""
from fastapi import APIRouter, HTTPException, status
from app.models import PreferencesRequest, PreferencesResponse


router = APIRouter()

# In-memory storage for MVP
# In production: use database with user authentication
_user_preferences = PreferencesRequest()


@router.post(
    "/preferences",
    response_model=PreferencesResponse,
    status_code=status.HTTP_200_OK,
    summary="Save user preferences",
    description=(
        "Save default calculation parameters. "
        "These will be used as defaults for future calculations. "
        "Note: In this MVP version, preferences are not persisted and will reset on server restart."
    )
)
async def save_preferences(preferences: PreferencesRequest) -> PreferencesResponse:
    """
    Save user's default sleep calculation preferences.

    Store your preferred default values for:
    - Sleep latency (how long you take to fall asleep)
    - Cycle length (your typical sleep cycle duration)
    - Min/max cycles to show in calculations

    **Note:** In this MVP version, preferences are stored in memory only.
    Future versions will support user accounts and persistent storage.

    **Example:**
    ```json
    {
      "sleep_latency_min": 20,
      "cycle_length_min": 85,
      "min_cycles": 5,
      "max_cycles": 6
    }
    ```
    """
    global _user_preferences

    try:
        # Validation is handled by Pydantic model
        _user_preferences = preferences

        return PreferencesResponse(
            message="Preferences saved successfully",
            preferences=preferences
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save preferences: {str(e)}"
        ) from e


@router.get(
    "/preferences",
    response_model=PreferencesRequest,
    summary="Get user preferences",
    description="Retrieve the currently saved default calculation parameters."
)
async def get_preferences() -> PreferencesRequest:
    """
    Get the current user preferences.

    Returns the saved default values that will be used for calculations
    if not explicitly overridden.

    **Returns:**
    The current preferences, or system defaults if none have been saved.
    """
    return _user_preferences


@router.delete(
    "/preferences",
    response_model=PreferencesResponse,
    summary="Reset preferences to defaults",
    description="Reset all preferences to system defaults."
)
async def reset_preferences() -> PreferencesResponse:
    """
    Reset preferences to system defaults.

    This will restore:
    - Sleep latency: 15 minutes
    - Cycle length: 90 minutes
    - Min cycles: 4
    - Max cycles: 6
    """
    global _user_preferences

    _user_preferences = PreferencesRequest()

    return PreferencesResponse(
        message="Preferences reset to defaults",
        preferences=_user_preferences
    )
