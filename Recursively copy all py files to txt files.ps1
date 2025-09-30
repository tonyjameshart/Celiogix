param (
    [string]$SourceDir = ".",
    [string]$TargetDir = ".\TxtCopies"
)

# Resolve source directory to absolute path
$SourceDir = (Resolve-Path $SourceDir).Path

# Ensure target directory exists
if (-not (Test-Path $TargetDir)) {
    New-Item -ItemType Directory -Path $TargetDir | Out-Null
}

# Get all Python files recursively
Get-ChildItem -Path $SourceDir -Filter *.py -Recurse | ForEach-Object {
    # Build relative path manually (safe for PS 5.1)
    $relativePath = $_.FullName.Substring($SourceDir.Length).TrimStart('\','/')
    $targetPath   = Join-Path $TargetDir ($relativePath -replace '\.py$', '.txt')

    # Ensure subdirectory exists
    $targetDirPath = Split-Path $targetPath
    if (-not (Test-Path $targetDirPath)) {
        New-Item -ItemType Directory -Path $targetDirPath -Force | Out-Null
    }

    # Copy file content
    Get-Content $_.FullName -Raw | Set-Content -Path $targetPath -Encoding UTF8
    Write-Host "Copied $($_.FullName) -> $targetPath"
}