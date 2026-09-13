@echo off
cd ..
uv run pytest --tb=no -q > nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo {}
) else (
    echo {"decision":"continue","reason":"Hay tests fallando. No te detengas -- corrige el codigo antes de terminar."}
)
