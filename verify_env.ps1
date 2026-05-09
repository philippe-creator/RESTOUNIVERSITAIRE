#!/usr/bin/env powershell
<#
    Script de vérification d'environnement pour RESTO_BM
    Vérifie que tout est prêt avant de lancer l'application
#>

$GREEN = "`e[92m"
$RED = "`e[91m"
$YELLOW = "`e[93m"
$BLUE = "`e[94m"
$RESET = "`e[0m"

$checks_passed = 0
$checks_total = 0

function Check-Command {
    param(
        [string]$Name,
        [string]$Command,
        [string]$Description
    )
    
    $global:checks_total++
    Write-Host "$YELLOW[$checks_total]$RESET $Description..."
    
    try {
        $result = & $Command 2>&1
        Write-Host "$GREEN✓ $Name trouvé: $result$RESET"
        $global:checks_passed++
        return $true
    } catch {
        Write-Host "$RED✗ $Name non trouvé!$RESET"
        return $false
    }
}

function Check-File {
    param(
        [string]$Path,
        [string]$Description
    )
    
    $global:checks_total++
    Write-Host "$YELLOW[$checks_total]$RESET $Description..."
    
    if (Test-Path $Path) {
        Write-Host "$GREEN✓ Fichier trouvé$RESET"
        $global:checks_passed++
        return $true
    } else {
        Write-Host "$RED✗ Fichier manquant: $Path$RESET"
        return $false
    }
}

# Header
Write-Host "$BLUE========================================$RESET"
Write-Host "$BLUE    VÉRIFICATION PRÉREQUIS RESTO_BM$RESET"
Write-Host "$BLUE========================================$RESET`n"

# Vérifications
Check-Command "Node.js" "node --version" "Vérification Node.js"
Check-Command "npm" "npm --version" "Vérification npm"
Check-Command "Python" "python --version" "Vérification Python"
Check-Command "pip" "pip --version" "Vérification pip"

Check-File ".venv\Scripts\python.exe" "Env virtuel Python"
Check-File "resto_bm\clauv2\restou-app\backend\package.json" "Backend package.json"
Check-File "resto_bm\clauv2\restou-app\frontend\package.json" "Frontend package.json"
Check-File "CHT_BOT_RESTAURANT\requirements.txt" "Dépendances bot Python"

# Résultat
Write-Host "`n$BLUE========================================$RESET"
Write-Host "Résultats: $checks_passed/$checks_total"
Write-Host "$BLUE========================================$RESET`n"

if ($checks_passed -eq $checks_total) {
    Write-Host "$GREEN✓ TOUS LES PRÉREQUIS SONT PRÉSENTS!$RESET`n"
    Write-Host "$YELLOW💡 Prochaine étape: .\start_all.ps1$RESET"
} else {
    Write-Host "$RED✗ CERTAINS PRÉREQUIS MANQUENT!$RESET`n"
    Write-Host "$YELLOW📖 Consultez BOT_GUIDE.md pour l'installation$RESET"
}
