# CONTENU À AJOUTER AU DOCUMENT TECHNIQUE
# Projet RESTO_BM - Rapport de Fin d'Année

---

## 11. Bot Conversationnel Intelligent

### 11.1 Vue d'ensemble

Le bot conversationnel RESTO_BM est un assistant IA intelligent basé sur LangChain et LangGraph qui permet aux utilisateurs d'interagir avec le système en langage naturel. Il s'intègre comme une couche intermédiaire entre le frontend React et le backend Node.js, offrant une expérience conversationnelle intuitive pour toutes les fonctionnalités métier.

**Objectifs principaux :**
- Permettre aux utilisateurs d'interagir en langage naturel avec le système
- Automatiser les tâches courantes (réservation, consultation, annulation)
- Fournir des réponses contextuelles basées sur le rôle de l'utilisateur
- Offrir une recherche documentaire intelligente via RAG

---

### 11.2 Architecture Technique

Le bot conversationnel repose sur une architecture en couches :

**Couche Présentation (Frontend React)**
- Interface utilisateur textuelle intégrée dans l'application React existante
- Communication avec l'API du bot via protocole HTTP standard
- Gestion de l'état de connexion et de l'historique de conversation

**Couche API (Flask)**
- Service API RESTful indépendant
- Extraction automatique du rôle utilisateur depuis le JWT
- Cache des instances d'agents par rôle pour optimiser les performances
- Gestion des sessions de conversation avec identifiants uniques

**Couche Intelligence Artificielle (LangChain/LangGraph)**
- Agent conversationnel basé sur LangChain avec LangGraph pour la gestion de la mémoire
- Intégration du modèle GPT-4o-mini via OpenRouter pour la génération de réponses
- Sélection automatique des outils appropriés selon la requête utilisateur
- Prompts système personnalisés selon le rôle de l'utilisateur

**Couche Intégration (Tools)**
- 20+ outils LangChain encapsulant les appels à l'API backend existante
- Authentification automatique via token JWT pour chaque outil
- Gestion centralisée des erreurs et formatage uniforme des réponses

---

### 11.3 Stack Technologique

| Composant | Technologie | Description |
|-----------|-------------|-------------|
| Runtime | Python 3.8+ | Langage principal |
| API Web | Flask | Framework REST |
| Framework IA | LangChain | Orchestration agent |
| Framework IA | LangGraph | Gestion mémoire |
| LLM | GPT-4o-mini (OpenRouter) | Modèle de langage |
| Vector DB | ChromaDB | Stockage embeddings |
| Embeddings | HuggingFace | Modèle embeddings |
| Authentification | PyJWT | Validation JWT |

---

### 11.4 Outils LangChain Intégrés

Le bot dispose de **20+ outils** organisés par catégorie :

**Restaurants (2 outils)** : Liste des restaurants et détails complets

**Menus (3 outils)** : Liste des menus avec filtres et détails des plats

**Réservations (4 outils)** : Création, consultation, annulation et détails de réservations

**Paiements (2 outils)** : Historique et reçus de paiements

**Notifications (4 outils)** : Liste, comptage et marquage des notifications

**Profil (2 outils)** : Affichage et mise à jour du profil utilisateur

**QR Codes (3 outils)** : Génération, validation et scan des QR codes

**Administration (3 outils)** : Statistiques, gestion utilisateurs (admin uniquement)

**Recherche Documentaire (1 outil)** : Recherche dans les documents PDF (RAG)

---

### 11.5 Gestion Multi-Rôles

Le bot adapte ses réponses et ses outils en fonction du rôle de l'utilisateur :

| Rôle | Accès | Réduction | Visibilité |
|------|-------|-----------|------------|
| **étudiant** | Complet | 50% automatique | Ses propres données |
| **citoyen** | Complet | Aucune (100%) | Ses propres données |
| **admin_pro** | Complet + Admin | Aucune | SON restaurant uniquement |
| **admin** | Complet + Admin | Aucune | GLOBALE (tous restaurants) |

Le système extrait automatiquement le rôle depuis le token JWT et maintient un cache d'agents pré-initialisés par rôle pour optimiser les performances. Chaque rôle possède un prompt système personnalisé.

---

### 11.6 Système RAG (Retrieval-Augmented Generation)

Le système RAG permet au bot de répondre à des questions en se basant sur des documents PDF. Le processus fonctionne selon les étapes suivantes :

1. **Chargement des documents** : Les fichiers PDF sont chargés
2. **Découpage en chunks** : Chaque document est divisé en segments
3. **Génération d'embeddings** : Chaque chunk est converti en vecteur sémantique
4. **Stockage vectoriel** : Les embeddings sont stockés dans ChromaDB
5. **Récupération** : Lors d'une question, le système récupère les documents les plus pertinents
6. **Génération** : L'agent utilise ces documents pour générer une réponse informée

---

### 11.7 Mémoire de Conversation

Le bot utilise le système de mémoire de LangGraph pour maintenir le contexte de conversation. Chaque conversation est identifiée par un identifiant unique, permettant :
- Maintenir l'historique par session utilisateur
- Revenir sur des conversations précédentes
- Contextualiser les réponses basées sur l'historique
- Supporter plusieurs utilisateurs simultanément sans interférence

---

### 11.8 Intégration Frontend

Le composant React intégré dans l'application fournit une interface utilisateur moderne et responsive avec les fonctionnalités suivantes :
- Zone de texte pour la saisie des messages
- Affichage de l'historique de conversation
- Vérification automatique du statut de connexion
- Gestion des erreurs réseau
- Bouton d'effacement de l'historique

Le bot est accessible via un onglet dédié dans la barre de navigation de l'application React.

---

### 11.9 Exemples d'Utilisation

**Restaurants** : L'utilisateur peut demander "quels sont les restaurants ouverts?" et le bot répond avec une liste structurée incluant le nom, le statut, l'adresse et les horaires.

**Réservation** : L'utilisateur peut demander "réserve moi un menu pizza pour demain midi" et le bot crée automatiquement la réservation, calcule le prix (avec réduction si applicable), génère le paiement et le QR code.

**Profil** : L'utilisateur peut demander "mon profil" et le bot affiche toutes ses informations personnelles.

**Notifications** : L'utilisateur peut demander "mes notifications" et le bot liste toutes les notifications avec leur statut.

---

### 11.10 Sécurité

**Validation JWT** : Le bot valide systématiquement le token JWT pour chaque requête, empêchant l'accès non autorisé aux fonctionnalités protégées.

**Filtrage des Outils par Rôle** : Les outils d'administration ne sont accessibles qu'aux rôles autorisés (admin et admin_pro). Ce filtrage est appliqué au niveau de l'instanciation de l'agent.

**Variables d'Environnement** : Les clés API sensibles sont stockées dans un fichier `.env` non versionné pour éviter leur divulgation.

---

### 11.11 Conclusion

Le bot conversationnel RESTO_BM représente une avancée significative dans l'expérience utilisateur du système de restauration universitaire. En combinant LangChain, LangGraph et une architecture multi-rôles sophistiquée, il offre une interface naturelle et intuitive pour accéder à toutes les fonctionnalités du système.

**Points forts :**
- Interface conversationnelle naturelle
- Adaptation automatique au rôle de l'utilisateur
- Intégration transparente avec l'API existante
- Système RAG pour des réponses basées sur des documents
- Mémoire de conversation pour un contexte continu

Cette démonstration de l'utilisation de l'IA conversationnelle dans un contexte métier réel constitue une réalisation technique majeure pour ce projet de fin d'année.

---

**Date de création** : 9 mai 2026  
**Projet** : RESTO_BM - Projet de Fin d'Année  
**Version** : 1.0
