@echo off
cd /d "%~dp0"
echo Signing in to Google Classroom (choose your teaching account in the browser)...
echo.
python classroom_post.py courses
echo.
pause
