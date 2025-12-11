# Install Docker Desktop on Windows
# Run this script as administrator
$ErrorActionPreference = 'Stop'

Write-Host "🐳 Installing Docker Desktop for Windows..."

# Download Docker Desktop Installer
$dockerDesktopUrl = "https://desktop.docker.com/win/stable/Docker%20Desktop%20Installer.exe"
$installerPath = "$env:TEMP\DockerDesktopInstaller.exe"

Write-Host "📥 Downloading Docker Desktop..."
Invoke-WebRequest -Uri $dockerDesktopUrl -OutFile $installerPath

# Run installer
Write-Host "⚙️ Installing Docker Desktop (this may take a few minutes)..."
Start-Process -Wait $installerPath -ArgumentList "install --quiet"

Write-Host "🧹 Cleaning up..."
Remove-Item -Force $installerPath

Write-Host "✅ Docker Desktop installation complete!"
Write-Host "⚠️ Please restart your computer to complete setup."
Write-Host "After restart, run 'docker --version' to verify installation."
