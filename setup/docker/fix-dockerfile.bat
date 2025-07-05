@echo off
REM Quick fix for the Dockerfile before deployment

echo 🔧 Fixing Dockerfile...

REM Create a backup
copy Dockerfile.postgis-arm64-working Dockerfile.postgis-arm64-working.backup

REM Remove the problematic line
powershell -Command "(Get-Content Dockerfile.postgis-arm64-working) -replace 'RUN su - postgres -c \"initdb -D /var/lib/postgresql/data\"', '# RUN su - postgres -c \"initdb -D /var/lib/postgresql/data\"' | Set-Content Dockerfile.postgis-arm64-working"

echo ✅ Dockerfile fixed - initdb line commented out
echo 📋 Now you can run: deploy-to-remote.bat

pause 