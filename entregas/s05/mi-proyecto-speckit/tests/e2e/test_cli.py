"""
End-to-end (E2E) tests.
Executes the full application via subprocess, verifying stdout and exit codes.
"""

import subprocess
import sys


def test_cli_e2e_successful_conversion():
    # Execute full program: uv run python -m src.temp_converter.cli --value 100 --from C --to F
    result = subprocess.run(
        [sys.executable, "-m", "src.temp_converter.cli", "--value", "100", "--from", "C", "--to", "F"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "212.00 F" in result.stdout.strip()


def test_cli_e2e_absolute_zero_boundary():
    result = subprocess.run(
        [sys.executable, "-m", "src.temp_converter.cli", "--value", "-273.15", "--from", "C", "--to", "K"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "0.00 K" in result.stdout.strip()


def test_cli_e2e_error_below_absolute_zero():
    result = subprocess.run(
        [sys.executable, "-m", "src.temp_converter.cli", "--value", "-300", "--from", "C", "--to", "F"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1
    assert "Physical violation" in result.stderr
