@echo off
echo Setting up Design System Schema...
echo.

REM Check if .env file exists
if not exist "..\..\backend\.env" (
    echo Error: .env file not found in backend directory
    echo Please ensure you have configured your database connection
    pause
    exit /b 1
)

REM Load environment variables
for /f "tokens=*" %%a in ('type "..\..\backend\.env" ^| findstr /v "^#" ^| findstr /v "^$"') do (
    set %%a
)

REM Set database connection parameters
set DB_HOST=%DB_HOST%
set DB_PORT=%DB_PORT%
set DB_NAME=%DB_NAME%
set DB_USER=%DB_USER%
set DB_PASSWORD=%DB_PASSWORD%

echo Database: %DB_HOST%:%DB_PORT%/%DB_NAME%
echo User: %DB_USER%
echo.

REM Run the design system schema
echo Creating design system schema...
psql -h %DB_HOST% -p %DB_PORT% -U %DB_USER% -d %DB_NAME% -f "..\schemas\design\01_create_design_schema.sql"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo Design System schema created successfully!
    echo.
    echo Features available:
    echo - Table Designs: Create and manage table structures
    echo - Mapping Configurations: Define file-to-table mappings
    echo - Audit Logging: Track all design system activities
    echo - AI-Powered Matching: Automatic file-to-design matching
    echo.
) else (
    echo.
    echo Error: Failed to create design system schema
    echo Please check your database connection and permissions
    echo.
)

pause 