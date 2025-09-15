# File: tools/purge-git.ps1
<#!
Removes all Git repositories under a path while keeping working files intact.
- Deletes `.git` directories and `.git` files that point to external gitdirs.
- Optional: remove .gitignore/.gitattributes/.gitmodules.
- Supports dry-run.

USAGE
-----
# Preview only
#   .\tools\purge-git.ps1 -Root "C:\Users\tonyj\Documents" -DryRun

# Actually purge
#   .\tools\purge-git.ps1 -Root "C:\Users\tonyj\Documents"

# Also remove .gitignore/.gitattributes/.gitmodules
#   .\tools\purge-git.ps1 -Root "C:\Users\tonyj\Documents" -IncludeMeta
#>

[CmdletBinding()]
param(
    [Parameter(Position=0)]
    [string]$Root = ".",
    [switch]$DryRun,
    [switch]$IncludeMeta
)

function Resolve-PathSafe([string]$Path, [string]$BaseDir) {
    if ([System.IO.Path]::IsPathRooted($Path)) { return (Resolve-Path -LiteralPath $Path).Path }
    $combined = Join-Path -Path $BaseDir -ChildPath $Path
    return (Resolve-Path -LiteralPath $combined).Path
}

$ErrorActionPreference = 'Stop'
$removedGitDirs   = @()
$removedGitFiles  = @()
$removedMetaFiles = @()
$skipped          = @()
$errors           = @()

$rootPath = (Resolve-Path -LiteralPath $Root).Path
Write-Host "Scanning: $rootPath" -ForegroundColor Cyan

try {
    # 1) .git directories
    $gitDirs = Get-ChildItem -LiteralPath $rootPath -Recurse -Force -Directory -Filter ".git" -ErrorAction SilentlyContinue

    # 2) .git files (worktrees/submodules)
    $gitFiles = Get-ChildItem -LiteralPath $rootPath -Recurse -Force -File -Filter ".git" -ErrorAction SilentlyContinue

    Write-Host ("Found {0} .git directories, {1} .git files" -f $gitDirs.Count, $gitFiles.Count)

    if ($DryRun) {
        Write-Host "\nDRY RUN: would remove these .git directories:" -ForegroundColor Yellow
        $gitDirs | ForEach-Object { Write-Host "  DIR  $_" }
        Write-Host "\nDRY RUN: would remove these .git files (and their targets if inside root):" -ForegroundColor Yellow
        foreach ($f in $gitFiles) {
            Write-Host "  FILE $f"
            try {
                $first = (Get-Content -LiteralPath $f.FullName -TotalCount 1)
                if ($first -match '^gitdir:\s*(.+)\s*$') {
                    $target = Resolve-PathSafe -Path $Matches[1] -BaseDir $f.DirectoryName
                    Write-Host "       -> gitdir: $target"
                }
            } catch {}
        }
        if ($IncludeMeta) {
            $meta = Get-ChildItem -LiteralPath $rootPath -Recurse -Force -File -Include .gitignore,.gitattributes,.gitmodules -ErrorAction SilentlyContinue
            Write-Host "\nDRY RUN: would remove meta files:" -ForegroundColor Yellow
            $meta | ForEach-Object { Write-Host "  META $_" }
        }
        return
    }

    # Remove .git directories first
    foreach ($d in $gitDirs) {
        try {
            # remove hidden+readonly attributes if set
            attrib -h -s -r "$($d.FullName)" 2>$null | Out-Null
            Remove-Item -LiteralPath $d.FullName -Recurse -Force -ErrorAction Stop
            $removedGitDirs += $d.FullName
        } catch {
            $errors += "DIR fail: $($d.FullName) :: $_"
        }
    }

    # Handle .git files
    foreach ($f in $gitFiles) {
        try {
            $content = Get-Content -LiteralPath $f.FullName -TotalCount 1
            if ($content -match '^gitdir:\s*(.+)\s*$') {
                $target = $null
                try { $target = Resolve-PathSafe -Path $Matches[1] -BaseDir $f.DirectoryName } catch {}
                if ($target -and $target.StartsWith($rootPath, [System.StringComparison]::OrdinalIgnoreCase) -and (Test-Path -LiteralPath $target)) {
                    try {
                        attrib -h -s -r "$target" 2>$null | Out-Null
                        Remove-Item -LiteralPath $target -Recurse -Force -ErrorAction Stop
                    } catch {
                        $errors += "TARGET fail: $target :: $_"
                    }
                } else {
                    $skipped += "Skipped external gitdir for $($f.FullName): $target"
                }
            }
            Remove-Item -LiteralPath $f.FullName -Force -ErrorAction Stop
            $removedGitFiles += $f.FullName
        } catch {
            $errors += "FILE fail: $($f.FullName) :: $_"
        }
    }

    if ($IncludeMeta) {
        $meta = Get-ChildItem -LiteralPath $rootPath -Recurse -Force -File -Include .gitignore,.gitattributes,.gitmodules -ErrorAction SilentlyContinue
        foreach ($m in $meta) {
            try {
                Remove-Item -LiteralPath $m.FullName -Force -ErrorAction Stop
                $removedMetaFiles += $m.FullName
            } catch {
                $errors += "META fail: $($m.FullName) :: $_"
            }
        }
    }

} catch {
    $errors += $_.ToString()
}

# Summary
Write-Host "\nPurged .git directories: $($removedGitDirs.Count)" -ForegroundColor Green
Write-Host "Purged .git files:       $($removedGitFiles.Count)" -ForegroundColor Green
if ($IncludeMeta) { Write-Host "Purged meta files:      $($removedMetaFiles.Count)" -ForegroundColor Green }
if ($skipped.Count -gt 0) {
    Write-Host "\nSkipped (external targets):" -ForegroundColor Yellow
    $skipped | ForEach-Object { Write-Host "  $_" }
}
if ($errors.Count -gt 0) {
    Write-Host "\nErrors:" -ForegroundColor Red
    $errors | ForEach-Object { Write-Host "  $_" }
}
