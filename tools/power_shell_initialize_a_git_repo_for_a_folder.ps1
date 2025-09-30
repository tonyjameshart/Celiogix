# File: tools/init-repo.ps1
<#!
Initialize a Git repository at a given path, make an initial commit,
optionally add a remote and push.

Why: one command to turn any folder into a repo safely.
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory, Position=0)]
    [string]$Path,                                 # e.g., C:\Users\tonyj\Documents\repo

    [string]$Branch = "main",                     # default branch name
    [string]$Remote = $null,                       # e.g., https://github.com/user/repo.git
    [switch]$Push,                                 # attempt 'git push -u origin <branch>'
    [switch]$AddPythonGitignore,                   # add a minimal Python .gitignore
    [switch]$SetLocalIdentity,                     # set repo-local user.name/email if provided
    [string]$UserName,
    [string]$UserEmail,
    [switch]$MarkSafeDirectory                     # add to git config --global safe.directory
)

function Assert-Git() {
    $null = git --version 2>$null
    if ($LASTEXITCODE -ne 0) { throw "Git is not installed or not in PATH" }
}

function Ensure-Dir([string]$p) {
    if (-not (Test-Path -LiteralPath $p)) { New-Item -ItemType Directory -Path $p | Out-Null }
    return (Resolve-Path -LiteralPath $p).Path
}

function Git-Run([Parameter(ValueFromRemainingArguments)] $Args) {
    & git @Args
    if ($LASTEXITCODE -ne 0) { throw "git $Args failed" }
}

try {
    Assert-Git
    $root = Ensure-Dir -p $Path
    Set-Location -LiteralPath $root

    if (Test-Path -LiteralPath (Join-Path $root ".git")) {
        throw "Already a Git repository: $root"
    }

    # Initialize repo with branch (fallback logic if -b unsupported)
    & git init -b $Branch . 2>$null
    if ($LASTEXITCODE -ne 0) {
        Git-Run init .
        Git-Run symbolic-ref HEAD "refs/heads/$Branch"
    }

    if ($MarkSafeDirectory) {
        Git-Run config --global --add safe.directory "$root"
    }

    if ($SetLocalIdentity) {
        if ($UserName) { Git-Run config user.name  "$UserName" }
        if ($UserEmail) { Git-Run config user.email "$UserEmail" }
    }

    # Seed README if none exists
    if (-not (Test-Path -LiteralPath (Join-Path $root "README.md"))) {
        $repoName = Split-Path -Path $root -Leaf
        "# $repoName`n`nInitialized on $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" | 
            Out-File -LiteralPath (Join-Path $root "README.md") -Encoding UTF8 -NoNewline
    }

    if ($AddPythonGitignore) {
        $gi = @(
            "__pycache__/",
            "*.py[cod]",
            "*.pyo",
            "*.pyd",
            ".venv/",
            "venv/",
            "env/",
            "build/",
            "dist/",
            "*.egg-info/",
            "*.log"
        ) -join "`n"
        $gi | Out-File -LiteralPath (Join-Path $root ".gitignore") -Encoding UTF8
    }

    # Initial commit
    Git-Run add -A
    # commit may fail if nothing to commit; handle gracefully
    & git commit -m "Initial commit" 2>$null
    if ($LASTEXITCODE -ne 0) { Write-Host "Nothing to commit; empty repo." -ForegroundColor Yellow }

    if ($Remote) {
        Git-Run remote add origin "$Remote"
        if ($Push) {
            # First push
            & git push -u origin $Branch
            if ($LASTEXITCODE -ne 0) {
                Write-Warning "Push failed (auth/permissions?). Repo initialized locally; remote set as 'origin'."
            }
        }
    }

    # Show summary
    Write-Host "\nInitialized repo:" -ForegroundColor Green
    Write-Host "  Path:   $root"
    Write-Host "  Branch: $Branch"
    if ($Remote) { Write-Host "  Remote: origin -> $Remote" }
    & git status -sb
}
catch {
    Write-Error $_
    exit 1
}
