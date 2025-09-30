# File: tools/move-repo.ps1
<#!
Relocate or rename a Git repo on disk (Windows/PowerShell).
Why: Moving the folder preserves history because `.git` moves with it.

USAGE EXAMPLES
--------------
# Move repo to a new parent directory, same name
#   From anywhere:
#   .\tools\move-repo.ps1 -Source "C:\Users\tonyj\Documents\Celiogix" -To "D:\Projects"

# Move and rename in one go
#   .\tools\move-repo.ps1 -Source "C:\Users\tonyj\Documents\Celiogix" -To "D:\Projects\CeliogixApp"

# Dry-run preview
#   .\tools\move-repo.ps1 -Source . -To "D:\Projects" -DryRun

Notes
- Remotes (GitHub URLs) are unaffected by a local path change.
- After move, you may see a Git "unsafe repository" warning. This script can add the new path to safe.directory.
- Virtualenvs or scripts with hardcoded paths may need updating manually.
#>

[CmdletBinding()]
param(
    [Parameter(Position=0)]
    [string]$Source = ".",                          # any path inside the repo

    [Parameter(Mandatory, Position=1)]
    [string]$To,                                      # parent dir OR full new path

    [switch]$DryRun,
    [switch]$AddSafeDirectory                         # add new path to `git config --global safe.directory`
)

function Get-RepoRoot([string]$Path) {
    Push-Location $Path
    try {
        $inside = git rev-parse --is-inside-work-tree 2>$null
        if ($LASTEXITCODE -ne 0 -or $inside -ne 'true') { throw "Not a git repo: $(Resolve-Path .)" }
        (git rev-parse --show-toplevel).Trim()
    } finally { Pop-Location }
}

function Resolve-Destination([string]$SrcRoot, [string]$To) {
    if (-not (Test-Path $To)) {
        # Treat as full destination path (including new name)
        return $To
    }
    $item = Get-Item $To
    if ($item.PSIsContainer) {
        # Append current repo folder name
        $name = Split-Path $SrcRoot -Leaf
        return (Join-Path $To $name)
    }
    throw "Destination exists and is not a directory: $To"
}

try {
    $srcRoot = Get-RepoRoot -Path $Source
    $destPath = Resolve-Destination -SrcRoot $srcRoot -To $To

    if (Test-Path $destPath) {
        throw "Destination already exists: $destPath"
    }

    Write-Host "Moving repo" -ForegroundColor Green
    Write-Host "  From: $srcRoot"
    Write-Host "    To: $destPath"

    if ($DryRun) {
        Write-Host "DRY RUN: no changes made." -ForegroundColor Yellow
        return
    }

    # Ensure destination parent exists
    $parent = Split-Path $destPath -Parent
    if (-not (Test-Path $parent)) { New-Item -ItemType Directory -Path $parent | Out-Null }

    Move-Item -LiteralPath $srcRoot -Destination $destPath

    # Verify in new location
    Push-Location $destPath
    try {
        $inside = git rev-parse --is-inside-work-tree 2>$null
        if ($LASTEXITCODE -ne 0 -or $inside -ne 'true') { throw "Post-move: Git not detected at $destPath" }
        $branch = (git rev-parse --abbrev-ref HEAD).Trim()
        Write-Host "Repo OK at new path on branch: $branch" -ForegroundColor Cyan

        if ($AddSafeDirectory) {
            git config --global --add safe.directory "$destPath" | Out-Null
            Write-Host "Added safe.directory: $destPath" -ForegroundColor DarkCyan
        }
    } finally { Pop-Location }

    Write-Host "Done" -ForegroundColor Green
}
catch {
    Write-Error $_
    exit 1
}
