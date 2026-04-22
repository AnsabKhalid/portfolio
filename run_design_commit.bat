@echo off
:: ─────────────────────────────────────────────────────────────────
:: Portfolio Auto Design Committer – Windows Task Scheduler runner
::
:: Schedule this file via Windows Task Scheduler to run automatically.
:: See setup instructions printed at the bottom, or run:
::   schtasks /query /tn "PortfolioDesignCommit"
:: ─────────────────────────────────────────────────────────────────
cd /d "%~dp0"

echo.
echo [%DATE% %TIME%] Starting portfolio design commit...
echo.

python auto_design_commits.py

if %ERRORLEVEL% neq 0 (
    echo.
    echo [ERROR] Script exited with code %ERRORLEVEL%
    exit /b %ERRORLEVEL%
)

echo.
echo [%DATE% %TIME%] Done.
