import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver

from tools import (
    # Documents
    search_documents,
    # Restaurants
    list_restaurants,
    get_restaurant_details,
    # Menus
    list_menus,
    list_restaurant_menus,
    get_menu_details,
    # Réservations
    make_reservation,
    get_my_reservations,
    cancel_reservation,
    get_reservation_details,
    # Paiements
    get_my_payments,
    get_payment_receipt,
    # Notifications
    get_my_notifications,
    count_unread_notifications,
    mark_notification_as_read,
    mark_all_notifications_as_read,
    # Profil
    get_profile,
    update_profile,
    # QR Codes
    get_qrcode_by_reservation,
    validate_qrcode,
    scan_qrcode,
    # Utilitaires
    get_today_date,
    # Admin sécurisés
    get_resto_stats,
    list_registered_users,
    remove_user_from_resto,
)

load_dotenv()

# Mémoire globale pour l'agent
memory = MemorySaver()

# ─── Outils de base (tous les rôles) ────────────────────────────────
BASE_TOOLS = [
    list_restaurants,
    get_restaurant_details,
    list_menus,
    list_restaurant_menus,
    get_menu_details,
    make_reservation,
    get_my_reservations,
    cancel_reservation,
    get_reservation_details,
    get_my_payments,
    get_payment_receipt,
    get_my_notifications,
    count_unread_notifications,
    mark_notification_as_read,
    mark_all_notifications_as_read,
    get_profile,
    update_profile,
    get_qrcode_by_reservation,
    validate_qrcode,
    scan_qrcode,
    get_today_date,
]

# ─── Outils admin (admin et admin_pro uniquement) ───────────────────
ADMIN_TOOLS = [
    get_resto_stats,
    list_registered_users,
    remove_user_from_resto,
]

# ─── Prompts système par rôle ───────────────────────────────────────
SYSTEM_PROMPTS = {
    "etudiant": """Tu es un assistant IA intelligent du restaurant universitaire RESTO_BM.
Tu aides les ÉTUDIANTS avec :
- Consulter les restaurants ouverts et leurs menus
- Faire et gérer des réservations (réduction automatique de 50% appliquée)
- Consulter les paiements et reçus
- Gérer les notifications et le profil
- Valider les QR codes
- Répondre à des questions via la recherche documentaire

IMPORTANT: Les étudiants bénéficient d'une réduction de 50% automatique sur tous les repas.
Tu n'as PAS accès aux outils d'administration (statistiques, gestion utilisateurs).
""",

    "citoyen": """Tu es un assistant IA intelligent du restaurant universitaire RESTO_BM.
Tu aides les CITOYENS avec :
- Consulter les restaurants ouverts et leurs menus
- Faire et gérer des réservations (tarif plein, sans réduction)
- Consulter les paiements et reçus
- Gérer les notifications et le profil
- Valider les QR codes
- Répondre à des questions via la recherche documentaire

IMPORTANT: Les citoyens paient le tarif plein (100% du prix).
Tu n'as PAS accès aux outils d'administration.
""",

    "admin_pro": """Tu es un assistant IA intelligent du restaurant universitaire RESTO_BM.
Tu aides un ADMINISTRATEUR DE RESTAURANT (Admin Pro) avec :
- Toutes les fonctionnalités utilisateur standard
- 📊 Consulter les statistiques de SON restaurant (get_resto_stats)
- 👥 Lister les utilisateurs inscrits à son restaurant (list_registered_users)
- ❌ Retirer un utilisateur de son restaurant (remove_user_from_resto)

IMPORTANT: Tu as accès aux outils d'administration. Les données sont filtrées pour ne montrer que celles du restaurant géré par cet admin.
""",

    "admin": """Tu es un assistant IA intelligent du restaurant universitaire RESTO_BM.
Tu aides le SUPER ADMINISTRATEUR avec :
- Toutes les fonctionnalités utilisateur standard
- 📊 Consulter les statistiques GLOBALES de tous les restaurants (get_resto_stats)
- 👥 Lister TOUS les utilisateurs inscrits (list_registered_users)
- ❌ Retirer un utilisateur globalement (remove_user_from_resto)

IMPORTANT: Tu as une visibilité GLOBALE sur tous les restaurants et utilisateurs.
""",
}

COMMON_INSTRUCTIONS = """
INSTRUCTIONS COMMUNES:
- N'hésite pas à appeler plusieurs outils à la suite si nécessaire.
- Utilise toujours get_today_date() si on te parle d'"aujourd'hui", "demain", etc.
- Pour une réservation, si l'utilisateur demande "demain", trouve d'abord la date.
- Réponds en français, de manière claire, structurée et amicale.
- Utilise le formatage Markdown (listes, gras) pour rendre tes réponses lisibles.
- Si un outil te fournit un lien image (QR Code ![alt](url)), inclus-le tel quel dans ta réponse.
"""


def create_agent_instance(role="etudiant"):
    """
    Crée une instance d'agent avec des outils et un prompt filtrés selon le rôle.
    
    Args:
        role: Le rôle de l'utilisateur ('etudiant', 'citoyen', 'admin', 'admin_pro')
    """
    # Sélection des outils selon le rôle
    tools = list(BASE_TOOLS)
    
    # Ajouter RAG si disponible
    if search_documents is not None:
        tools.append(search_documents)
    
    # Ajouter les outils admin pour les rôles autorisés
    if role in ('admin', 'admin_pro'):
        tools.extend(ADMIN_TOOLS)

    llm = ChatOpenAI(
        model="openai/gpt-4o-mini",
        api_key=os.getenv("OPENROUTER_API_KEY"),
        base_url="https://openrouter.ai/api/v1"
    )

    # Prompt personnalisé selon le rôle
    role_prompt = SYSTEM_PROMPTS.get(role, SYSTEM_PROMPTS["etudiant"])
    system_prompt = role_prompt + COMMON_INSTRUCTIONS

    agent_executor = create_react_agent(
        llm,
        tools=tools,
        prompt=system_prompt,
        checkpointer=memory
    )

    return agent_executor