@echo off
echo Installing dependencies...
pip install -r requirements.txt
echo.
echo Starting Telegram Bot...
python bot.py
pause
