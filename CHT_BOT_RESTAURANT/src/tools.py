"""
Tools LangChain pour le Bot RESTO_BM
Intègre tous les endpoints de l'API Node.js backend
"""

from langchain.tools import tool
import requests
import json
from datetime import datetime, timedelta
from typing import Optional
from contextvars import ContextVar

# Variable de contexte pour le token de l'utilisateur actuel
user_token_var = ContextVar("user_token", default=None)
# Variable de contexte pour le rôle de l'utilisateur actuel
user_role_var = ContextVar("user_role", default="etudiant")

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
BASE_URL = "http://localhost:5000/api"

# Cache pour le token et l'utilisateur courant
_auth_cache = {
    "token": None,
    "user": None,
    "expires_at": None
}

# ─────────────────────────────────────────────
# AUTHENTIFICATION
# ─────────────────────────────────────────────

def _get_token() -> Optional[str]:
    """Récupère le token JWT (priorité au token de contexte, puis cache)."""
    global _auth_cache
    
    # 1. Vérifier si un token est présent dans le contexte de la requête actuelle
    ctx_token = user_token_var.get()
    if ctx_token:
        return ctx_token

    try:
        # 2. Sinon, utiliser le token système en cache (fallback)
        if _auth_cache["token"] and _auth_cache["expires_at"] and datetime.now() < _auth_cache["expires_at"]:
            return _auth_cache["token"]
        
        # Sinon, se reconnecter
        response = requests.post(
            f"{BASE_URL}/auth/connexion",
            json={
                "email": "youssef@univ.ma",
                "motDePasse": "1234"
            },
            timeout=5
        )
        
        if response.status_code != 200:
            return None
        
        data = response.json()
        _auth_cache["token"] = data.get("token")
        _auth_cache["user"] = data.get("utilisateur")
        # Expire dans 24h
        _auth_cache["expires_at"] = datetime.now() + timedelta(hours=24)
        
        return _auth_cache["token"]
    
    except Exception as e:
        print(f"❌ Erreur authentication: {e}")
        return None

def _headers() -> dict:
    """Construit les headers avec le token JWT."""
    token = _get_token()
    return {
        "Authorization": f"Bearer {token}" if token else "",
        "Content-Type": "application/json"
    }

# ─────────────────────────────────────────────
# 🏪 RESTAURANTS
# ─────────────────────────────────────────────

@tool
def list_restaurants(open_only: bool = True) -> str:
    """
    Récupère la liste de tous les restaurants.
    
    Args:
        open_only: Si True, ne retourne que les restaurants ouverts
    
    Returns: Liste formatée des restaurants avec statut et horaires
    """
    try:
        params = {}
        if open_only:
            params["estOuvert"] = "true"
        
        response = requests.get(
            f"{BASE_URL}/restaurants",
            params=params,
            timeout=5
        )
        
        if response.status_code != 200:
            return "❌ Impossible de récupérer les restaurants"
        
        data = response.json()
        restaurants = data.get("data", [])
        
        if not restaurants:
            return "❌ Aucun restaurant " + ("ouvert" if open_only else "disponible")
        
        result = f"🏪 Restaurants {'ouverts' if open_only else 'disponibles'}:\n\n"
        for i, r in enumerate(restaurants, 1):
            status = "✅ OUVERT" if r.get("estOuvert") else "🔴 FERMÉ"
            result += f"{i}. {r['nom']}\n"
            result += f"   Statut: {status}\n"
            result += f"   Adresse: {r.get('adresse', 'N/A')}\n"
            result += f"   Horaires: {r.get('horairesOuverture', 'N/A')}\n"
            result += f"   Contact: {r.get('telephone', 'N/A')}\n"
            result += f"   ID: {r['_id']}\n\n"
        
        return result
    
    except Exception as e:
        return f"❌ Erreur: {str(e)}"


@tool
def get_restaurant_details(restaurant_id: str) -> str:
    """
    Récupère les détails complets d'un restaurant.
    
    Args:
        restaurant_id: L'ID du restaurant
    
    Returns: Informations détaillées du restaurant
    """
    try:
        response = requests.get(
            f"{BASE_URL}/restaurants/{restaurant_id}",
            timeout=5
        )
        
        if response.status_code != 200:
            return f"❌ Restaurant {restaurant_id} introuvable"
        
        data = response.json()
        r = data.get("data", {})
        
        result = f"🏪 Détails de {r['nom']}\n\n"
        result += f"Adresse: {r.get('adresse', 'N/A')}\n"
        result += f"Téléphone: {r.get('telephone', 'N/A')}\n"
        result += f"Email: {r.get('email', 'N/A')}\n"
        result += f"Horaires: {r.get('horairesOuverture', 'N/A')}\n"
        result += f"Statut: {'✅ OUVERT' if r.get('estOuvert') else '🔴 FERMÉ'}\n"
        result += f"Capacité: {r.get('capacite', 'N/A')} places\n"
        result += f"Gérant: {r.get('gerantId', {}).get('nom', 'N/A')}\n"
        
        return result
    
    except Exception as e:
        return f"❌ Erreur: {str(e)}"

# ─────────────────────────────────────────────
# 📋 MENUS
# ─────────────────────────────────────────────

@tool
def list_menus(restaurant_id: Optional[str] = None, date: Optional[str] = None, active_only: bool = True) -> str:
    """
    Récupère la liste des menus disponibles.
    
    Args:
        restaurant_id: Filtrer par restaurant (optionnel)
        date: Filtrer par date YYYY-MM-DD (optionnel)
        active_only: Si True, ne retourne que les menus actifs
    
    Returns: Liste formatée des menus
    """
    try:
        params = {}
        if restaurant_id:
            params["restaurantId"] = restaurant_id
        if date:
            params["date"] = date
        if active_only:
            params["actif"] = "true"
        
        response = requests.get(
            f"{BASE_URL}/menus",
            params=params,
            timeout=5
        )
        
        if response.status_code != 200:
            return "❌ Impossible de récupérer les menus"
        
        data = response.json()
        menus = data.get("data", [])
        
        if not menus:
            return "❌ Aucun menu disponible pour ces critères"
        
        result = "📋 Menus disponibles:\n\n"
        for i, m in enumerate(menus, 1):
            result += f"{i}. {m['typeRepas']}\n"
            result += f"   Prix: {m.get('prix', 'N/A')} DH\n"
            result += f"   Restaurant: {m.get('restaurantId', {}).get('nom', 'N/A')}\n"
            result += f"   Date: {m.get('date', 'N/A')}\n"
            result += f"   Description: {m.get('description', 'N/A')}\n"
            result += f"   ID: {m['_id']}\n"
            result += f"   Statut: {'✅ Actif' if m.get('actif') else '🔴 Inactif'}\n\n"
        
        return result
    
    except Exception as e:
        return f"❌ Erreur: {str(e)}"


@tool
def get_menu_details(menu_id: str) -> str:
    """
    Récupère les détails complets d'un menu.
    
    Args:
        menu_id: L'ID du menu
    
    Returns: Informations détaillées du menu
    """
    try:
        response = requests.get(
            f"{BASE_URL}/menus/{menu_id}",
            timeout=5
        )
        
        if response.status_code != 200:
            return f"❌ Menu {menu_id} introuvable"
        
        data = response.json()
        m = data.get("data", {})
        
        result = f"📋 Menu: {m['typeRepas']}\n\n"
        result += f"Prix: {m.get('prix', 'N/A')} DH\n"
        result += f"Restaurant: {m.get('restaurantId', {}).get('nom', 'N/A')}\n"
        result += f"Date: {m.get('date', 'N/A')}\n"
        result += f"Description: {m.get('description', 'N/A')}\n"
        result += f"Ingredients: {m.get('ingredients', 'N/A')}\n"
        result += f"Statut: {'✅ Actif' if m.get('actif') else '🔴 Inactif'}\n"
        
        return result
    
    except Exception as e:
        return f"❌ Erreur: {str(e)}"


@tool
def list_restaurant_menus(restaurant_id: str, date: Optional[str] = None) -> str:
    """
    Récupère les menus d'un restaurant spécifique.
    
    Args:
        restaurant_id: L'ID du restaurant
        date: Date spécifique YYYY-MM-DD (optionnel)
    
    Returns: Menus du restaurant
    """
    try:
        params = {}
        if date:
            params["date"] = date
        
        response = requests.get(
            f"{BASE_URL}/restaurants/{restaurant_id}/menus",
            params=params,
            timeout=5
        )
        
        if response.status_code != 200:
            return f"❌ Impossible de récupérer les menus du restaurant {restaurant_id}"
        
        data = response.json()
        menus = data.get("data", [])
        
        if not menus:
            return "❌ Aucun menu disponible pour ce restaurant"
        
        result = f"📋 Menus disponibles:\n\n"
        for i, m in enumerate(menus, 1):
            result += f"{i}. {m['typeRepas']}\n"
            result += f"   Prix: {m.get('prix', 'N/A')} DH\n"
            result += f"   ID: {m['_id']}\n\n"
        
        return result
    
    except Exception as e:
        return f"❌ Erreur: {str(e)}"

# ─────────────────────────────────────────────
# 🪑 RÉSERVATIONS
# ─────────────────────────────────────────────

@tool
def make_reservation(menu_id: str, date_repas: str, creneau_horaire: str = "midi", nombre_personnes: int = 1) -> str:
    """
    Crée une nouvelle réservation.
    
    Args:
        menu_id: L'ID du menu à réserver
        date_repas: Date du repas YYYY-MM-DD
        creneau_horaire: Créneau (midi, soir, petit-déjeuner)
        nombre_personnes: Nombre de personnes
    
    Returns: Confirmation de réservation avec ID et QR code
    """
    try:
        token = _get_token()
        if not token:
            return "❌ Erreur authentication"
        
        payload = {
            "menuId": menu_id,
            "dateRepas": date_repas,
            "creneauHoraire": creneau_horaire,
            "nombrePersonnes": nombre_personnes
        }
        
        response = requests.post(
            f"{BASE_URL}/reservations",
            json=payload,
            headers=_headers(),
            timeout=5
        )
        
        if response.status_code != 201:
            data = response.json()
            return f"❌ Erreur réservation: {data.get('message', 'Erreur inconnue')}"
        
        data = response.json()
        reservation = data.get("data", {}).get("reservation", {})
        paiement = data.get("data", {}).get("paiement", {})
        qrcode = data.get("data", {}).get("qrcode", {})
        
        result = "✅ RÉSERVATION CONFIRMÉЕ\n\n"
        result += f"ID Réservation: {reservation.get('_id', 'N/A')}\n"
        result += f"Date: {reservation.get('dateRepas', 'N/A')}\n"
        result += f"Créneau: {reservation.get('creneauHoraire', 'N/A')}\n"
        result += f"Personnes: {reservation.get('nombrePersonnes', 'N/A')}\n"
        result += f"Statut: {reservation.get('statut', 'N/A')}\n\n"
        result += f"💰 Paiement:\n"
        result += f"Montant: {paiement.get('montant', 'N/A')} DH\n"
        result += f"Méthode: {paiement.get('methode', 'N/A')}\n"
        result += f"Statut: {paiement.get('statut', 'N/A')}\n\n"
        result += f"🎫 QR Code ID: {qrcode.get('code', 'N/A')}\n"
        result += f"![QR Code](https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={qrcode.get('code', 'N/A')})\n"
        result += "Utilisez ce QR code pour confirmer votre présence au restaurant."
        
        return result
    
    except Exception as e:
        return f"❌ Erreur: {str(e)}"


@tool
def get_my_reservations(statut: Optional[str] = None) -> str:
    """
    Récupère les réservations de l'utilisateur connecté.
    
    Args:
        statut: Filtrer par statut (confirmée, annulée, expirée, etc.)
    
    Returns: Liste des réservations de l'utilisateur
    """
    try:
        token = _get_token()
        if not token:
            return "❌ Erreur authentication"
        
        params = {}
        if statut:
            params["statut"] = statut
        
        response = requests.get(
            f"{BASE_URL}/reservations/mes-reservations",
            headers=_headers(),
            params=params,
            timeout=5
        )
        
        if response.status_code != 200:
            data = response.json()
            return f"❌ Erreur API: {data.get('message', 'Erreur inconnue')}"
        
        data = response.json()
        reservations = data.get("data", [])
        
        if not reservations:
            return "❌ Aucune réservation trouvée"
        
        result = f"📋 Vos réservations ({len(reservations)}):\n\n"
        for r in reservations:
            menu_info = r.get('menuId', {})
            resto_info = menu_info.get('restaurantId', {})
            
            result += f"🔹 Réservation ID: {r['_id']}\n"
            result += f"   Restaurant: {resto_info.get('nom', 'N/A')}\n"
            result += f"   Repas: {menu_info.get('typeRepas', 'N/A')}\n"
            result += f"   Date: {r.get('dateRepas', 'N/A')}\n"
            result += f"   Créneau: {r.get('creneauHoraire', 'N/A')}\n"
            result += f"   Personnes: {r.get('nombrePersonnes', 1)}\n"
            result += f"   Statut: {r.get('statut', 'N/A')}\n\n"
        
        return result
    
    except Exception as e:
        return f"❌ Erreur: {str(e)}"


@tool
def cancel_reservation(reservation_id: str) -> str:
    """
    Annule une réservation existante.
    
    Args:
        reservation_id: L'ID de la réservation à annuler
    
    Returns: Confirmation d'annulation
    """
    try:
        token = _get_token()
        if not token:
            return "❌ Erreur authentication"
        
        response = requests.patch(
            f"{BASE_URL}/reservations/{reservation_id}/annuler",
            headers=_headers(),
            timeout=5
        )
        
        if response.status_code != 200:
            data = response.json()
            return f"❌ Erreur annulation: {data.get('message', 'Erreur inconnue')}"
        
        data = response.json()
        reservation = data.get("data", {})
        
        result = f"✅ RÉSERVATION ANNULÉE\n\n"
        result += f"ID: {reservation.get('_id', 'N/A')}\n"
        result += f"Nouveau Statut: {reservation.get('statut', 'N/A')}\n"
        result += "Un remboursement sera effectué."
        
        return result
    
    except Exception as e:
        return f"❌ Erreur: {str(e)}"


@tool
def get_reservation_details(reservation_id: str) -> str:
    """
    Récupère les détails complets d'une réservation.
    
    Args:
        reservation_id: L'ID de la réservation
    
    Returns: Détails complets de la réservation
    """
    try:
        token = _get_token()
        if not token:
            return "❌ Erreur authentication"
        
        response = requests.get(
            f"{BASE_URL}/reservations/{reservation_id}",
            headers=_headers(),
            timeout=5
        )
        
        if response.status_code != 200:
            return f"❌ Réservation {reservation_id} introuvable"
        
        data = response.json()
        reservation = data.get("data", {}).get("reservation", {})
        paiement = data.get("data", {}).get("paiement", {})
        qrcode = data.get("data", {}).get("qrcode", {})
        
        result = "🎟️ DÉTAILS RÉSERVATION\n\n"
        result += f"ID: {reservation.get('_id', 'N/A')}\n"
        result += f"Restaurant: {reservation.get('menuId', {}).get('restaurantId', {}).get('nom', 'N/A')}\n"
        result += f"Repas: {reservation.get('menuId', {}).get('typeRepas', 'N/A')}\n"
        result += f"Date: {reservation.get('dateRepas', 'N/A')}\n"
        result += f"Créneau: {reservation.get('creneauHoraire', 'N/A')}\n"
        result += f"Personnes: {reservation.get('nombrePersonnes', 1)}\n"
        result += f"Statut: {reservation.get('statut', 'N/A')}\n"
        result += f"Date Réservation: {reservation.get('dateReservation', 'N/A')}\n\n"
        result += f"💳 Paiement:\n"
        result += f"   Montant: {paiement.get('montant', 'N/A')} DH\n"
        result += f"   Méthode: {paiement.get('methode', 'N/A')}\n"
        result += f"   Statut: {paiement.get('statut', 'N/A')}\n\n"
        result += f"🎫 QR Code: {qrcode.get('code', 'N/A')}\n"
        
        return result
    
    except Exception as e:
        return f"❌ Erreur: {str(e)}"

# ─────────────────────────────────────────────
# 💳 PAIEMENTS
# ─────────────────────────────────────────────

@tool
def get_my_payments() -> str:
    """
    Récupère l'historique des paiements de l'utilisateur.
    
    Returns: Liste des paiements avec montants et statuts
    """
    try:
        token = _get_token()
        if not token:
            return "❌ Erreur authentication"
        
        response = requests.get(
            f"{BASE_URL}/paiements/mes-paiements",
            headers=_headers(),
            timeout=5
        )
        
        if response.status_code != 200:
            data = response.json()
            return f"❌ Erreur API: {data.get('message', 'Erreur inconnue')}"
        
        data = response.json()
        paiements = data.get("data", [])
        
        if not paiements:
            return "❌ Aucun paiement trouvé"
        
        result = f"💳 HISTORIQUE DES PAIEMENTS ({len(paiements)}):\n\n"
        for p in paiements:
            result += f"🔹 ID: {p.get('_id', 'N/A')}\n"
            result += f"   Montant: {p.get('montant', 'N/A')} DH\n"
            result += f"   Méthode: {p.get('methode', 'N/A')}\n"
            result += f"   Statut: {p.get('statut', 'N/A')}\n"
            result += f"   Date: {p.get('datePaiement', 'N/A')}\n\n"
        
        return result
    
    except Exception as e:
        return f"❌ Erreur: {str(e)}"


@tool
def get_payment_receipt(payment_id: str) -> str:
    """
    Récupère le reçu d'un paiement spécifique.
    
    Args:
        payment_id: L'ID du paiement
    
    Returns: Détails du reçu
    """
    try:
        token = _get_token()
        if not token:
            return "❌ Erreur authentication"
        
        response = requests.get(
            f"{BASE_URL}/paiements/{payment_id}/recu",
            headers=_headers(),
            timeout=5
        )
        
        if response.status_code != 200:
            return f"❌ Reçu {payment_id} introuvable"
        
        data = response.json()
        receipt = data.get("data", {})
        
        result = "📄 REÇU DE PAIEMENT\n\n"
        result += f"Numéro: {receipt.get('numero', 'N/A')}\n"
        result += f"Date: {receipt.get('date', 'N/A')}\n"
        result += f"Montant: {receipt.get('montant', 'N/A')} DH\n"
        result += f"Référence Paiement: {receipt.get('referencePaiement', 'N/A')}\n"
        result += f"Détails: {receipt.get('details', 'N/A')}\n"
        
        return result
    
    except Exception as e:
        return f"❌ Erreur: {str(e)}"

# ─────────────────────────────────────────────
# 🔔 NOTIFICATIONS
# ─────────────────────────────────────────────

@tool
def get_my_notifications(unread_only: bool = False) -> str:
    """
    Récupère les notifications de l'utilisateur.
    
    Args:
        unread_only: Si True, ne retourne que les non-lues
    
    Returns: Liste des notifications
    """
    try:
        token = _get_token()
        if not token:
            return "❌ Erreur authentication"
        
        params = {}
        if unread_only:
            params["lue"] = "false"
        
        response = requests.get(
            f"{BASE_URL}/notifications/mes-notifications",
            headers=_headers(),
            params=params,
            timeout=5
        )
        
        if response.status_code != 200:
            data = response.json()
            return f"❌ Erreur API: {data.get('message', 'Erreur inconnue')}"
        
        data = response.json()
        notifications = data.get("data", [])
        
        if not notifications:
            return "❌ Aucune notification"
        
        result = f"🔔 NOTIFICATIONS ({len(notifications)}):\n\n"
        for n in notifications:
            icon = "🔵" if not n.get('lue') else "⚪"
            result += f"{icon} {n.get('titre', 'N/A')}\n"
            result += f"   {n.get('message', 'N/A')}\n"
            result += f"   Date: {n.get('dateCreation', 'N/A')}\n\n"
        
        return result
    
    except Exception as e:
        return f"❌ Erreur: {str(e)}"


@tool
def count_unread_notifications() -> str:
    """
    Compte le nombre de notifications non-lues.
    
    Returns: Nombre de notifications non-lues
    """
    try:
        token = _get_token()
        if not token:
            return "❌ Erreur authentication"
        
        response = requests.get(
            f"{BASE_URL}/notifications/non-lues/count",
            headers=_headers(),
            timeout=5
        )
        
        if response.status_code != 200:
            return "❌ Impossible de compter les notifications"
        
        data = response.json()
        count = data.get("data", {}).get("count", 0)
        
        return f"🔔 Vous avez {count} notification(s) non-lue(s)"
    
    except Exception as e:
        return f"❌ Erreur: {str(e)}"


@tool
def mark_notification_as_read(notification_id: str) -> str:
    """
    Marque une notification comme lue.
    
    Args:
        notification_id: L'ID de la notification
    
    Returns: Confirmation
    """
    try:
        token = _get_token()
        if not token:
            return "❌ Erreur authentication"
        
        response = requests.patch(
            f"{BASE_URL}/notifications/{notification_id}/marquer-lue",
            headers=_headers(),
            timeout=5
        )
        
        if response.status_code != 200:
            return "❌ Impossible de marquer la notification comme lue"
        
        return "✅ Notification marquée comme lue"
    
    except Exception as e:
        return f"❌ Erreur: {str(e)}"


@tool
def mark_all_notifications_as_read() -> str:
    """
    Marque toutes les notifications comme lues.
    
    Returns: Confirmation
    """
    try:
        token = _get_token()
        if not token:
            return "❌ Erreur authentication"
        
        response = requests.patch(
            f"{BASE_URL}/notifications/marquer-tout-lue",
            headers=_headers(),
            timeout=5
        )
        
        if response.status_code != 200:
            return "❌ Impossible de marquer les notifications comme lues"
        
        data = response.json()
        count = data.get("data", {}).get("modifiees", 0)
        
        return f"✅ {count} notification(s) marquée(s) comme lue(s)"
    
    except Exception as e:
        return f"❌ Erreur: {str(e)}"

# ─────────────────────────────────────────────
# 👤 PROFIL
# ─────────────────────────────────────────────

@tool
def get_profile() -> str:
    """
    Récupère le profil de l'utilisateur connecté.
    
    Returns: Informations du profil
    """
    try:
        token = _get_token()
        if not token:
            return "❌ Erreur authentication"
        
        response = requests.get(
            f"{BASE_URL}/utilisateurs/profil",
            headers=_headers(),
            timeout=5
        )
        
        if response.status_code != 200:
            return "❌ Impossible de récupérer le profil"
        
        data = response.json()
        user = data.get("data", {})
        
        result = "👤 MON PROFIL\n\n"
        result += f"Nom: {user.get('nom', 'N/A')}\n"
        result += f"Prénom: {user.get('prenom', 'N/A')}\n"
        result += f"Email: {user.get('email', 'N/A')}\n"
        result += f"Téléphone: {user.get('telephone', 'N/A')}\n"
        result += f"Rôle: {user.get('role', 'N/A')}\n"
        result += f"Boursier: {'Oui ✓' if user.get('boursier') else 'Non ✗'}\n"
        result += f"Numéro Étudiant: {user.get('numeroEtudiant', 'N/A')}\n"
        result += f"Date Inscription: {user.get('dateInscription', 'N/A')}\n"
        
        return result
    
    except Exception as e:
        return f"❌ Erreur: {str(e)}"


@tool
def update_profile(telephone: Optional[str] = None, adresse: Optional[str] = None) -> str:
    """
    Met à jour le profil de l'utilisateur.
    
    Args:
        telephone: Nouveau numéro de téléphone
        adresse: Nouvelle adresse
    
    Returns: Profil mis à jour
    """
    try:
        token = _get_token()
        if not token:
            return "❌ Erreur authentication"
        
        payload = {}
        if telephone:
            payload["telephone"] = telephone
        if adresse:
            payload["adresse"] = adresse
        
        if not payload:
            return "❌ Aucun champ à mettre à jour"
        
        response = requests.put(
            f"{BASE_URL}/utilisateurs/mon-profil",
            json=payload,
            headers=_headers(),
            timeout=5
        )
        
        if response.status_code != 200:
            data = response.json()
            return f"❌ Erreur modification: {data.get('message', 'Erreur inconnue')}"
        
        data = response.json()
        user = data.get("data", {})
        
        result = "✅ PROFIL MIS À JOUR\n\n"
        result += f"Téléphone: {user.get('telephone', 'N/A')}\n"
        result += f"Adresse: {user.get('adresse', 'N/A')}\n"
        
        return result
    
    except Exception as e:
        return f"❌ Erreur: {str(e)}"

# ─────────────────────────────────────────────
# 🎫 QR CODES
# ─────────────────────────────────────────────

@tool
def get_qrcode_by_reservation(reservation_id: str) -> str:
    """
    Récupère le QR code d'une réservation.
    
    Args:
        reservation_id: L'ID de la réservation
    
    Returns: Informations du QR code
    """
    try:
        token = _get_token()
        if not token:
            return "❌ Erreur authentication"
        
        response = requests.get(
            f"{BASE_URL}/qrcodes/reservation/{reservation_id}",
            headers=_headers(),
            timeout=5
        )
        
        if response.status_code != 200:
            return f"❌ QR code pour la réservation {reservation_id} introuvable"
        
        data = response.json()
        qrcode = data.get("data", {})
        
        result = "🎫 QR CODE\n\n"
        result += f"Code: {qrcode.get('code', 'N/A')}\n"
        result += f"Réservation: {qrcode.get('reservationId', 'N/A')}\n"
        result += f"Statut: {qrcode.get('statut', 'N/A')}\n"
        result += f"Date Création: {qrcode.get('dateCreation', 'N/A')}\n"
        result += f"Scannage: {'Oui ✓' if qrcode.get('scanne') else 'Non ✗'}\n"
        
        return result
    
    except Exception as e:
        return f"❌ Erreur: {str(e)}"


@tool
def validate_qrcode(qrcode: str) -> str:
    """
    Valide un QR code.
    
    Args:
        qrcode: Le code QR à valider
    
    Returns: Résultat de la validation
    """
    try:
        token = _get_token()
        if not token:
            return "❌ Erreur authentication"
        
        response = requests.get(
            f"{BASE_URL}/qrcodes/valider/{qrcode}",
            headers=_headers(),
            timeout=5
        )
        
        if response.status_code != 200:
            data = response.json()
            return f"❌ QR Code invalide: {data.get('message', 'Erreur inconnue')}"
        
        data = response.json()
        result = data.get("data", {})
        
        validation_result = "✅ QR CODE VALIDE\n\n"
        validation_result += f"Code: {result.get('code', 'N/A')}\n"
        validation_result += f"Réservation: {result.get('reservationId', 'N/A')}\n"
        validation_result += f"Statut: {result.get('statut', 'N/A')}\n"
        
        return validation_result
    
    except Exception as e:
        return f"❌ Erreur: {str(e)}"


@tool
def scan_qrcode(qrcode: str) -> str:
    """
    Scanne (marque comme utilisé) un QR code.
    Administrateur seulement.
    
    Args:
        qrcode: Le code QR à scanner
    
    Returns: Résultat du scan
    """
    try:
        token = _get_token()
        if not token:
            return "❌ Erreur authentication"
        
        response = requests.patch(
            f"{BASE_URL}/qrcodes/scanner/{qrcode}",
            headers=_headers(),
            timeout=5
        )
        
        if response.status_code != 200:
            data = response.json()
            return f"❌ Impossible de scanner: {data.get('message', 'Erreur inconnue')}"
        
        data = response.json()
        result = data.get("data", {})
        
        scan_result = "✅ QR CODE SCANNÉ\n\n"
        scan_result += f"Code: {result.get('code', 'N/A')}\n"
        scan_result += f"Réservation: {result.get('reservationId', 'N/A')}\n"
        scan_result += f"Date Scan: {result.get('dateScannage', 'N/A')}\n"
        scan_result += f"Statut: {result.get('statut', 'N/A')}\n"
        
        return scan_result
    
    except Exception as e:
        return f"❌ Erreur: {str(e)}"



# ─────────────────────────────────────────────
# 📅 UTILITAIRES
# ─────────────────────────────────────────────

@tool
def get_today_date() -> str:
    """
    Retourne la date et l'heure actuelles.
    Utilise cet outil quand l'utilisateur mentionne 'aujourd'hui', 'demain', 'cette semaine', etc.
    
    Returns: Date et heure actuelles formatées
    """
    now = datetime.now()
    jours = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
    mois = ['janvier', 'février', 'mars', 'avril', 'mai', 'juin',
            'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre']
    
    jour_nom = jours[now.weekday()]
    mois_nom = mois[now.month - 1]
    
    demain = now + timedelta(days=1)
    
    return (
        f"📅 Date actuelle: {jour_nom} {now.day} {mois_nom} {now.year}\n"
        f"🕐 Heure: {now.strftime('%H:%M')}\n"
        f"📆 Aujourd'hui (YYYY-MM-DD): {now.strftime('%Y-%m-%d')}\n"
        f"📆 Demain (YYYY-MM-DD): {demain.strftime('%Y-%m-%d')}"
    )


# ─────────────────────────────────────────────
# 🏪 GESTION DES RESTAURANTS (Admin)
# ─────────────────────────────────────────────

@tool
def create_restaurant(nom: str, adresse: str, capacite: int, horaires_ouverture: str) -> str:
    """
    Crée un nouveau restaurant (Admin et Admin Pro uniquement).
    
    Args:
        nom: Nom du restaurant
        adresse: Adresse complète du restaurant
        capacite: Nombre de places disponibles
        horaires_ouverture: Horaires d'ouverture (ex: "8h-22h")
    
    Returns: Confirmation de création du restaurant
    """
    try:
        token = _get_token()
        if not token:
            return "❌ Erreur authentication"
        
        payload = {
            "nom": nom,
            "adresse": adresse,
            "capacite": capacite,
            "horairesOuverture": horaires_ouverture
        }
        
        response = requests.post(
            f"{BASE_URL}/restaurants",
            json=payload,
            headers=_headers(),
            timeout=5
        )
        
        if response.status_code != 201:
            data = response.json()
            return f"❌ Erreur création restaurant: {data.get('message', 'Erreur inconnue')}"
        
        data = response.json()
        restaurant = data.get("data", {})
        
        result = "✅ RESTAURANT CRÉÉ\n\n"
        result += f"Nom: {restaurant.get('nom', 'N/A')}\n"
        result += f"Adresse: {restaurant.get('adresse', 'N/A')}\n"
        result += f"Capacité: {restaurant.get('capacite', 'N/A')} places\n"
        result += f"Horaires: {restaurant.get('horairesOuverture', 'N/A')}\n"
        result += f"ID: {restaurant.get('_id', 'N/A')}\n"
        result += f"Statut: {'✅ OUVERT' if restaurant.get('estOuvert') else '🔴 FERMÉ'}\n"
        
        return result
    
    except Exception as e:
        return f"❌ Erreur: {str(e)}"


@tool
def get_my_restaurant() -> str:
    """
    Récupère les informations du restaurant géré par l'Admin Pro.
    
    Returns: Détails du restaurant géré
    """
    try:
        token = _get_token()
        if not token:
            return "❌ Erreur authentication"
        
        response = requests.get(
            f"{BASE_URL}/admin-pro/restaurant",
            headers=_headers(),
            timeout=5
        )
        
        if response.status_code != 200:
            data = response.json()
            return f"❌ Erreur: {data.get('message', 'Erreur inconnue')}"
        
        data = response.json()
        restaurant = data.get("data", {})
        
        if not restaurant:
            return "❌ Aucun restaurant géré trouvé"
        
        result = "🏪 MON RESTAURANT\n\n"
        result += f"Nom: {restaurant.get('nom', 'N/A')}\n"
        result += f"Adresse: {restaurant.get('adresse', 'N/A')}\n"
        result += f"Capacité: {restaurant.get('capacite', 'N/A')} places\n"
        result += f"Horaires: {restaurant.get('horairesOuverture', 'N/A')}\n"
        result += f"Statut: {'✅ OUVERT' if restaurant.get('estOuvert') else '🔴 FERMÉ'}\n"
        result += f"ID: {restaurant.get('_id', 'N/A')}\n"
        
        return result
    
    except Exception as e:
        return f"❌ Erreur: {str(e)}"


# ─────────────────────────────────────────────
# 👥 GESTION DES UTILISATEURS
# ─────────────────────────────────────────────

@tool
def register_citoyen(nom: str, prenom: str, email: str, mot_de_passe: str, 
                     telephone: str, cni: str, profession: str, 
                     date_naissance: str, adresse_complete: str) -> str:
    """
    Inscrit un nouveau citoyen (sans réduction).
    
    Args:
        nom: Nom de famille
        prenom: Prénom
        email: Adresse email
        mot_de_passe: Mot de passe (min 4 caractères)
        telephone: Numéro de téléphone (format: 0XXXXXXXXX)
        cni: Numéro CNI
        profession: Profession
        date_naissance: Date de naissance (YYYY-MM-DD)
        adresse_complete: Adresse complète
    
    Returns: Confirmation d'inscription
    """
    try:
        payload = {
            "nom": nom,
            "prenom": prenom,
            "email": email,
            "motDePasse": mot_de_passe,
            "telephone": telephone,
            "role": "citoyen",
            "cni": cni,
            "profession": profession,
            "dateNaissance": date_naissance,
            "adresseComplete": adresse_complete
        }
        
        response = requests.post(
            f"{BASE_URL}/auth/inscription",
            json=payload,
            timeout=5
        )
        
        if response.status_code != 201:
            data = response.json()
            return f"❌ Erreur inscription citoyen: {data.get('message', 'Erreur inconnue')}"
        
        data = response.json()
        utilisateur = data.get("data", {})
        
        result = "✅ CITOYEN INSCRIT\n\n"
        result += f"Nom: {utilisateur.get('nom', 'N/A')} {utilisateur.get('prenom', 'N/A')}\n"
        result += f"Email: {utilisateur.get('email', 'N/A')}\n"
        result += f"Téléphone: {utilisateur.get('telephone', 'N/A')}\n"
        result += f"Rôle: {utilisateur.get('role', 'N/A')}\n"
        result += f"Réduction: 0% (tarif plein)\n"
        result += "\n🎉 Bienvenue! Vous pouvez maintenant réserver des repas."
        
        return result
    
    except Exception as e:
        return f"❌ Erreur: {str(e)}"


@tool
def calculate_price_reduction(prix_original: float) -> str:
    """
    Calcule le prix avec réduction selon le type d'utilisateur.
    
    Args:
        prix_original: Prix original du menu
    
    Returns: Prix final avec réduction appliquée
    """
    try:
        token = _get_token()
        if not token:
            return "❌ Erreur authentication"
        
        payload = {"prixOriginal": prix_original}
        
        response = requests.post(
            f"{BASE_URL}/citoyens/calculer-prix",
            json=payload,
            headers=_headers(),
            timeout=5
        )
        
        if response.status_code == 200:
            # Citoyen
            data = response.json()
            prix_data = data.get("data", {})
            
            result = "💰 CALCUL DU PRIX\n\n"
            result += f"Prix original: {prix_original} DH\n"
            result += f"Réduction: {prix_data.get('reduction', 0)} DH\n"
            result += f"Prix final: {prix_data.get('prixFinal', prix_original)} DH\n"
            result += f"Statut: {prix_data.get('eligibilite', {}).get('raison', 'N/A')}\n"
            
            return result
        else:
            # Vérifier si c'est un étudiant
            response = requests.get(
                f"{BASE_URL}/utilisateurs/profil",
                headers=_headers(),
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                user = data.get("data", {})
                
                if user.get("role") == "etudiant":
                    # Calcul manuel pour étudiant (50% de réduction)
                    reduction = prix_original * 0.5
                    prixFinal = prix_original - reduction
                    
                    result = "💰 CALCUL DU PRIX\n\n"
                    result += f"Prix original: {prix_original} DH\n"
                    result += f"Réduction étudiante: 50%\n"
                    result += f"Montant réduit: {reduction} DH\n"
                    result += f"Prix final: {prixFinal} DH\n"
                    result += f"Économie: {reduction} DH\n"
                    result += "Statut: Réduction automatique pour les étudiants\n"
                    
                    return result
            
            return f"❌ Impossible de calculer la réduction"
    
    except Exception as e:
        return f"❌ Erreur: {str(e)}"


# ─────────────────────────────────────────────
# 📊 STATISTIQUES ADMIN PRO
# ─────────────────────────────────────────────

@tool
def get_restaurant_statistics() -> str:
    """
    Récupère les statistiques du restaurant (Admin Pro uniquement).
    
    Returns: Statistiques détaillées du restaurant
    """
    try:
        token = _get_token()
        if not token:
            return "❌ Erreur authentication"
        
        response = requests.get(
            f"{BASE_URL}/admin-pro/statistiques",
            headers=_headers(),
            timeout=5
        )
        
        if response.status_code != 200:
            data = response.json()
            return f"❌ Erreur: {data.get('message', 'Permission refusée ou erreur inconnue')}"
        
        data = response.json()
        stats = data.get("data", {})
        
        result = "📊 STATISTIQUES DU RESTAURANT\n\n"
        
        # Réservations du mois
        totalReservations = stats.get("totalReservations", 0)
        result += f"📝 Réservations ce mois: {totalReservations}\n"
        
        # Revenus mensuels
        revenus = stats.get("revenusMensuels", [])
        if revenus and len(revenus) > 0:
            totalRevenus = revenus[0].get("total", 0)
            result += f"💰 Revenus ce mois: {totalRevenus} DH\n"
        else:
            result += "💰 Revenus ce mois: 0 DH\n"
        
        # Menus actifs
        menusActifs = stats.get("menusActifs", 0)
        result += f"🍽️ Menus actifs: {menusActifs}\n"
        
        result += "\n📈 Ces statistiques couvrent les 30 derniers jours."
        
        return result
    
    except Exception as e:
        return f"❌ Erreur: {str(e)}"


# ─────────────────────────────────────────────
# 🔒 OUTILS ADMIN SÉCURISÉS
# ─────────────────────────────────────────────

@tool
def get_resto_stats() -> str:
    """
    Récupère les statistiques (réservations, revenus, fréquentation).
    Réservé aux administrateurs (admin ou admin_pro).
    
    Returns: Statistiques détaillées
    """
    try:
        role = user_role_var.get()
        if role not in ('admin', 'admin_pro'):
            return "🚫 Accès refusé. Cet outil est réservé aux administrateurs."
        
        token = _get_token()
        if not token:
            return "❌ Erreur authentication"
        
        response = requests.get(
            f"{BASE_URL}/admin/stats",
            headers=_headers(),
            timeout=10
        )
        
        if response.status_code != 200:
            data = response.json()
            return f"❌ Erreur: {data.get('message', 'Permission refusée')}"
        
        data = response.json()
        s = data.get("data", {})
        stats = s.get("stats", {})
        
        result = "📊 STATISTIQUES ADMIN\n\n"
        result += f"📝 Total réservations: {stats.get('totalReservations', 0)}\n"
        result += f"👥 Total personnes: {stats.get('totalPersonnes', 0)}\n"
        result += f"✅ Confirmées: {stats.get('confirmées', 0)}\n"
        result += f"❌ Annulées: {stats.get('annulées', 0)}\n"
        result += f"💰 Revenus: {s.get('revenus', 0)} DH\n"
        result += f"🏪 Périmètre: {s.get('restaurantId', 'Tous')}\n"
        
        return result
    except Exception as e:
        return f"❌ Erreur: {str(e)}"


@tool
def list_registered_users() -> str:
    """
    Liste les utilisateurs inscrits.
    Réservé aux administrateurs (admin ou admin_pro).
    
    Returns: Liste des utilisateurs
    """
    try:
        role = user_role_var.get()
        if role not in ('admin', 'admin_pro'):
            return "🚫 Accès refusé. Cet outil est réservé aux administrateurs."
        
        token = _get_token()
        if not token:
            return "❌ Erreur authentication"
        
        response = requests.get(
            f"{BASE_URL}/admin/utilisateurs",
            headers=_headers(),
            timeout=10
        )
        
        if response.status_code != 200:
            data = response.json()
            return f"❌ Erreur: {data.get('message', 'Permission refusée')}"
        
        data = response.json()
        users = data.get("data", [])
        
        if not users:
            return "Aucun utilisateur inscrit."
        
        result = f"👥 UTILISATEURS INSCRITS ({data.get('count', len(users))}):\n\n"
        for u in users:
            role_icon = {'etudiant': '🎓', 'citoyen': '🏛️', 'admin': '🔑', 'admin_pro': '⭐'}.get(u.get('role'), '👤')
            result += f"{role_icon} {u.get('prenom', '')} {u.get('nom', '')}\n"
            result += f"   Email: {u.get('email', 'N/A')}\n"
            result += f"   Rôle: {u.get('role', 'N/A')}\n\n"
        
        return result
    except Exception as e:
        return f"❌ Erreur: {str(e)}"


@tool
def remove_user_from_resto(user_id: str) -> str:
    """
    Retire un utilisateur d'un restaurant (annule ses réservations futures).
    Réservé aux administrateurs (admin ou admin_pro).
    
    Args:
        user_id: L'ID de l'utilisateur à retirer
    
    Returns: Confirmation du retrait
    """
    try:
        role = user_role_var.get()
        if role not in ('admin', 'admin_pro'):
            return "🚫 Accès refusé. Cet outil est réservé aux administrateurs."
        
        token = _get_token()
        if not token:
            return "❌ Erreur authentication"
        
        response = requests.delete(
            f"{BASE_URL}/admin/utilisateurs/{user_id}/retirer",
            headers=_headers(),
            timeout=10
        )
        
        if response.status_code != 200:
            data = response.json()
            return f"❌ Erreur: {data.get('message', 'Permission refusée')}"
        
        data = response.json()
        count = data.get("modifiedCount", 0)
        
        return f"✅ Utilisateur retiré. {count} réservation(s) future(s) annulée(s)."
    except Exception as e:
        return f"❌ Erreur: {str(e)}"


# ─────────────────────────────────────────────
# 🔍 RAG (documents PDF) — optionnel
# ─────────────────────────────────────────────

try:
    from retriever import get_retriever
    _retriever = get_retriever()
    
    @tool
    def search_documents(question: str) -> str:
        """
        Recherche des informations dans les documents PDF du restaurant.
        
        Args:
            question: La question à rechercher dans les documents
        
        Returns: Informations trouvées dans les documents
        """
        try:
            docs = _retriever.invoke(question)
            if not docs:
                return "❌ Aucune information trouvée dans les documents."
            return "📄 Résultats de recherche:\n\n" + "\n\n".join([doc.page_content for doc in docs])
        except Exception as e:
            return f"❌ Erreur recherche documents: {str(e)}"
    
    print("RAG documents PDF active")
except Exception as e:
    print(f"RAG documents non disponible: {e}")
    search_documents = None