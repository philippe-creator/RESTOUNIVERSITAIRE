#!/usr/bin/env pwsh
# Script de lancement complet - RESTO_BM avec Chat Vocal (Corrigé)
# ======================================================

# Configuration
$homeDir = $PSScriptRoot
$backendDir = Join-Path $homeDir "resto_bm\clauv2\restou-app\backend"
$apiDir = Join-Path $homeDir "CHT_BOT_RESTAURANT"
$frontendDir = Join-Path $homeDir "resto_bm\clauv2\restou-app\frontend"

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  🎤 RESTO_BM - Chat Vocal" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# =========================================
# 1. BACKEND API (Node.js)
# =========================================
Write-Host "📌 Lancement Backend API (Port 5000)..." -ForegroundColor Yellow

$backendScript = @"
cd "$backendDir"
npm install
Write-Host "✅ Backend démarré sur http://localhost:5000" -ForegroundColor Green
npm start
"@

$backendPath = Join-Path $env:TEMP "start_backend.ps1"
Set-Content -Path $backendPath -Value $backendScript

Start-Process powershell.exe -ArgumentList "-NoExit", "-File", $backendPath `
  -WindowStyle Normal -PassThru | Out-Null

Start-Sleep -Seconds 3

# =========================================
# 2. API VOCALE (Python Flask)
# =========================================
Write-Host "📌 Lancement API Vocale (Port 5001)..." -ForegroundColor Yellow

$apiScript = @"
cd "$apiDir"
pip install -r requirments.txt 2>&1 | Out-Null
pip install flask flask-cors 2>&1 | Out-Null

cd "$apiDir\src"
Write-Host "✅ API Vocale démarrée sur http://localhost:5001" -ForegroundColor Green
python api.py
"@

$apiPath = Join-Path $env:TEMP "start_api.ps1"
Set-Content -Path $apiPath -Value $apiScript

Start-Process powershell.exe -ArgumentList "-NoExit", "-File", $apiPath `
  -WindowStyle Normal -PassThru | Out-Null

Start-Sleep -Seconds 3

# =========================================
# 3. FRONTEND REACT
# =========================================
Write-Host "📌 Lancement Frontend React (Port 3000)..." -ForegroundColor Yellow

$frontendScript = @"
cd "$frontendDir"
npm install
Write-Host "✅ Frontend démarré sur http://localhost:3000" -ForegroundColor Green
npm start
"@

$frontendPath = Join-Path $env:TEMP "start_frontend.ps1"
Set-Content -Path $frontendPath -Value $frontendScript

Start-Process powershell.exe -ArgumentList "-NoExit", "-File", $frontendPath `
  -WindowStyle Normal -PassThru | Out-Null

Start-Sleep -Seconds 5

# =========================================
# AFFICHAGE DES INFORMATIONS
# =========================================
Write-Host "`n========================================" -ForegroundColor Green
Write-Host "✅ TOUS LES SERVICES LANCÉS!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

Write-Host "`n📍 Services disponibles:
" -ForegroundColor Cyan

Write-Host "  🔌 Backend API:        " -NoNewline -ForegroundColor Yellow
Write-Host "http://localhost:5000" -ForegroundColor Green

Write-Host "  🎤 API Vocale:        " -NoNewline -ForegroundColor Yellow
Write-Host "http://localhost:5001" -ForegroundColor Green

Write-Host "  🌐 Frontend App:      " -NoNewline -ForegroundColor Yellow
Write-Host "http://localhost:3000" -ForegroundColor Green

Write-Host "`n📱 Instructions:
" -ForegroundColor Cyan

Write-Host "  1. Ouvrez votre navigateur" -ForegroundColor White
Write-Host "  2. Allez sur http://localhost:3000" -ForegroundColor White
Write-Host "  3. Connectez-vous" -ForegroundColor White
Write-Host "  4. Cliquez sur 🎤 Chat Vocal" -ForegroundColor White
Write-Host "  5. Discutez avec le bot!" -ForegroundColor White

Write-Host "`n⏸️  Appuyez sur Ctrl+C pour arrêter les services" -ForegroundColor Yellow
Write-Host "`n========================================`n" -ForegroundColor Green

# Garder la fenêtre ouverte
Read-Host "Appuyez sur Entrée pour continuer"
