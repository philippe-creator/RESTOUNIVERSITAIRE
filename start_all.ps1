#!/usr/bin/env powershell
<#
    Script de lancement complet de l'application RESTO_BM
    Lance le backend Node.js, le frontend React, et le bot Python
#>

# Couleurs pour le terminal
$GREEN = "`e[92m"
$RED = "`e[91m"
$YELLOW = "`e[93m"
$BLUE = "`e[94m"
$RESET = "`e[0m"

Write-Host "$BLUE========================================$RESET"
Write-Host "$BLUE    RESTO_BM - LANCEMENT COMPLET$RESET"
Write-Host "$BLUE========================================$RESET`n"

# Vérifier Node.js
Write-Host "$YELLOW[1]$RESET Vérification de Node.js..."
$node_version = node --version 2>&1
if ($?) {
    Write-Host "$GREEN✓ Node.js trouvé: $node_version$RESET"
} else {
    Write-Host "$RED✗ Node.js non trouvé!$RESET"
    exit
}

# Vérifier Python
Write-Host "$YELLOW[2]$RESET Vérification de Python..."
$python_version = python --version 2>&1
if ($?) {
    Write-Host "$GREEN✓ Python trouvé: $python_version$RESET"
} else {
    Write-Host "$RED✗ Python non trouvé!$RESET"
    exit
}

# Éléments
$backend_path = "$PSScriptRoot\resto_bm\clauv2\restou-app\backend"
$frontend_path = "$PSScriptRoot\resto_bm\clauv2\restou-app\frontend"
$bot_path = "$PSScriptRoot\CHT_BOT_RESTAURANT\src"

Write-Host "`n$BLUE========================================$RESET"
Write-Host "$BLUE    DÉMARRAGE DES SERVICES$RESET"
Write-Host "$BLUE========================================$RESET`n"

# Terminal 1: Backend Node.js
Write-Host "$YELLOW[3]$RESET Lancement du backend Node.js (port 5000)..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$backend_path'; npm start"
Write-Host "$GREEN✓ Backend lancé$RESET"
Start-Sleep -Seconds 3

# Terminal 2: Frontend React
Write-Host "$YELLOW[4]$RESET Lancement du frontend React (port 3000)..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$frontend_path'; npm start"
Write-Host "$GREEN✓ Frontend lancé$RESET"
Start-Sleep -Seconds 3

# Terminal 3: Bot Python
Write-Host "$YELLOW[5]$RESET Lancement du bot Python (port 5001)..."
$activate_script = "$PSScriptRoot\.venv\Scripts\Activate.ps1"
if (Test-Path $activate_script) {
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "& '$activate_script'; cd '$bot_path'; python api.py"
} else {
    Write-Host "$RED✗ Environnement virtuel non trouvé!$RESET"
    exit
}
Write-Host "$GREEN✓ Bot lancé$RESET"

Write-Host "`n$BLUE========================================$RESET"
Write-Host "$GREEN✓✓✓ TOUS LES SERVICES SONT LANCÉS$RESET"
Write-Host "$BLUE========================================$RESET`n"

Write-Host "$YELLOW📍 URLS:$RESET"
Write-Host "  Frontend: http://localhost:3000"
Write-Host "  Backend:  http://localhost:5000/api"
Write-Host "  Bot API:  http://localhost:5001/api"
Write-Host "`n$YELLOW💡 Conseil:$RESET Ouvrez VoiceChat.jsx pour utiliser le bot!"
