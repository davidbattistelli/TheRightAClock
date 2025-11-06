"""
Test suite for sleep cycle calculator (TDD)

Following TDD methodology:
1. Write tests first
2. Run tests (they should fail)
3. Implement code to make tests pass
4. Refactor and repeat
"""
import pytest
from datetime import time, datetime, timedelta
from app.calculator import SleepCycleCalculator, SleepOption


class TestSleepCycleCalculator:
    """Test the core sleep cycle calculation logic"""

    def test_basic_calculation_5_cycles(self):
        """Test basic calculation with default parameters (5 cycles)"""
        calculator = SleepCycleCalculator()
        options = calculator.calculate(
            wake_time="07:30",
            sleep_latency_min=15,
            cycle_length_min=90,
            min_cycles=5,
            max_cycles=5
        )

        assert len(options) == 1
        option = options[0]
        assert option.cycles == 5
        # 5 cycles * 90 min = 450 min = 7h 30m
        # Wake at 07:30, sleep 7h30 + 15min latency = 7h45 total
        # 07:30 - 7h45 = 23:45 (previous day)
        assert option.bedtime == "23:45"
        assert option.total_sleep_minutes == 465  # 450 + 15
        assert option.total_sleep_hours == pytest.approx(7.75, abs=0.01)

    def test_multiple_cycle_options(self):
        """Test calculation with multiple cycle options (4-6)"""
        calculator = SleepCycleCalculator()
        options = calculator.calculate(
            wake_time="07:00",
            sleep_latency_min=15,
            cycle_length_min=90,
            min_cycles=4,
            max_cycles=6
        )

        assert len(options) == 3
        # Should be ordered descending by cycles (6, 5, 4)
        assert options[0].cycles == 6
        assert options[1].cycles == 5
        assert options[2].cycles == 4

        # Check calculations
        # 6 cycles: 6*90=540min + 15 = 555min = 9h15m -> 07:00 - 9h15m = 21:45
        assert options[0].bedtime == "21:45"
        assert options[0].total_sleep_minutes == 555

        # 5 cycles: 5*90=450min + 15 = 465min = 7h45m -> 07:00 - 7h45m = 23:15
        assert options[1].bedtime == "23:15"
        assert options[1].total_sleep_minutes == 465

        # 4 cycles: 4*90=360min + 15 = 375min = 6h15m -> 07:00 - 6h15m = 00:45
        assert options[2].bedtime == "00:45"
        assert options[2].total_sleep_minutes == 375

    def test_custom_cycle_length(self):
        """Test with custom cycle length (85 minutes instead of 90)"""
        calculator = SleepCycleCalculator()
        options = calculator.calculate(
            wake_time="06:00",
            sleep_latency_min=10,
            cycle_length_min=85,
            min_cycles=5,
            max_cycles=5
        )

        assert len(options) == 1
        # 5 cycles * 85 min = 425 min + 10 min latency = 435 min = 7h15m
        # 06:00 - 7h15m = 22:45
        assert options[0].bedtime == "22:45"
        assert options[0].total_sleep_minutes == 435
        assert options[0].total_sleep_hours == pytest.approx(7.25, abs=0.01)

    def test_zero_sleep_latency(self):
        """Test with zero sleep latency (falls asleep instantly)"""
        calculator = SleepCycleCalculator()
        options = calculator.calculate(
            wake_time="08:00",
            sleep_latency_min=0,
            cycle_length_min=90,
            min_cycles=6,
            max_cycles=6
        )

        # 6 cycles * 90 = 540 min = 9h exactly
        # 08:00 - 9h = 23:00
        assert options[0].bedtime == "23:00"
        assert options[0].total_sleep_minutes == 540

    def test_midnight_crossing(self):
        """Test bedtime calculation that crosses midnight"""
        calculator = SleepCycleCalculator()
        options = calculator.calculate(
            wake_time="02:00",  # Early morning wake
            sleep_latency_min=15,
            cycle_length_min=90,
            min_cycles=5,
            max_cycles=5
        )

        # 5 cycles * 90 = 450 + 15 = 465 min = 7h45m
        # 02:00 - 7h45m = 18:15 (previous day)
        assert options[0].bedtime == "18:15"

    def test_recommendation_flag_sufficient_sleep(self):
        """Test that options with ≥7 hours are marked as recommended"""
        calculator = SleepCycleCalculator()
        options = calculator.calculate(
            wake_time="07:00",
            sleep_latency_min=15,
            cycle_length_min=90,
            min_cycles=4,
            max_cycles=6
        )

        # 6 cycles: 555 min = 9.25h -> recommended ✓
        assert options[0].total_sleep_minutes == 555
        assert options[0].recommended is True

        # 5 cycles: 465 min = 7.75h -> recommended ✓
        assert options[1].total_sleep_minutes == 465
        assert options[1].recommended is True

        # 4 cycles: 375 min = 6.25h -> NOT recommended ✗
        assert options[2].total_sleep_minutes == 375
        assert options[2].recommended is False

    def test_recommendation_boundary_420_minutes(self):
        """Test recommendation boundary at exactly 7 hours (420 minutes)"""
        calculator = SleepCycleCalculator()

        # Just under 7 hours: 419 minutes
        options = calculator.calculate(
            wake_time="07:00",
            sleep_latency_min=14,  # 4*90 + 14 = 374 min
            cycle_length_min=90,
            min_cycles=4,
            max_cycles=4
        )
        assert options[0].total_sleep_minutes == 374
        assert options[0].recommended is False

        # Exactly 7 hours: 420 minutes
        options = calculator.calculate(
            wake_time="07:00",
            sleep_latency_min=60,  # 4*90 + 60 = 420 min
            cycle_length_min=90,
            min_cycles=4,
            max_cycles=4
        )
        assert options[0].total_sleep_minutes == 420
        assert options[0].recommended is True

    def test_note_generation(self):
        """Test that explanatory notes are generated correctly"""
        calculator = SleepCycleCalculator()
        options = calculator.calculate(
            wake_time="07:00",
            sleep_latency_min=15,
            cycle_length_min=90,
            min_cycles=5,
            max_cycles=5
        )

        note = options[0].note
        assert "5 cycles" in note
        assert "7h 30m" in note or "7h30m" in note or "450" in note
        assert "15 min" in note or "15min" in note
        assert "7h 45m" in note or "7h45m" in note or "465" in note

    def test_single_cycle(self):
        """Test calculation with just 1 cycle (nap scenario)"""
        calculator = SleepCycleCalculator()
        options = calculator.calculate(
            wake_time="14:00",
            sleep_latency_min=5,
            cycle_length_min=90,
            min_cycles=1,
            max_cycles=1
        )

        # 1 cycle * 90 = 90 + 5 = 95 min
        # 14:00 - 95min = 12:25
        assert options[0].cycles == 1
        assert options[0].bedtime == "12:25"
        assert options[0].total_sleep_minutes == 95

    def test_edge_case_max_cycles(self):
        """Test with maximum supported cycles (10)"""
        calculator = SleepCycleCalculator()
        options = calculator.calculate(
            wake_time="10:00",
            sleep_latency_min=0,
            cycle_length_min=90,
            min_cycles=10,
            max_cycles=10
        )

        # 10 cycles * 90 = 900 min = 15 hours
        # 10:00 - 15h = 19:00 (previous day)
        assert options[0].cycles == 10
        assert options[0].bedtime == "19:00"
        assert options[0].total_sleep_minutes == 900

    def test_wake_time_at_midnight(self):
        """Test wake time at midnight (00:00)"""
        calculator = SleepCycleCalculator()
        options = calculator.calculate(
            wake_time="00:00",
            sleep_latency_min=15,
            cycle_length_min=90,
            min_cycles=5,
            max_cycles=5
        )

        # 5 cycles * 90 + 15 = 465 min = 7h45m
        # 00:00 - 7h45m = 16:15 (previous day)
        assert options[0].bedtime == "16:15"

    def test_wake_time_at_noon(self):
        """Test wake time at noon (12:00)"""
        calculator = SleepCycleCalculator()
        options = calculator.calculate(
            wake_time="12:00",
            sleep_latency_min=20,
            cycle_length_min=100,
            min_cycles=6,
            max_cycles=6
        )

        # 6 cycles * 100 + 20 = 620 min = 10h20m
        # 12:00 - 10h20m = 01:40
        assert options[0].bedtime == "01:40"
        assert options[0].total_sleep_minutes == 620

    def test_sorting_by_cycles_descending(self):
        """Verify options are sorted by cycle count (most cycles first)"""
        calculator = SleepCycleCalculator()
        options = calculator.calculate(
            wake_time="07:00",
            sleep_latency_min=15,
            cycle_length_min=90,
            min_cycles=3,
            max_cycles=7
        )

        assert len(options) == 5  # 3, 4, 5, 6, 7
        for i in range(len(options) - 1):
            assert options[i].cycles > options[i + 1].cycles


class TestInputValidation:
    """Test input validation and error handling"""

    def test_invalid_time_format(self):
        """Test that invalid time formats raise appropriate errors"""
        calculator = SleepCycleCalculator()

        with pytest.raises(ValueError, match="time format"):
            calculator.calculate("25:00", 15, 90, 4, 6)  # Invalid hour

        with pytest.raises(ValueError, match="time format"):
            calculator.calculate("12:60", 15, 90, 4, 6)  # Invalid minute

        with pytest.raises(ValueError, match="time format"):
            calculator.calculate("not-a-time", 15, 90, 4, 6)

    def test_invalid_parameter_ranges(self):
        """Test that out-of-range parameters are rejected"""
        calculator = SleepCycleCalculator()

        # Negative sleep latency
        with pytest.raises(ValueError):
            calculator.calculate("07:00", -1, 90, 4, 6)

        # Excessive sleep latency
        with pytest.raises(ValueError):
            calculator.calculate("07:00", 61, 90, 4, 6)

        # Invalid cycle length (too short)
        with pytest.raises(ValueError):
            calculator.calculate("07:00", 15, 59, 4, 6)

        # Invalid cycle length (too long)
        with pytest.raises(ValueError):
            calculator.calculate("07:00", 15, 111, 4, 6)

        # Invalid cycle counts
        with pytest.raises(ValueError):
            calculator.calculate("07:00", 15, 90, 0, 6)  # min too low

        with pytest.raises(ValueError):
            calculator.calculate("07:00", 15, 90, 4, 11)  # max too high

    def test_min_cycles_greater_than_max(self):
        """Test that min_cycles > max_cycles raises error"""
        calculator = SleepCycleCalculator()

        with pytest.raises(ValueError, match="min_cycles.*max_cycles"):
            calculator.calculate("07:00", 15, 90, min_cycles=6, max_cycles=4)


class TestSleepOptionModel:
    """Test the SleepOption data class"""

    def test_sleep_option_creation(self):
        """Test creating a SleepOption instance"""
        option = SleepOption(
            cycles=5,
            bedtime="23:45",
            total_sleep_hours=7.75,
            total_sleep_minutes=465,
            recommended=True,
            note="Test note"
        )

        assert option.cycles == 5
        assert option.bedtime == "23:45"
        assert option.total_sleep_hours == 7.75
        assert option.total_sleep_minutes == 465
        assert option.recommended is True
        assert option.note == "Test note"
