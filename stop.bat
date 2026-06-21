@echo off
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8443') do taskkill /F /PID %%a
