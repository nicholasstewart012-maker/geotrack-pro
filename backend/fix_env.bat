@echo off
cd /d "%~dp0"
echo ---------------------------------------------------
echo FIXING ENVIRONMENT CONFIGURATION
echo ---------------------------------------------------

echo 1. backup existing .env if present...
if exist .env copy .env .env.bak >nul

echo 2. Writing new .env file...
(
echo DATABASE_URL=postgresql://postgres:Password012_@localhost:5432/postgres
) > .env

echo 3. Verifying...
if exist .env (
    echo [OK] .env file created successfully!
    echo [OK] Content:
    type .env
) else (
    echo [ERROR] Failed to create file. Check permissions.
)

echo.
echo ---------------------------------------------------
echo DONE. Now run: python seed_data.py
echo ---------------------------------------------------
pause
