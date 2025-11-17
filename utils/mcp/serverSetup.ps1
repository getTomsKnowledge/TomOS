if (-not (Test-Path weather)) { uv init --no-workspace weather }
Set-Location weather

uv venv
& .\.venv\Scripts\Activate.ps1

uv add mcp[cli] httpx

if (-not (Test-Path weather.py)) { New-Item -ItemType File weather.py | Out-Null }