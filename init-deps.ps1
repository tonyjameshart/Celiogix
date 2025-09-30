# scripts/init-deps.ps1
# Purpose: Create dependency files and install them into a local venv.
# Why: Ensures consistent, reproducible setup on Windows/PowerShell.


Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'


function Get-PythonCmd {
if (Get-Command py -ErrorAction SilentlyContinue) { return @('py','-3') }
elseif (Get-Command python -ErrorAction SilentlyContinue) { return @('python') }
elseif (Get-Command python3 -ErrorAction SilentlyContinue) { return @('python3') }
else { throw 'Python not found. Install from https://www.python.org/downloads/ or via winget.' }
}


function Write-TextUtf8NoBom([string]$Path, [string]$Content) {
$dir = Split-Path -Parent $Path
if ($dir -and -not (Test-Path $dir)) { New-Item -ItemType Directory -Path $dir | Out-Null }
Set-Content -Path $Path -Value $Content -Encoding utf8NoBOM
}


$python = Get-PythonCmd
$venvPath = Join-Path (Get-Location) '.venv'


if (-not (Test-Path $venvPath)) {
& $python -m venv $venvPath
}


$venvPython = Join-Path $venvPath 'Scripts/python.exe'
if (-not (Test-Path $venvPython)) { throw "Virtual env looks broken at $venvPath" }


$req = @"
requests>=2.32
"@


$reqDev = @"
pytest
pytest-cov
black
ruff
mypy
pre-commit
"@


Write-TextUtf8NoBom -Path (Join-Path (Get-Location) 'requirements.txt') -Content $req
Write-TextUtf8NoBom -Path (Join-Path (Get-Location) 'requirements-dev.txt') -Content $reqDev


& $venvPython -m pip install --upgrade pip
& $venvPython -m pip install -r requirements.txt -r requirements-dev.txt


Write-Host '✅ Created requirements files and installed deps into .venv' -ForegroundColor Green
Write-Host ' Activate with: . .venv\Scripts\Activate.ps1'