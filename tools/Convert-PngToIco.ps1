Add-Type -AssemblyName System.Drawing

function Convert-PngToIco {
    param (
        [Parameter(Mandatory)]
        [string]$PngPath,

        [string]$IcoPath = "$($PngPath -replace '\.png$', '.ico')"
    )

    if (-not (Test-Path $PngPath)) {
        Write-Error "❌ PNG file not found: $PngPath"
        return
    }

    try {
        Write-Host "🔄 Loading image..."
        $bitmap = [System.Drawing.Bitmap]::FromFile($PngPath)

        Write-Host "🧠 Creating icon handle..."
        $hIcon = $bitmap.GetHicon()
        $icon = [System.Drawing.Icon]::FromHandle($hIcon)

        Write-Host "💾 Saving to ICO: $IcoPath"
        $stream = New-Object System.IO.FileStream($IcoPath, [System.IO.FileMode]::Create)
        $icon.Save($stream)
        $stream.Close()

        Write-Host "✅ Conversion complete: $IcoPath"
    } catch {
        Write-Error "❌ Conversion failed: $_"
    }
}

# Example usage
#Convert-PngToIco -PngPath "C:\Path\To\your_image.png"