# 🎤 CHAT VOCAL RESTO_BM - INSTRUCTIONS FINALES

## ✨ TRÈS IMPORTANT: Tout est INTÉGRÉ dans l'app!

Le chat vocal n'est **plus** une interface séparée. C'est maintenant un **onglet à part entière** dans l'application RESTO_BM!

---

## 🚀 LANCEMENT FACILE (2 options)

### Option 1️⃣: Double-cliquez sur `lancer.bat` 🎯 RECOMMANDÉ

```
C:\Users\PHILIP\Desktop\RESTO_BM\lancer.bat
```

✅ Lance tout automatiquement dans 3 fenêtres PowerShell

### Option 2️⃣: Lancer manuellement dans 3 terminaux

**Terminal 1 - Backend API:**
```bash
cd C:\Users\PHILIP\Desktop\RESTO_BM\resto_bm\clauv2\restou-app\backend
npm install
npm start
```

**Terminal 2 - API Vocale:**
```bash
cd C:\Users\PHILIP\Desktop\RESTO_BM\CHT_BOT_RESTAURANT
pip install -r requirments.txt
pip install flask flask-cors
cd src
python voice_api.py
```

**Terminal 3 - Frontend:**
```bash
cd C:\Users\PHILIP\Desktop\RESTO_BM\resto_bm\clauv2\restou-app\frontend
npm install
npm start
```

---

## 📱 UTILISATION

### Après lancement:

1. **Allez sur:** `http://localhost:3000`

2. **Connectez-vous** avec vos identifiants

3. **Voyez la barre d'onglets au bas:**
   ```
   [🏠 Accueil] [🏪 Restos] [📅 Résa] [🎤 Chat Vocal] 🎯 [🔔 Notifs] [👤 Profil]
   ```

4. **Cliquez sur 🎤 Chat Vocal**

5. **Discutez avec le bot!**
   - Tapez un message OU
   - Cliquez 🎤 pour utiliser le microphone

---

## 🎯 Interfaces Affichées

### Page Chat Vocal

```
┌─ RESTO_BM ────────────────────────────────┐
│                                            │
│ 🤖 Chat RESTO_BM     ✅ API Connectée 🔊 🗑️ │
│ ├─────────────────────────────────────────│
│ │                                         │
│ │ Bot: Bienvenue! Je suis votre        │
│ │      assistant RESTO_BM. Vous       │
│ │      pouvez me parler...            │
│ │                                      │
│ │ Utilisateur: Quels restaurants?     │
│ │                                      │
│ │ Bot: 🏪 Voici les restaurants...    │
│ │                                      │
│ ├─────────────────────────────────────────│
│ │ [Tapez votre message...]             │
│ │ [🎤 Microphone] [📤 Envoyer]       │
│                                            │
│ [🏠] [🏪] [📅] [🎤] [🔔] [👤]          │
└────────────────────────────────────────────┘
```

---

## 🔄 Flux Complet

```
User se connecte
        ↓
App se lance sur http://localhost:3000
        ↓
User voit 6 onglets (Accueil, Restos, Résa, Chat Vocal, Notifs, Profil)
        ↓
User clique sur 🎤 Chat Vocal
        ↓
Interface de chat apparaît
        ↓
User tape OU clique 🎤
        ↓
Message envoyé à http://localhost:5001/api/chat
        ↓
API vocale traite avec LangChain (23 outils)
        ↓
Réponse revient
        ↓
Affichée dans l'interface
        ↓
Si voix activée → Boot parle aussi! 🔊
```

---

## ✅ Points de Vérification

Avant de lancer, assurez-vous:

- [x] Python 3.8+ installé: `python --version`
- [x] Node.js installé: `node --version`
- [x] npm installé: `npm --version`
- [x] Microphone connecté et testé
- [x] Ports 5000, 5001, 3000 libres:
  ```bash
  netstat -ano | findstr :5000
  netstat -ano | findstr :5001
  netstat -ano | findstr :3000
  ```

---

## 🆘 Dépannage

### ❌ Bot dit "API Déconnectée"

**Vérifiez que Terminal 2 affiche:**
```
🎤 API VOCALE RESTO_BM - LANCÉE
🌐 http://localhost:5001
```

Si absent, relancez Terminal 2 avec les commands ci-haut.

### ❌ React ne démarre pas

```bash
cd CHT_BOT_RESTAURANT
npm cache clean --force
cd resto_bm/clauv2/restou-app/frontend
npm cache clean --force
npm install
npm start
```

### ❌ Port déjà utilisé

```bash
# Trouver le processus
netstat -ano | findstr :XXXX

# Tuer le processus
taskkill /PID YYYY /F
```

### ❌ Module Python manquant

```bash
cd CHT_BOT_RESTAURANT
pip install -r requirments.txt --upgrade
pip install speech_recognition pyttsx3 flask flask-cors
```

---

## 📚 Documentation

Consultez ceci pour plus de détails:

1. **[INSTALLATION_CHAT_VOCAL.md](resto_bm/clauv2/restou-app/INSTALLATION_CHAT_VOCAL.md)**
   - Installation complète
   - Architecture d'intégration

2. **[GUIDE_VOCAL.md](CHT_BOT_RESTAURANT/GUIDE_VOCAL.md)**
   - Dépannage détaillé
   - Configuration avancée

3. **[COMMANDS.md](CHT_BOT_RESTAURANT/COMMANDS.md)**
   - Tous les commands
   - Exemples API

---

## 🎓 Fonctionnalités Disponibles

Tapez dans le chat:

```
"Quels restaurants sont ouverts?"
"Montre-moi les menus"
"Je réserve 2 places"
"Mes réservations"
"Combien j'ai de notifications?"
"Mets à jour mon profil"
"Mon QR code"
"Cherche [sujet]"
...et bien plus!
```

Le bot a **23 outils** à sa disposition!

---

## 🎉 C'EST PRÊT!

- ✅ Chat vocal intégré dans l'app
- ✅ Onglet 🎤 visible au bas
- ✅ Interface moderne et responsive
- ✅ Support voix complet
- ✅ 23 outils disponibles
- ✅ Prêt en production

---

## 🚀 À VOUS DE JOUER!

```bash
# Option 1 (Recommandé):
Double-cliquez sur: lancer.bat

# Ou Option 2:
npm start  (Terminal 3, après avoir lancé les autres)
```

**Puis allez sur:** `http://localhost:3000`

**Cliquez sur:** 🎤 Chat Vocal

**Profitez! 🎤✨**

---

**Questions?** Consultez les documentations listées ci-haut.

**Bon chat vocal!** 🤖💬
