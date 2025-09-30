[CmdletBinding()]
param(
  [switch]$Staged,
  [switch]$Changed,
  [string[]]$Files
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$repo = Split-Path -Parent $PSScriptRoot
Set-Location $repo

function Invoke-Step([string]$Name, [string]$Cmd) {
  Write-Host "==> $Name" -ForegroundColor Cyan
  & powershell -NoProfile -Command $Cmd
}

$validExt = @('.py','.toml','.yml','.yaml')
function Filter-Files([string[]]$paths){
  foreach ($p in $paths) {
    if (Test-Path $p) {
      $ext = [IO.Path]::GetExtension($p).ToLower()
      if ($validExt -contains $ext) { Resolve-Path -LiteralPath $p | % { $_.Path } }
    }
  }
}

$targets = @()
if ($Files) {
  $targets = Filter-Files $Files
} elseif ($Staged) {
  $targets = Filter-Files (git diff --name-only --cached --diff-filter=ACMRT)
} elseif ($Changed) {
  $upstream = (git rev-parse --abbrev-ref --symbolic-full-name '@{u}' 2>$null)
  if (-not $upstream) { $upstream = 'HEAD' }
  $targets = Filter-Files (git diff --name-only $upstream --diff-filter=ACMRT)
} else {
  $targets = Get-ChildItem -Recurse -File -Include *.py,*.toml,*.yml,*.yaml | % FullName
  $targets = Filter-Files $targets
}

if (-not $targets) {
  Write-Host "No target files." -ForegroundColor Yellow
  exit 0
}

Invoke-Step "pre-commit install" 'py -m pre_commit install'
if (Test-Path ".pre-commit-config.yml" -and -not (Test-Path ".pre-commit-config.yaml")) {
  Rename-Item ".pre-commit-config.yml" ".pre-commit-config.yaml" -Force
}

$pyTargets = $targets | ?{ $_.ToLower().EndsWith('.py') }
if ($pyTargets) {
  $joined = ($pyTargets | % { '"{0}"' -f $_ }) -join ' '
  Invoke-Step "ruff --fix" ("py -m ruff check --fix -- " + $joined)
  Invoke-Step "ruff format" ("py -m ruff format -- " + $joined)
  Invoke-Step "isort" ("py -m isort --profile black --line-length 100 -- " + $joined)
  Invoke-Step "black" ("py -m black --line-length 100 -- " + $joined)
}

$cfgArg = ""
if (Test-Path ".pre-commit-config.yaml") { $cfgArg = "-c .pre-commit-config.yaml" }
$joinedAll = ($targets | % { '"{0}"' -f $_ }) -join ' '
Invoke-Step "pre-commit (selected files)" ("py -m pre_commit run --files " + $joinedAll + " " + $cfgArg)

if ($pyTargets) {
  $joined = ($pyTargets | % { '"{0}"' -f $_ }) -join ' '
  Invoke-Step "mypy" ("py -m mypy --config-file pyproject.toml -- " + $joined)
}

Write-Host "`nDone." -ForegroundColor Green
