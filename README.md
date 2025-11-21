# Bot de Révision Wild Code School

> Système automatisé de génération de tests de révision personnalisés à partir des cours Wild Code School, avec envoi automatique sur Discord via l'API gratuite Groq (Llama 3.3 70B).

---

## Table des matières

1. [Vue d'ensemble](#vue-densemble)
2. [Prérequis](#prérequis)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Utilisation](#utilisation)
6. [Architecture et fonctionnement](#architecture-et-fonctionnement)
7. [Dépannage](#dépannage)
8. [FAQ](#faq)
9. [Contribution](#contribution)
10. [Licence](#licence)

---

## Vue d'ensemble

Ce bot automatise le processus de révision des cours Wild Code School en :

1. Se connectant automatiquement à la plateforme Odyssey
2. Récupérant le contenu des cours planifiés (textes, images, ressources Google Drive/Colab)
3. Générant un test de révision unique et personnalisé via l'IA Llama 3.3 70B (Groq)
4. Envoyant le test formaté sur Discord via webhook

**Exemple concret** : Pour 4 cours planifiés (Python, Pandas, Matplotlib, Git), le système génère un test unique de 15-20 minutes contenant 2-3 questions par cours, intelligemment mélangées pour favoriser la compréhension transversale.

---

## Prérequis

### Système

- Python 3.8 ou supérieur
- Système d'exploitation : Windows, macOS ou Linux
- Connexion Internet stable

### Comptes requis

- **Wild Code School** : Compte actif avec accès à Odyssey
- **Groq** : Compte gratuit pour accéder à l'API Llama 3.3 ([console.groq.com](https://console.groq.com))
- **Discord** : Serveur avec permissions de création de webhooks

### Fichiers nécessaires

- **Planning Excel** : `Revision_WCS.xlsx` contenant les colonnes :
  - `cours` : Nom du cours
  - `url_wcs` : URL du cours sur Odyssey
  - `YYYY-MM-DD` : Colonnes de dates avec marqueurs pour les cours à réviser

---

## Installation

### 1. Cloner le dépôt

```bash
git clone https://github.com/VOTRE_USERNAME/wcs-revision-bot.git
cd wcs-revision-bot
```

### 2. Créer un environnement virtuel

**Windows** :
```bash
python -m venv .venv
.venv\Scripts\activate
```

**macOS/Linux** :
```bash
python3 -m venv .venv
source .venv/bin/activate
```

L'activation est confirmée par l'affichage de `(.venv)` au début de la ligne de commande.

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
playwright install chromium
```

**Note** : L'installation peut prendre 5-10 minutes lors de la première exécution.

---

## Configuration

### 1. Création du fichier d'environnement

```bash
cp .env.example .env
```

### 2. Configuration de la clé API Groq

**Obtention de la clé** :
1. Créer un compte sur [console.groq.com](https://console.groq.com)
2. Naviguer vers "API Keys"
3. Générer une nouvelle clé (format : `gsk_...`)
4. Copier la clé dans le fichier `.env` :

```env
GROQ_API_KEY=gsk_votre_cle_secrete_ici
```

**Important** : Ne jamais partager cette clé ni la versionner sur Git (`.gitignore` est préconfiguré).

### 3. Configuration du webhook Discord

**Création du webhook** :
1. Ouvrir Discord et sélectionner le serveur cible (si vous n'en n'êtes pas administrateur, créez le votre)
2. Choisir le canal destiné aux tests de révision
3. Paramètres du canal → Intégrations → Webhooks
4. Créer un webhook et copier l'URL générée
5. Ajouter l'URL dans le fichier `.env` :

```env
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/VOTRE_WEBHOOK_ID/VOTRE_TOKEN
```

### 4. Identifiants Wild Code School

```env
WCS_EMAIL=votre.email@example.com
WCS_PASSWORD=votre_mot_de_passe
```

**Sécurité** : Le fichier `.env` contient des informations sensibles. Ne jamais le partager ni le versionner.

### 5. Préparation du planning Excel

Le fichier `Revision_WCS.xlsx` à la racine du projet doit avoir la structure suivante :

| cours | url_wcs | 2025-11-21 | 2025-11-22 |
|-------|---------|-----------|-----------|
| Python Basics | https://odyssey.wildcodeschool.com/courses/123 | X | |
| Pandas Introduction | https://odyssey.wildcodeschool.com/courses/456 | X | X |

- Colonnes de dates au format ISO (YYYY-MM-DD)
- Marqueur (`X`, `✓`, `1`, etc.) pour indiquer les cours à réviser

Si vous voulez effacer le contenu du tableau pour le remplir à votre maniere, alors : Pour les dates effacez SEULEMENT les date de la colonne date : ca va supprimer le reste sans toucher aux formules.

---

## Utilisation

### Exécution standard

1. Activer l'environnement virtuel (si non actif) :
   ```bash
   # Windows
   .venv\Scripts\activate
   
   # macOS/Linux
   source .venv/bin/activate
   ```

2. Lancer le bot :
   ```bash
   python main.py
   ```

### Exemple de sortie

```
2025-11-21 12:03:22 [INFO] Démarrage du script de révision WCS.
2025-11-21 12:03:22 [INFO] 4 cours à réviser aujourd'hui.
Connexion à https://odyssey.wildcodeschool.com/users/sign_in...
Login réussi.
Traitement : Python Basics
Traitement : Pandas Introduction
Traitement : Matplotlib Introduction
Traitement : Git Fundamentals
2025-11-21 12:03:40 [INFO] Génération d'UN SEUL test combiné pour 4 cours
🚀 Lancement de llama-3.3-70b-versatile sur Groq...
2025-11-21 12:03:46 [INFO] Envoi du test combiné sur Discord
2025-11-21 12:03:50 [INFO] Test combiné généré et envoyé avec succès !
```

Le test sera disponible dans le canal Discord configuré.

---

## Architecture et fonctionnement

### Flux de données

```
┌─────────────────────────────────────────────────────┐
│  1. LANCEMENT DU BOT                                │
│     python main.py                                  │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│  2. ANALYSE DU PLANNING                             │
│     • Lecture de Revision_WCS.xlsx                  │
│     • Extraction des cours pour la date courante    │
│     • Validation des URLs                           │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│  3. SCRAPING AUTOMATISÉ                             │
│     • Initialisation de Playwright (Chromium)       │
│     • Authentification sur Odyssey                  │
│     • Navigation vers chaque cours                  │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│  4. EXTRACTION DU CONTENU                           │
│     • Texte des cours (HTML → Markdown)             │
│     • Images et ressources visuelles                │
│     • Liens Google Drive/Colab                     │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│  5. GÉNÉRATION IA (Groq/Llama 3.3)                  │
│     • Agrégation du contenu de tous les cours       │
│     • Requête API Groq avec prompt optimisé         │
│     • Génération d'un test unique et cohérent       │
│     • Format Markdown, sans corrigé                 │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│  6. DISTRIBUTION DISCORD                            │
│     • Découpage intelligent (<2000 caractères)     │
│     • Préservation du formatage Markdown            │
│     • Envoi via webhook                             │
└─────────────────────────────────────────────────────┘
```

### Composants principaux

- **`main.py`** : Orchestrateur principal du workflow
- **`wcs_scraper.py`** : Module de scraping Playwright
- **`test_generator.py`** : Interface avec l'API Groq et gestion des prompts
- **`discord_client.py`** : Gestion de l'envoi Discord avec découpage automatique

---

## Dépannage

### Erreur : `GROQ_API_KEY manquante`

**Cause** : Fichier `.env` absent ou mal configuré

**Solution** :
1. Vérifier l'existence du fichier `.env` (distincte de `.env.example`)
2. Confirmer la présence de la ligne `GROQ_API_KEY=gsk_...`
3. Vérifier l'absence d'espaces avant/après le signe `=`

### Erreur : `DISCORD_WEBHOOK_URL est introuvable`

**Cause** : URL du webhook non configurée

**Solution** :
1. Vérifier la ligne `DISCORD_WEBHOOK_URL=...` dans `.env`
2. Confirmer que l'URL commence par `https://discord.com/api/webhooks/`
3. Tester manuellement le webhook :
   ```bash
   curl -X POST -H "Content-Type: application/json" \
   -d '{"content":"Test de connexion"}' \
   VOTRE_URL_WEBHOOK
   ```

### Erreur : `Login échoué` ou erreurs d'authentification

**Cause** : Identifiants WCS incorrects ou expirés

**Solution** :
1. Vérifier `WCS_EMAIL` et `WCS_PASSWORD` dans `.env`
2. Tester la connexion manuelle sur [Odyssey](https://odyssey.wildcodeschool.com)
3. Réinitialiser le mot de passe si nécessaire
4. Vérifier la validité des URLs dans `Revision_WCS.xlsx`

### Erreur : `Must be 2000 or fewer in length` (Discord)

**Cause** : Limite de caractères Discord dépassée (rare avec le découpage automatique)

**Solution** :
Ajuster la constante `MAX_LEN` dans `discord_client.py` :
```python
MAX_LEN = 1800  # Réduire si nécessaire (actuellement 1900)
```

### Le test n'apparaît pas sur Discord

**Diagnostic** :
1. Vérifier les logs du terminal pour `[INFO] Test combiné généré et envoyé avec succès !`
2. Confirmer le canal Discord cible
3. Vérifier les permissions du webhook
4. Consulter les logs d'erreur Discord dans le terminal

---

## FAQ

### Le service est-il entièrement gratuit ?

Oui. Tous les composants utilisent des versions gratuites :
- **Groq (Llama 3.3)** : Tier gratuit avec limites généreuses (~14 000 requêtes/jour)
- **Discord** : Webhooks gratuits et illimités
- **Python et dépendances** : Open-source

Pour un usage quotidien (1 test/jour), les quotas gratuits sont largement suffisants.

### Limites de génération quotidienne

**Quotas Groq (tier gratuit)** :
- 14 000 requêtes par jour
- 6 000 tokens par minute
- 20 000 tokens maximum par requête

Un test quotidien représente ~0.007% du quota journalier.

### Compatibilité multiplateforme

Le bot est compatible avec :
- Windows 10/11
- macOS (Intel et Apple Silicon)
- Linux (distributions basées sur Debian/Ubuntu)

Les commandes d'installation varient légèrement (voir section Installation).

### Personnalisation du format des tests

Le prompt système peut être modifié dans `test_generator.py` :

```python
SYSTEM_PROMPT = """
Tu es un professeur de Data Science...

Objectif :
- Construire UN SEUL test de révision de 15 à 20 minutes.
- Chaque cours doit contenir environ 2 ou 3 questions.
- Format Markdown clair.
- ...
"""
```

Paramètres personnalisables :
- Durée du test
- Nombre de questions par cours
- Style des questions (ouvertes, QCM, exercices, etc.)
- Présence ou absence d'un corrigé

### Automatisation quotidienne

**Windows (Planificateur de tâches)** :
1. Ouvrir le Planificateur de tâches
2. Créer une tâche de base
3. Déclencheur : Quotidien à l'heure souhaitée (ex: 08:00)
4. Action : Démarrer un programme
   - Programme : `python.exe`
   - Arguments : `main.py`
   - Dossier de démarrage : Chemin absolu vers le projet

**macOS/Linux (cron)** :
```bash
crontab -e
```

Ajouter la ligne :
```cron
0 8 * * * cd /chemin/absolu/vers/wcs-revision-bot && .venv/bin/python main.py
```

### Modification du modèle d'IA

Groq propose plusieurs modèles. Pour changer, modifier `test_generator.py` :

```python
model_name = "llama-3.3-70b-versatile"  # Configuration actuelle
```

**Alternatives disponibles** :
- `llama-3.1-8b-instant` : Plus rapide, moins précis
- `mixtral-8x7b-32768` : Bon compromis vitesse/qualité
- `llama-3.1-70b-versatile` : Version précédente de Llama

Consulter la [documentation Groq](https://console.groq.com/docs/models) pour la liste complète.

### Sécurité des données

**Mesures de sécurité implémentées** :
- Stockage local des credentials (`.env` non versionné)
- Communications HTTPS uniquement
- Pas de stockage des mots de passe en clair dans le code

**Bonnes pratiques** :
- Ne jamais partager le fichier `.env`
- Utiliser des mots de passe forts et uniques
- Régénérer les clés API en cas de compromission suspectée

---

## Contribution

Les contributions sont les bienvenues. Pour contribuer :

1. Fork du projet
2. Créer une branche feature : `git checkout -b feature/amelioration`
3. Commit des modifications : `git commit -m "Ajout de [fonctionnalité]"`
4. Push vers la branche : `git push origin feature/amelioration`
5. Ouvrir une Pull Request avec description détaillée

**Guidelines** :
- Suivre PEP 8 pour le code Python
- Ajouter des tests pour les nouvelles fonctionnalités
- Documenter les changements dans le README si nécessaire
- Utiliser des messages de commit descriptifs
- Aucun autre llm ne doit remplacer l'actuel
- Idées bienvenues : architectures front avec dashboards et publication des tests sur une appli web (je me chargerais de l'hebergement en ligne)

---

## Licence

GPLv3 -License : Le code peut etre reutilisé SEULEMENT dans vos projets open source. L'utilisation de ce code dans vos projets commerciaux sans l'accord du propriétaire pourras entrainer des poursuites judiciaires. Pour vos projets commerciaux, contactez novarealmteam@gmail.com.
Voir le fichier [LICENSE](LICENSE) pour plus de détails.

---

## Support

- **Issues** : [Ouvrir un ticket](https://github.com/VOTRE_USERNAME/wcs-revision-bot/issues)
- **Discussions** : [Forum du projet](https://github.com/VOTRE_USERNAME/wcs-revision-bot/discussions)
- **Email** : support@example.com

---

**Développé avec Groq (Llama 3.3), Playwright et Discord Webhooks**
