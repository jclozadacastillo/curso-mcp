# Feature Specification: Temperature Converter Service
**Status:** Approved  
**Author:** Juan Carlos Lozada (UNIANDES)  
**Target:** Python 3.12 Backend Module  

---

## 1. Overview
The Temperature Converter module provides verified thermal conversions across Celsius (C), Fahrenheit (F), and Kelvin (K) scales. The implementation guarantees strict adherence to physical thermodynamic boundaries, precise two-decimal rounding, and unified CLI/programmatic consumption.

---

## 2. Functional Requirements

- **FR-001:** The system shall convert between Celsius, Fahrenheit, and Kelvin in any directional combination using exact international standard conversion formulas.
- **FR-002:** The system shall round all output conversion values to exactly two decimal places.
- **FR-003:** The system shall reject any input temperature below absolute zero (0.0 K, -273.15 °C, -459.67 °F) with a descriptive `ValueError`.
- **FR-004:** The system shall support both programmatic invocation via `TemperatureService` and command-line execution via CLI parameters (`--value`, `--from`, `--to`).

---

## 3. Acceptance Scenarios

### Scenario 1: Celsius to Fahrenheit Normal Conversion
* **Given** a temperature value of 100.0 in scale "C"
* **When** converted to scale "F"
* **Then** the result must be 212.00

### Scenario 2: Fahrenheit to Celsius Normal Conversion
* **Given** a temperature value of 32.0 in scale "F"
* **When** converted to scale "C"
* **Then** the result must be 0.00

### Scenario 3: Celsius to Kelvin Normal Conversion
* **Given** a temperature value of 0.0 in scale "C"
* **When** converted to scale "K"
* **Then** the result must be 273.15

### Scenario 4: Identity Conversion (Same Scale)
* **Given** a temperature value of 25.5 in scale "C"
* **When** converted to scale "C"
* **Then** the result must return 25.50 without mathematical distortion

### Scenario 5: Absolute Zero Boundary Condition
* **Given** a temperature value of -273.15 in scale "C"
* **When** converted to scale "K"
* **Then** the result must be exactly 0.00 without raising an error

### Scenario 6: Rejection Below Absolute Zero
* **Given** a temperature value of -274.00 in scale "C"
* **When** conversion is attempted to any target scale
* **Then** the system must raise `ValueError` indicating violation of absolute zero

### Scenario 7: CLI End-to-End Execution
* **Given** the CLI is called with `--value 100 --from C --to F`
* **When** the command executes
* **Then** exit code must be 0 and stdout must contain "212.00 F"

---

## 4. Edge Cases

- **Non-numeric input:** Passing strings like "abc", boolean values, or `None` raises `TypeError`.
- **Case and whitespace tolerance:** Scale strings such as `" c "` or `"k"` are normalized to uppercase stripped tokens.
- **Unsupported scales:** Scale identifier outside `{"C", "F", "K"}` raises `ValueError`.
- **Extreme float handling:** Non-finite numbers (`inf`, `-inf`, `nan`) are validated and rejected.

---

## 5. Clarifications
- **CL-001:** Negative temperatures above absolute zero (e.g., -40 °C) are physically valid and must convert to -40.00 °F cleanly.
- **CL-002:** Output numbers must preserve standard floating-point representation with two decimal places.
