# Architecture Plan — Temperature Converter Module

## 1. Modularity and Layers
- **Core Engine (`src/temp_converter/converter.py`):** Pure mathematical functions, boundary enforcement (absolute zero), scale validation. Independent of I/O.
- **Service Layer (`src/temp_converter/service.py`):** High-level orchestrator. Validates inputs, handles normalization, formats decimal outputs, wraps domain exceptions.
- **Presentation Layer (`src/temp_converter/cli.py`):** CLI interface using standard `argparse`, returns exit codes and formatted stdout.

## 2. Testing Strategy
- Core unit testing for exact formulas and physical limits.
- In-memory service integration testing.
- End-to-end command-line tests.
