"""
Sleep cycle calculator core logic

This module contains the main algorithm for calculating optimal bedtimes
based on sleep cycles, wake time, and sleep latency.
"""
from typing import List
from datetime import datetime, timedelta
from pydantic import BaseModel, Field


class SleepOption(BaseModel):
    """Represents a single bedtime option with calculated sleep metrics"""

    cycles: int = Field(..., description="Number of sleep cycles")
    bedtime: str = Field(..., description="Suggested bedtime in HH:MM format")
    total_sleep_hours: float = Field(..., description="Total sleep time in decimal hours")
    total_sleep_minutes: int = Field(..., description="Total sleep time in minutes")
    recommended: bool = Field(
        default=False,
        description="Whether this option meets recommended sleep duration (≥7h)"
    )
    note: str = Field(..., description="Explanation of the calculation")


class SleepCycleCalculator:
    """
    Calculator for optimal bedtimes based on sleep cycles.

    The algorithm works as follows:
    1. Parse the wake time
    2. For each number of cycles (min_cycles to max_cycles):
       a. Calculate total sleep time = (cycles * cycle_length) + sleep_latency
       b. Subtract total sleep time from wake time to get bedtime
       c. Determine if it meets recommended duration (≥7 hours)
    3. Return sorted list of options (most cycles first)
    """

    # Constants
    RECOMMENDED_SLEEP_MINUTES = 420  # 7 hours
    MIN_SLEEP_LATENCY = 0
    MAX_SLEEP_LATENCY = 60
    MIN_CYCLE_LENGTH = 60
    MAX_CYCLE_LENGTH = 110
    MIN_CYCLES = 1
    MAX_CYCLES = 10

    def calculate(
        self,
        wake_time: str,
        sleep_latency_min: int,
        cycle_length_min: int,
        min_cycles: int,
        max_cycles: int
    ) -> List[SleepOption]:
        """
        Calculate optimal bedtimes based on sleep cycles.

        Args:
            wake_time: Target wake time in HH:MM format (24-hour)
            sleep_latency_min: Minutes it takes to fall asleep
            cycle_length_min: Duration of one sleep cycle in minutes
            min_cycles: Minimum number of cycles to calculate
            max_cycles: Maximum number of cycles to calculate

        Returns:
            List of SleepOption objects, sorted by number of cycles (descending)

        Raises:
            ValueError: If any parameter is invalid
        """
        # Validate inputs
        self._validate_inputs(
            wake_time, sleep_latency_min, cycle_length_min, min_cycles, max_cycles
        )

        # Parse wake time
        wake_datetime = self._parse_time(wake_time)

        # Calculate options for each cycle count
        options: List[SleepOption] = []
        for num_cycles in range(min_cycles, max_cycles + 1):
            option = self._calculate_option(
                wake_datetime,
                num_cycles,
                sleep_latency_min,
                cycle_length_min
            )
            options.append(option)

        # Sort by number of cycles (descending - most sleep first)
        options.sort(key=lambda x: x.cycles, reverse=True)

        return options

    def _validate_inputs(
        self,
        wake_time: str,
        sleep_latency_min: int,
        cycle_length_min: int,
        min_cycles: int,
        max_cycles: int
    ) -> None:
        """Validate all input parameters"""

        # Validate wake time format
        try:
            self._parse_time(wake_time)
        except ValueError as e:
            raise ValueError(f"Invalid time format: {e}") from e

        # Validate sleep latency
        if not (self.MIN_SLEEP_LATENCY <= sleep_latency_min <= self.MAX_SLEEP_LATENCY):
            raise ValueError(
                f"sleep_latency_min must be between {self.MIN_SLEEP_LATENCY} "
                f"and {self.MAX_SLEEP_LATENCY} minutes"
            )

        # Validate cycle length
        if not (self.MIN_CYCLE_LENGTH <= cycle_length_min <= self.MAX_CYCLE_LENGTH):
            raise ValueError(
                f"cycle_length_min must be between {self.MIN_CYCLE_LENGTH} "
                f"and {self.MAX_CYCLE_LENGTH} minutes"
            )

        # Validate cycle counts
        if not (self.MIN_CYCLES <= min_cycles <= self.MAX_CYCLES):
            raise ValueError(
                f"min_cycles must be between {self.MIN_CYCLES} and {self.MAX_CYCLES}"
            )

        if not (self.MIN_CYCLES <= max_cycles <= self.MAX_CYCLES):
            raise ValueError(
                f"max_cycles must be between {self.MIN_CYCLES} and {self.MAX_CYCLES}"
            )

        if min_cycles > max_cycles:
            raise ValueError("min_cycles must be less than or equal to max_cycles")

    def _parse_time(self, time_str: str) -> datetime:
        """
        Parse time string in HH:MM format to datetime object.

        Args:
            time_str: Time in HH:MM format

        Returns:
            datetime object with arbitrary date and given time

        Raises:
            ValueError: If time_str is not in valid format
        """
        try:
            hours, minutes = time_str.split(":")
            h, m = int(hours), int(minutes)

            if not (0 <= h <= 23):
                raise ValueError(f"Hours must be 0-23, got {h}")
            if not (0 <= m <= 59):
                raise ValueError(f"Minutes must be 0-59, got {m}")

            # Use arbitrary date (2024-01-01) since we only care about time
            return datetime(2024, 1, 1, h, m)

        except (ValueError, AttributeError) as e:
            raise ValueError(
                f"Time must be in HH:MM format (24-hour). Got: {time_str}"
            ) from e

    def _calculate_option(
        self,
        wake_datetime: datetime,
        num_cycles: int,
        sleep_latency_min: int,
        cycle_length_min: int
    ) -> SleepOption:
        """
        Calculate a single bedtime option for given number of cycles.

        Args:
            wake_datetime: Target wake time as datetime
            num_cycles: Number of sleep cycles
            sleep_latency_min: Minutes to fall asleep
            cycle_length_min: Duration of one cycle

        Returns:
            SleepOption with calculated bedtime and metrics
        """
        # Calculate total sleep time
        sleep_time_min = num_cycles * cycle_length_min
        total_time_min = sleep_time_min + sleep_latency_min

        # Calculate bedtime by subtracting total time from wake time
        bedtime_datetime = wake_datetime - timedelta(minutes=total_time_min)

        # Format bedtime as HH:MM
        bedtime_str = bedtime_datetime.strftime("%H:%M")

        # Calculate total sleep in hours (decimal)
        total_sleep_hours = total_time_min / 60.0

        # Determine if recommended (≥7 hours = 420 minutes)
        recommended = total_time_min >= self.RECOMMENDED_SLEEP_MINUTES

        # Generate explanatory note
        sleep_hours = sleep_time_min // 60
        sleep_mins = sleep_time_min % 60
        total_hours = total_time_min // 60
        total_mins = total_time_min % 60

        note = (
            f"{num_cycles} cycles = {sleep_hours}h {sleep_mins}m "
            f"({sleep_time_min} min) + {sleep_latency_min} min to fall asleep = "
            f"{total_hours}h {total_mins}m total"
        )

        return SleepOption(
            cycles=num_cycles,
            bedtime=bedtime_str,
            total_sleep_hours=total_sleep_hours,
            total_sleep_minutes=total_time_min,
            recommended=recommended,
            note=note
        )


# Convenience function for quick calculations
def calculate_bedtimes(
    wake_time: str,
    sleep_latency_min: int = 15,
    cycle_length_min: int = 90,
    min_cycles: int = 4,
    max_cycles: int = 6
) -> List[SleepOption]:
    """
    Convenience function to calculate bedtimes.

    Args:
        wake_time: Target wake time in HH:MM format
        sleep_latency_min: Minutes to fall asleep (default: 15)
        cycle_length_min: Sleep cycle duration (default: 90)
        min_cycles: Minimum cycles to calculate (default: 4)
        max_cycles: Maximum cycles to calculate (default: 6)

    Returns:
        List of SleepOption objects

    Example:
        >>> options = calculate_bedtimes("07:30")
        >>> for option in options:
        ...     print(f"{option.cycles} cycles: go to bed at {option.bedtime}")
    """
    calculator = SleepCycleCalculator()
    return calculator.calculate(
        wake_time, sleep_latency_min, cycle_length_min, min_cycles, max_cycles
    )
