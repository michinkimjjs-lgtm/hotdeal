$ErrorActionPreference = "Stop"

try {
    Write-Host "1. Checking for locks..."
    if (Test-Path .git/index.lock) { 
        Remove-Item .git/index.lock -Force 
        Write-Host " - Removed stale lock file."
    }

    Write-Host "2. Staging all changes..."
    git add .

    Write-Host "3. Committing..."
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    git commit --allow-empty -m "Hotfix: Indentation Error $timestamp"
    
    Write-Host "4. Pushing to GitHub..."
    git push origin main

    Write-Host "SUCCESS: Deployment completed."
} catch {
    Write-Host "ERROR: $($_.Exception.Message)"
    exit 1
}
