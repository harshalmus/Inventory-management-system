@echo off
cd /d "%~dp0"
echo Starting Inventory Management App (StockPilot IMS)...
echo Opening http://127.0.0.1:5000 in your browser...
start http://127.0.0.1:5000
venv\Scripts\python.exe app.py
pause
