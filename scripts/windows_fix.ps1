python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8010
Write-Host "Chat: http://127.0.0.1:8010/"
Write-Host "Admin: http://127.0.0.1:8010/admin"