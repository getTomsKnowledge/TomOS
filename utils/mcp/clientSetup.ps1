# Create project directory
if (-not (Test-Path mcp-client)) { uv init --no-workspace mcp-client }
Set-Location mcp-client

# Create virtual environment
uv venv

# Activate virtual environment
& .\.venv\Scripts\Activate.ps1

# Install required packages
uv add mcp openai python-dotenv

# Remove boilerplate files
Remove-Item main.py

# Create our main file
if (-not (Test-Path client.py)) { New-Item -ItemType File client.py | Out-Null }