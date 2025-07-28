@echo off
REM CLI Runner Script for Windows - Persona-Driven PDF Analysis System

echo 🚀 Persona-Driven PDF Analysis System - CLI Mode
echo ================================================

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Python is required but not installed.
    pause
    exit /b 1
)

REM Check if offline CLI script exists
if not exist "cli_offline.py" (
    echo ❌ Error: cli_offline.py not found.
    pause
    exit /b 1
)

REM Run with provided arguments or interactively
if "%~1"=="" (
    echo 🔧 Running in interactive mode...
    python cli_offline.py
) else (
    echo 🔧 Running with arguments: %*
    python cli_offline.py %*
)

pause