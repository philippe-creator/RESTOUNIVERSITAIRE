@echo off
REM Script de lancement - RESTO_BM avec Chat Vocal
REM ===============================================
REM Ce script ouvre 3 terminaux pour lancer tous les services

cls
echo.
echo ===============================================
echo   🎤 RESTO_BM - Chat Vocal
echo ===============================================
echo.

REM Vérifier si les répertoires existent
if not exist "resto_bm\clauv2\restou-app\backend\" (
  echo ❌ Erreur: Répertoire backend introuvable
  echo   Assurez-vous d'exécuter ce script depuis le dossier racine
  pause
  exit /b 1
)

REM ===============================================
REM 1. Backend API (Node.js)
REM ===============================================
echo 📌 Lancement Backend API (Port 5000)...
start "Backend API - http://localhost:5000" cmd /k "cd resto_bm\clauv2\restou-app\backend && npm install && npm start"
timeout /t 3

REM ===============================================
REM 2. API Vocale (Python Flask)
REM ===============================================
echo 📌 Lancement API Vocale (Port 5001)...
start "API Vocale - http://localhost:5001" cmd /k "cd CHT_BOT_RESTAURANT && pip install -r requirments.txt && pip install flask flask-cors && cd src && python voice_api.py"
timeout /t 3

REM ===============================================
REM 3. Frontend React
REM ===============================================
echo 📌 Lancement Frontend React (Port 3000)...
start "Frontend React - http://localhost:3000" cmd /k "cd resto_bm\clauv2\restou-app\frontend && npm install && npm start"
timeout /t 5

REM ===============================================
REM Affichage des informations
REM ===============================================
cls
echo.
echo ===============================================
echo   ✅ TOUS LES SERVICES LANCÉS!
echo ===============================================
echo.
echo 📍 Services disponibles:
echo.
echo   🔌 Backend API:     http://localhost:5000
echo   🎤 API Vocale:      http://localhost:5001
echo   🌐 Frontend App:    http://localhost:3000
echo.
echo 📱 Instructions:
echo.
echo   1. Ouvrez votre navigateur
echo   2. Allez sur http://localhost:3000
echo   3. Connectez-vous
echo   4. Cliquez sur 🎤 Chat Vocal
echo   5. Discutez avec le bot!
echo.
echo ⏸️  Fermez les fenêtres des terminaux pour arrêter
echo.
echo ===============================================
echo.

pause
