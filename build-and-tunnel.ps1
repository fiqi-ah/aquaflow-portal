# 1. Start Backend Tunnel and capture URL
Write-Host "Starting Backend Tunnel..."
$backendProcess = Start-Process cloudflared -ArgumentList "tunnel --url http://localhost:8000" -PassThru -RedirectStandardOutput "backend_tunnel.log" -NoNewWindow
Start-Sleep -Seconds 5
$backendUrl = Select-String -Path "backend_tunnel.log" -Pattern "https://.*\.trycloudflare\.com" | ForEach-Object { $_.Matches.Value }
Stop-Process -Id $backendProcess.Id -Force
Remove-Item "backend_tunnel.log"

if (-not $backendUrl) { Write-Error "Failed to get Backend URL"; exit 1 }
Write-Host "Backend URL: $backendUrl"

# 2. Set Env Var and Build Frontend
$env:VITE_API_URL = $backendUrl
Write-Host "Building Frontend with API URL: $backendUrl"
Set-Location frontend
npm run build
Set-Location ..

# 3. Serve Static Files
Write-Host "Serving Static Files on port 5173..."
$serverProcess = Start-Process python -ArgumentList "-m", "http.server", "5173", "--directory", "./frontend/dist" -PassThru -NoNewWindow

# 4. Start Frontend Tunnel
Write-Host "Starting Frontend Tunnel..."
$frontendProcess = Start-Process cloudflared -ArgumentList "tunnel --url http://localhost:5173" -PassThru -RedirectStandardOutput "frontend_tunnel.log" -NoNewWindow
Start-Sleep -Seconds 5
$frontendUrl = Select-String -Path "frontend_tunnel.log" -Pattern "https://.*\.trycloudflare\.com" | ForEach-Object { $_.Matches.Value }

Write-Host "`n========================================="
Write-Host "PUBLIC FRONTEND URL: $frontendUrl"
Write-Host "PUBLIC BACKEND URL:  $backendUrl"
Write-Host "=========================================`n"

# Keep running until Ctrl+C
Wait-Process -Id $serverProcess.Id, $frontendProcess.Id