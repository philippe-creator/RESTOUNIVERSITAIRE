"""
API Flask pour le Bot RESTO_BM avec LangChain & LangGraph
Utilise l'agent LangGraph avec mémoire
Port: 5001 pour ne pas interférer avec le backend Node.js
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
from dotenv import load_dotenv
from datetime import datetime

import jwt
# Import de l'agent et du contexte de token
from agent import create_agent_instance, memory
from tools import user_token_var, user_role_var

load_dotenv()

app = Flask(__name__)
CORS(app)

# Historique global pour debug (fallback)
conversation_history = []

# Cache des agents par rôle
_agent_cache = {}

JWT_SECRET = os.getenv("JWT_SECRET", "votre_secret_jwt_super_securise_2026")

# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def _extract_role_from_jwt(token):
    """Extrait le rôle de l'utilisateur depuis le JWT."""
    if not token:
        return "etudiant"
    try:
        decoded = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return decoded.get("role", "etudiant")
    except jwt.ExpiredSignatureError:
        print("JWT expiré")
        return "etudiant"
    except jwt.InvalidTokenError as e:
        print(f"JWT invalide: {e}")
        return "etudiant"


def _get_agent_for_role(role):
    """Récupère ou crée un agent pour un rôle donné."""
    if role not in _agent_cache:
        try:
            _agent_cache[role] = create_agent_instance(role=role)
            print(f"Agent créé pour le rôle: {role}")
        except Exception as e:
            print(f"Erreur création agent ({role}): {e}")
            return None
    return _agent_cache[role]

# ─────────────────────────────────────────────
# INITIALISATION
# ─────────────────────────────────────────────

# Pré-créer l'agent par défaut (etudiant)
try:
    _agent_cache["etudiant"] = create_agent_instance(role="etudiant")
    print("Agent LangGraph initialise (etudiant)")
except Exception as e:
    print(f"Erreur initialisation agent: {e}")

# ─────────────────────────────────────────────
# ENDPOINTS
# ─────────────────────────────────────────────

@app.route('/api/health', methods=['GET'])
def health():
    """Vérifier que l'API est opérationnelle"""
    return jsonify({
        "status": "OK",
        "message": "Bot API RESTO_BM is running",
        "timestamp": datetime.now().isoformat(),
        "agent_ready": len(_agent_cache) > 0
    }), 200


@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Endpoint principal pour communiquer avec le bot.
    Extrait le rôle du JWT pour sélectionner l'agent approprié.
    
    Body:
    {
        "message": "string - message utilisateur",
        "session_id": "string - optionnel, défaut à 'default'",
        "token": "string - JWT token de l'utilisateur"
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({
                "success": False,
                "error": "Message requis",
                "response": "Veuillez envoyer un message"
            }), 400

        user_message = data.get('message', '').strip()
        session_id = data.get('session_id', 'default_session')
        user_token = data.get('token')
        
        if not user_message:
            return jsonify({
                "success": False,
                "error": "Message vide",
                "response": "Message vide"
            }), 400

        # ─── Extraction du rôle depuis le JWT ───
        user_role = _extract_role_from_jwt(user_token)
        print(f"\n[{session_id}] Rôle détecté: {user_role}")
        
        # ─── Récupérer l'agent filtré par rôle ───
        agent = _get_agent_for_role(user_role)
        if agent is None:
            return jsonify({
                "success": False,
                "error": "Agent non initialisé",
                "response": "❌ Le bot n'est pas prêt. Veuillez redémarrer l'API."
            }), 500

        # Log en historique local pour debug
        conversation_history.append({
            "role": "user",
            "message": user_message,
            "session_id": session_id,
            "user_role": user_role,
            "timestamp": datetime.now().isoformat()
        })

        print(f"[{session_id}] Utilisateur ({user_role}): {user_message}")

        try:
            # Fixer le token ET le rôle dans le contexte pour les outils
            token_reset = user_token_var.set(user_token)
            role_reset = user_role_var.set(user_role)
            
            # Appel à LangGraph avec gestion de la mémoire (thread_id)
            config = {
                "configurable": {
                    "thread_id": session_id,
                    "token": user_token
                }
            }
            
            response = agent.invoke(
                {"messages": [("user", user_message)]},
                config=config
            )
            
            # Réinitialiser le contexte après l'appel
            user_token_var.reset(token_reset)
            user_role_var.reset(role_reset)

            # Extraire la réponse du bot
            bot_response = response["messages"][-1].content
            
            print(f"[{session_id}] Bot: (reponse de {len(bot_response)} caracteres)")

        except Exception as e:
            bot_response = f"Erreur lors du traitement: {str(e)[:200]}"
            print(f"Erreur agent: {e}")

        # Log en historique
        conversation_history.append({
            "role": "bot",
            "message": bot_response,
            "session_id": session_id,
            "timestamp": datetime.now().isoformat()
        })

        return jsonify({
            "success": True,
            "response": bot_response,
            "message": user_message,
            "user_role": user_role,
            "timestamp": datetime.now().isoformat()
        }), 200

    except Exception as e:
        print(f"Erreur endpoint /api/chat: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "response": f"Erreur serveur: {str(e)[:200]}"
        }), 500


@app.route('/api/chat/history', methods=['GET'])
def get_history():
    """Récupère l'historique de conversation (debug)"""
    try:
        session_id = request.args.get('session_id', 'default_session')
        history = [msg for msg in conversation_history if msg.get("session_id") == session_id]
        
        return jsonify({
            "success": True,
            "data": history,
            "count": len(history)
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/chat/clear', methods=['POST'])
def clear_history():
    """Efface l'historique de conversation"""
    global conversation_history
    try:
        data = request.get_json() or {}
        session_id = data.get('session_id', 'default_session')
        
        conversation_history = [msg for msg in conversation_history if msg.get("session_id") != session_id]
        
        return jsonify({
            "success": True,
            "message": "Historique effacé",
            "timestamp": datetime.now().isoformat()
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/agent/status', methods=['GET'])
def agent_status():
    """Récupère le statut de l'agent"""
    try:
        return jsonify({
            "success": True,
            "agent_ready": len(_agent_cache) > 0,
            "cached_roles": list(_agent_cache.keys()),
            "timestamp": datetime.now().isoformat()
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# ─────────────────────────────────────────────
# GESTION D'ERREURS
# ─────────────────────────────────────────────

@app.errorhandler(404)
def not_found(e):
    return jsonify({
        "success": False,
        "error": "Endpoint non trouvé"
    }), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({
        "success": False,
        "error": "Erreur serveur"
    }), 500

# ─────────────────────────────────────────────
# LANCER L'APP
# ─────────────────────────────────────────────

if __name__ == '__main__':
    print("\n" + "="*60)
    print("BOT API RESTO_BM - DEMARRAGE (Multi-Rôles)")
    print("="*60)
    print(f"Port: 5001")
    print(f"Mode: {os.getenv('FLASK_ENV', 'development')}")
    print(f"JWT Secret: {'***' + JWT_SECRET[-4:] if len(JWT_SECRET) > 4 else '***'}")
    print("\nEndpoints disponibles:")
    print("  GET  /api/health                   - Vérifier l'état du service")
    print("  POST /api/chat                     - Envoyer un message au bot")
    print("  GET  /api/chat/history            - Vérifier l'historique")
    print("  POST /api/chat/clear              - Effacer l'historique")
    print("  GET  /api/agent/status            - Statut de l'agent")
    print("="*60 + "\n")
    
    app.run(
        host='0.0.0.0',
        port=5001,
        debug=False,
        use_reloader=False
    )
