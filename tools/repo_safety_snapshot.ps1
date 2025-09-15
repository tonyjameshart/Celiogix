# File: scripts/repo_safety_snapshot.ps1
<#!
Creates a safe snapshot and a clean WIP branch.
Why: avoids losing work, keeps master clean, and records current diff.
#>

[CmdletBinding()] 
param(
    [string]$RepoRoot = ".",               # Path to your repo (default: current dir)
    [switch]$IncludeUntracked = $false,      # Include untracked files in commit
    [string]$BranchPrefix = "wip"           # Prefix for branch name
)

# Fail fast if not a Git repo
Set-Location -Path $RepoRoot
$inside = (git rev-parse --is-inside-work-tree 2>$null)
if ($LASTEXITCODE -ne 0 -or $inside -ne "true") {
    throw "Not a git repository: $(Resolve-Path .)"
}

$top = (git rev-parse --show-toplevel).Trim()
Set-Location -Path $top

$ts = Get-Date -Format "yyyyMMdd-HHmmss"
$branch = "$BranchPrefix/$ts"

# 1) Safety artifacts
$patchFile = "safety-$ts.patch"
# Full working-tree diff (unstaged + staged)
$null = git diff > $patchFile

# ZIP only modified/untracked files (ignored files excluded via --exclude-standard)
$changed = (git ls-files -m -o --exclude-standard) | Where-Object { $_ -ne $null }
if ($changed.Count -gt 0) {
    $zipFile = "safety-$ts.zip"
    # Compress-Archive needs paths relative to current directory
    Compress-Archive -Path $changed -DestinationPath $zipFile -Force
}

# 2) New work branch
# Use switch -c (creates + checks out); safe if repo is dirty.
$null = git switch -c $branch

# 3) Stage & commit
$null = git add -u   # Stage tracked changes (modifications/deletions)
if ($IncludeUntracked) { $null = git add -A }

# Commit only if there is something staged
$null = git diff --cached --quiet
if ($LASTEXITCODE -ne 0) {
    $null = git commit -m "WIP: snapshot $ts"
} else {
    Write-Host "Nothing staged; commit skipped." -ForegroundColor Yellow
}

# 4) Show short status & hints
$null = git status -sb
$null = git remote -v

Write-Host "\nSafety artifacts:" -NoNewline
Write-Host " $patchFile" -ForegroundColor Cyan -NoNewline
if ($zipFile) { Write-Host ", $zipFile" -ForegroundColor Cyan }

Write-Host "\nNext steps:" -ForegroundColor Green
Write-Host "  • Review commit: git show --stat" 
Write-Host "  • Add untracked selectively: git add -p <path>" 
Write-Host "  • Undo a path to last commit: git restore -- <path>" 
Write-Host "  • Keep untracked but drop tracked edits: git reset --hard ; git clean -nd" 
Write-Host "  • Push branch: git push -u origin $branch"


# -------------------------------------------------------------
# File: .gitignore.suggested  (copy lines you want into your .gitignore)
# -------------------------------------------------------------
# Python
# __pycache__/
# *.py[cod]
# *.pyo
# *.pyd
# *.so
# *.egg-info/
# .venv/
# venv/
# env/
# ENV/
# build/
# dist/
# .eggs/
# pip-wheel-metadata/

# IDE / Editor
# .vscode/
# .idea/
# *.code-workspace

# OS noise
# .DS_Store
# Thumbs.db
# desktop.ini

# Logs & artifacts
# logs/
# *.log
# *.zip
# Celiogix.zip

# Data (enable carefully; tracked files stay tracked until removed with --cached)
# *.db
# *.sqlite*
# data/
# Working/
# assets/

# Notes:
# - Ignoring a path does NOT untrack it if already committed. To stop tracking but keep the file:
#     git rm --cached -- <path>   # then add the path to .gitignore and commit
