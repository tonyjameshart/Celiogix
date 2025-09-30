[CmdletBinding()]
param(
  [string]$Python = "py",
  [switch]$Force,
  [switch]$GlobalInstall
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$repo = Split-Path -Parent $PSScriptRoot
Set-Location $repo

Write-Host "Repo: $repo" -ForegroundColor Cyan

if (-not $GlobalInstall) {
  $venvPath = Join-Path $repo ".venv"
  if ($Force -and (Test-Path $venvPath)) { Remove-Item -Recurse -Force $venvPath }
  if (-not (Test-Path $venvPath)) {
    Write-Host "==> Creating venv at .venv" -ForegroundColor Cyan
    & $Python -m venv .venv
  }
  $env:VIRTUAL_ENV = $venvPath
  $bin = Join-Path $venvPath "Scripts"
  $env:PATH = "$bin;$env:PATH"
  Write-Host "Activated venv: $venvPath" -ForegroundColor Green
} else {
  Write-Host "Using global/user site installs" -ForegroundColor Yellow
}

Write-Host "==> Upgrading pip" -ForegroundColor Cyan
py -m pip install -U pip

Write-Host "==> Installing dev deps" -ForegroundColor Cyan
py -m pip install -e ".[dev]"

if (Test-Path ".pre-commit-config.yml" -and -not (Test-Path ".pre-commit-config.yaml")) {
  Rename-Item ".pre-commit-config.yml" ".pre-commit-config.yaml" -Force
}

Write-Host "==> Installing pre-commit hooks" -ForegroundColor Cyan
py -m pre_commit install

Write-Host "==> Initial run of hooks (may auto-fix files)" -ForegroundColor Cyan
py -m pre_commit run --all-files

Write-Host "`nDone. To activate venv in new shells: `.venv\Scripts\Activate.ps1`" -ForegroundColor Green
a. Run py -m pre_commit run --all-files and paste any remaining errors.
b. Do you want Pylint integration added to CI and .pylintrc tuned next?




No file chosenNo file chosen
ChatGPT can make mistakes. Check important info.
