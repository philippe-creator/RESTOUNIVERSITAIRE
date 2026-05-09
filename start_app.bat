@echo off
echo ========================================
echo   🎤 RESTO_BM - Chat Vocal
echo ========================================
echo.

echo 📌 Lancement Backend API (Port 5000)...
start "Backend API" cmd /k "cd resto_bm\clauv2\restou-app\backend && npm install && npm start"

timeout /t 5 /nobreak >nul

echo 📌 Lancement API Vocale (Port 5001)...
start "API Vocale" cmd /k "cd CHT_BOT_RESTAURANT && pip install -r requirments.txt && pip install flask flask-cors && cd src && python api.py"

timeout /t 5 /nobreak >nul

echo 📌 Lancement Frontend React (Port 3000)...
start "Frontend React" cmd /k "cd resto_bm\clauv2\restou-app\frontend && npm install && npm start"

timeout /t 5 /nobreak >nul

echo.
echo ========================================
echo ✅ TOUS LES SERVICES LANCÉS!
echo ========================================
echo.
echo 📍 Services disponibles:
echo   🔌 Backend API:        http://localhost:5000
echo   🎤 API Vocale:        http://localhost:5001  
echo   🌐 Frontend App:      http://localhost:3000
echo.
echo 📱 Instructions:
echo   1. Ouvrez votre navigateur
echo   2. Allez sur http://localhost:3000
echo   3. Connectez-vous
echo   4. Cliquez sur 🎤 Chat Vocal
echo   5. Discutez avec le bot!
echo.
echo ⏸️  Fermez les fenêtres pour arrêter les services
echo ========================================
echo.
pause
