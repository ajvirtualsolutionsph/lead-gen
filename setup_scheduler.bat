@echo off
echo Registering nightly Lead Gen task...
schtasks /create /tn "LeadGen_NightlyUpdate" /tr "\"cmd.exe\" /c \"c:\Users\Admin\Documents\Project 3_Lead Gen\run_nightly.bat\"" /sc daily /st 00:00 /ru "%USERNAME%" /rl HIGHEST /f
if %errorlevel%==0 (
    echo.
    echo [OK] Task registered. It will run every night at 12:00 AM.
    echo      Logs saved to: c:\Users\Admin\Documents\Project 3_Lead Gen\logs\nightly.log
) else (
    echo.
    echo [!] Failed. Make sure you right-clicked and chose "Run as administrator".
)
pause
