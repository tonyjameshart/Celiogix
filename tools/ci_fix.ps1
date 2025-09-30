[CmdletBinding()]
param(
  [switch]$NoFail
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$repo = Split-Path -Parent $PSScriptRoot
Set-Location $repo

Write-Host "Repo: $repo" -ForegroundColor Cyan

if (Test-Path ".pre-commit-config.yml" -and -not (Test-Path ".pre-commit-config.yaml")) {
  Rename-Item ".pre-commit-config.yml" ".pre-commit-config.yaml" -Force
}

py -m pip install -U pip | Out-Null
py -m pip install -e ".[dev]" | Out-Null

$py = @(Get-ChildItem -Recurse -File -Include *.py | % FullName)
if ($py.Count -gt 0) {
  Write-Host "==> Ruff fix" -ForegroundColor Cyan
  py -m ruff check --fix -- $py
  Write-Host "==> Ruff format" -ForegroundColor Cyan
  py -m ruff format -- $py
  Write-Host "==> isort" -ForegroundColor Cyan
  py -m isort --profile black --line-length 100 -- $py
  Write-Host "==> black" -ForegroundColor Cyan
  py -m black --line-length 100 -- $py
}

$cfgFiles = @(".pre-commit-config.yaml","pyproject.toml") | ?{ Test-Path $_ }
if ($cfgFiles) {
  Write-Host "==> Config checks" -ForegroundColor Cyan
  py -m pre_commit run check-yaml --files ($cfgFiles -join ' ') 2>$null | Out-Host
  py -m pre_commit run check-toml --files pyproject.toml 2>$null | Out-Host
}

py -m pre_commit install | Out-Null
Write-Host "==> pre-commit (all files)" -ForegroundColor Cyan
$pc = (py -m pre_commit run --all-files); $pc | Out-Host

if ($py.Count -gt 0) {
  Write-Host "==> mypy" -ForegroundColor Cyan
  $mypy = (py -m mypy --config-file pyproject.toml -- $py); $mypy | Out-Host
}

Write-Host "`n==> Summary" -ForegroundColor Cyan
$changed = @(git status --porcelain)
if ($changed.Count -gt 0) {
  Write-Host "Files modified by fixers/hooks:" -ForegroundColor Yellow
  $changed | Out-Host
} else {
  Write-Host "No file changes after hooks." -ForegroundColor Green
}

if ($NoFail) { exit 0 }
$failed = ($pc -match 'Failed') -or ($mypy -match 'error:')
if ($failed) {
  Write-Host "CI fix detected remaining issues." -ForegroundColor Red
  exit 1
}
Write-Host "CI fix passed." -ForegroundColor Green
exit 0
