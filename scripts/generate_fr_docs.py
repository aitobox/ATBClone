import os

FR_DIR = "docs/guide/fr"
os.makedirs(FR_DIR, exist_ok=True)

readme = """# 📖 Guide d'utilisation ATBClone (Version française)

[English Version](../en/) | [簡體中文](../zh/) | [繁體中文](../zh-hant/) | [日本語](../ja/) | [한국어](../ko/) | [Deutsch](../de/) | Version française

Bienvenue dans le **Guide officiel d'utilisation d'ATBClone**. Ce manuel vous accompagne pas à pas dans la création d'instances multiples et l'isolation en bac à sable (sandbox) d'applications macOS — des opérations de base pour débutants aux analyses architecturales avancées et diagnostics système.

---

## 🧭 Plan du guide

| Chapitre | Titre | Public visé | Points clés |
| :--- | :--- | :--- | :--- |
| **[Chapitre 1](01-basic-operations.md)** | **[Opérations de base & Gestion des clones](01-basic-operations.md)** | 👶 **Débutants / Tous utilisateurs** | Assistant en 7 étapes, lancement, ouverture directe du dossier de données, **mises à jour synchronisées sans perte de données**, vue tableau (**mises à jour et suppressions par lot**), suppression sécurisée. |
| **[Chapitre 2](02-advanced-custom-recipes.md)** | **[Recettes personnalisées & Paramètres de base](02-advanced-custom-recipes.md)** | ⚡ **Utilisateurs intermédiaires** | Utilisation d'**App Prober (Sonde intelligente)** pour analyser des apps non répertoriées, éditeur visuel de recettes, **paramètres essentiels** (`bundle_id`, `strategy`, `strip_sandbox`, `proxy`). |
| **[Chapitre 3](03-under-the-hood-and-internals.md)** | **[Fonctionnement interne & Paramètres avancés](03-under-the-hood-and-internals.md)** | 🔬 **Experts / Développeurs** | Mécanismes Soft vs Hard Clone, **piliers du Hard Clone & détournement de wrapper binaire**, architecture données-logique découplée, **paramètres YAML avancés** (`environment_injection`, `symlink_whitelist`, macros de chemin). |
| **[Chapitre 4](04-faq-and-troubleshooting.md)** | **[FAQ, Diagnostic système & Support](04-faq-and-troubleshooting.md)** | 🩺 **Tous utilisateurs** | FAQ fréquentes (sécurité des données, chemins de stockage & migration, prévention des bannissements, fonctionnement sans droits root), diagnostic Doctor, **copie des détails du clone & signalement d'issues GitHub**. |

---

## 🌟 Pourquoi choisir ATBClone ?

Sur macOS, les méthodes traditionnelles de clonage (comme une simple copie par `cp -R` ou des alias dans le Terminal) échouent fréquemment car les applications modernes partagent leurs préférences utilisateur, bases de données SQLite et trousseaux d'accès au niveau système.

ATBClone résout ce problème grâce à une **quadruple isolation (Quadruple Isolation)** native :

```mermaid
graph TD
    A[Moteur d'isolation ATBClone] --> B[1. Isolation des données & du cache]
    A --> C[2. Identité visuelle & Dock indépendante]
    A --> D[3. Permissions de sécurité macOS TCC]
    A --> E[4. Isolation du trafic réseau par proxy]
    
    B --> B1["$HOME et $TMPDIR indépendants, aucun verrouillage de base de données"]
    C --> C1["Icône de Dock dédiée, nom personnalisé, recherche Spotlight native"]
    D --> D1["Autorisations micro, caméra et disque gérées séparément"]
    E --> E1["Routage proxy HTTP/SOCKS5 dédié par clone (anti-fingerprinting)"]
```

1. **📦 Isolation des données & du cache** : Chaque clone dispose de son propre répertoire personnel isolé (`$HOME`) ou `--user-data-dir`. Plusieurs comptes peuvent s'exécuter en parallèle sans conflit de bases de données ou de cache.
2. **🎨 Identité visuelle & Dock indépendante** : Les clones possèdent leurs propres noms et icônes, et apparaissent de manière autonome dans Spotlight, le Launchpad et le Dock.
3. **🛡️ Permissions de sécurité (TCC) isolées** : Grâce à des identifiants `CFBundleIdentifier` uniques, macOS considère chaque clone comme une entité distincte avec ses propres autorisations système.
4. **🌐 Isolation réseau par proxy** : Acheminez le trafic de certains clones via des proxys HTTP ou SOCKS5 distincts sans altérer la connexion réseau de l'hôte.

---

## 📚 Concepts clés & Glossaire

* **Application hôte (Host App)** : L'application d'origine installée sur votre Mac (généralement dans `/Applications`).
* **Application clonée (Clone App)** : L'instance générée par ATBClone (par défaut dans `~/ATBClone/Apps`).
* **Hard Clone (Duplication physique & détournement de wrapper)** : Copie complète du bundle, modification du Bundle ID, injection de scripts d'environnement et re-signature. Recommandé pour WeChat, Telegram, Slack et Discord.
* **Soft Clone (Wrapper de lanceur)** : Crée un lanceur léger transmettant des arguments de données isolés (`--user-data-dir`). Idéal pour les navigateurs et éditeurs de code (Cursor, VS Code, Chrome).
* **Recette (Recipe)** : Fichier YAML décrivant les règles de clonage et d'isolation d'une application.
* **Répertoire de données isolé** : Dossier où sont stockés les discussions, réglages et caches (par défaut `~/ATBClone/Data/<NomDuClone>`).

---

## 🚀 Démarrage rapide

1. **Téléchargement & Installation** : Téléchargez `ATBClone-*.dmg` depuis les [GitHub Releases](https://github.com/aitobox/ATBClone/releases) et glissez `ATBClone.app` dans `/Applications`.
2. **Lancement** : Ouvrez ATBClone depuis le Launchpad.
3. **Assistant** : Cliquez sur **"+ Nouveau clone"** en haut à droite.
4. **Suivez les 7 étapes** : Choisissez l'application ➔ Vérifiez la recette ➔ Nommez le clone ➔ Validez les chemins ➔ **"Cloner maintenant"**.
5. **Profitez** : Cliquez sur **"Lancer"** ou démarrez votre clone via Spotlight !
"""

ch01 = """# Chapitre 1 : Opérations de base & Gestion des clones

Ce chapitre vous guide dans la création de votre premier clone à l'aide de l'assistant interactif en 7 étapes, puis détaille les opérations quotidiennes (lancement, accès aux données, synchronisation des mises à jour et suppression sécurisée).

---

## 📑 Sommaire

- [Créer une application clonée (Assistant en 7 étapes)](#creer-une-application-clonee-assistant-en-7-etapes)
  - [Étape 1 : Sélectionner l'application cible](#etape-1-selectionner-lapplication-cible)
  - [Étape 2 : Vérifier la recette et la stratégie](#etape-2-verifier-la-recette-et-la-strategie)
  - [Étape 3 : Définir l'identité et la langue](#etape-3-definir-lidentite-et-la-langue)
  - [Étape 4 : Confirmer l'emplacement d'installation](#etape-4-confirmer-lemplacement-dinstallation)
  - [Étape 5 : Configurer le répertoire de données](#etape-5-configurer-le-repertoire-de-donnees)
  - [Étape 6 : Configurer un proxy réseau (Optionnel)](#etape-6-configurer-un-proxy-reseau-optionnel)
  - [Étape 7 : Confirmer et lancer le clonage](#etape-7-confirmer-et-lancer-le-clonage)
- [Gérer vos applications clonées](#gerer-vos-applications-clonees)
  - [Lancer un clone](#lancer-un-clone)
  - [Ouvrir directement le dossier de données](#ouvrir-directement-le-dossier-de-donnees)
  - [Synchronisation sans perte lors des mises à jour](#synchronisation-sans-perte-lors-des-mises-a-jour)
  - [Opérations par lot dans la vue tableau](#operations-par-lot-dans-la-vue-tableau)
  - [Suppression sécurisée (Conserver vs Purger les données)](#suppression-securisee-conserver-vs-purger-les-donnees)

---

## 🪄 Créer une application clonée (Assistant en 7 étapes)

Cliquez sur **"+ Nouveau clone"** sur le tableau de bord pour ouvrir l'assistant.

### Étape 1 : Sélectionner l'application cible
Sélectionnez le fichier `.app` à cloner (ex. `/Applications/WeChat.app` ou `Cursor.app`).

### Étape 2 : Vérifier la recette et la stratégie
ATBClone analyse automatiquement l'application et choisit la meilleure stratégie (`Hard Clone` ou `Soft Clone`).

### Étape 3 : Définir l'identité et la langue
Définissez un nom clair (ex. `WeChat-Pro`), personnalisez l'icône si souhaité, et fixez la langue d'interface.

### Étape 4 : Confirmer l'emplacement d'installation
Par défaut : `~/ATBClone/Apps/<NomDuClone>.app`.

### Étape 5 : Configurer le répertoire de données
Par défaut : `~/ATBClone/Data/<NomDuClone>`.
* **Architecture découplée** : La séparation stricte entre l'exécutable (`Apps/`) et les données utilisateur (`Data/`) garantit que vos fichiers ne sont jamais supprimés lors d'une mise à jour de l'app.

### Étape 6 : Configurer un proxy réseau (Optionnel)
Configurez un proxy `HTTP` ou `SOCKS5` dédié si nécessaire.

### Étape 7 : Confirmer et lancer le clonage
Vérifiez le récapitulatif et cliquez sur **"Cloner maintenant"**.

---

## 🖥️ Gérer vos applications clonées

* **Lancement** : Depuis l'interface ATBClone, via la recherche Spotlight (`Cmd + Espace`), ou directement depuis le Dock.
* **Accès aux données** : Cliquez sur l'icône de dossier d'une carte pour ouvrir le répertoire de données dans le Finder.
* **Mises à jour synchronisées** : Cliquez sur **"Mettre à jour"** après une mise à jour de l'application hôte. Le clone est mis à jour sans aucune perte de données.
* **Suppression sécurisée** : Choisissez entre supprimer uniquement l'application ou effacer également le dossier de données.
"""

ch02 = """# Chapitre 2 : Recettes personnalisées & Paramètres de base

Apprenez à utiliser **App Prober** pour analyser des applications tierces et à créer des recettes personnalisées avec l'éditeur visuel.

---

## 📑 Sommaire

- [Analyse automatique avec App Prober](#analyse-automatique-avec-app-prober)
  - [Diagnostic en un clic via la GUI](#diagnostic-en-un-clic-via-la-gui)
  - [Diagnostic en ligne de commande (CLI)](#diagnostic-en-ligne-de-commande-cli)
- [Structure YAML d'une recette](#structure-yaml-dune-recette)
  - [1. bundle_id](#1-bundle_id)
  - [2. strategy](#2-strategy)
  - [3. strip_sandbox](#3-strip_sandbox)
  - [4. proxy](#4-proxy)

---

## 🔍 Analyse automatique avec App Prober

```bash
atbclone probe /Applications/Slack.app
```

Sortie :

```text
================================================================================
ATBClone Application Prober
Target: /Applications/Slack.app
================================================================================
[+] Bundle ID: com.tinyspeck.slackmacgap
[+] Framework: Electron (Chromium-based)
[+] App Sandbox: Enabled
[+] Recommendation: Strategy=hard_clone, StripSandbox=true
================================================================================
```

---

## 📜 Structure YAML d'une recette

```yaml
version: "1.0"
name: "Slack"
description: "Configuration multi-instances isolée pour Slack"

bundle_id: "com.tinyspeck.slackmacgap"
strategy: "hard_clone"
strip_sandbox: true

proxy:
  type: "http"
  host: "127.0.0.1"
  port: 7890
```

* `bundle_id` : Identifiant de l'application originale.
* `strategy` : `hard_clone` (duplication et wrappers) ou `soft_clone` (arguments de données).
* `strip_sandbox` : Supprime la restriction du bac à sable pour autoriser des dossiers de données personnalisés.
* `proxy` : Configuration de proxy réseau optionnel.
"""

ch03 = """# Chapitre 3 : Fonctionnement interne & Paramètres avancés

Analyse détaillée des mécanismes internes d'ATBClone, du détournement de wrapper binaire et des macros YAML dynamiques.

---

## 📑 Sommaire

- [Comparatif architectural : Soft Clone vs Hard Clone](#comparatif-architectural--soft-clone-vs-hard-clone)
- [Les 3 piliers technologiques du Hard Clone](#les-3-piliers-technologiques-du-hard-clone)
  - [1. Mutation du Bundle ID](#1-mutation-du-bundle-id)
  - [2. Détournement de wrapper binaire (Wrapper Hijack)](#2-detournement-de-wrapper-binaire-wrapper-hijack)
  - [3. Suppression du bac à sable et re-signature ad-hoc](#3-suppression-du-bac-a-sable-et-re-signature-ad-hoc)
- [Paramètres YAML avancés](#parametres-yaml-avances)
- [Exemple complet de recette](#exemple-complet-de-recette)

---

## ⚡ Les 3 piliers technologiques du Hard Clone

### 1. Mutation du Bundle ID
Le fichier `Info.plist` reçoit un identifiant unique (`CFBundleIdentifier`), permettant à macOS de gérer les permissions et notifications de manière totalement indépendante.

### 2. Détournement de wrapper binaire (Wrapper Hijack)
1. L'exécutable réel est renommé en `<App>.real`.
2. Un script shell POSIX prend sa place et redéfinit l'environnement :
   * `export HOME="<DossierDeDonnées>"`
   * `export TMPDIR="<DossierDeDonnées>/tmp"`
   * `export XDG_DATA_HOME="<DossierDeDonnées>/Library/Application Support"`
3. Le script démarre ensuite l'exécutable `.real`.

### 3. Suppression du bac à sable et re-signature ad-hoc
L'autorisation App Sandbox est purgée des droits de l'application, puis celle-ci est signée localement avec `codesign -f -s -`.

---

## ⚙️ Paramètres YAML avancés

```yaml
version: "1.0"
name: "Discord"
strategy: "hard_clone"
strip_sandbox: true
injection_mode: "wrapper_hijack"

proxy:
  type: "socks5"
  host: "127.0.0.1"
  port: 10808

environment_injection:
  DISCORD_USER_DATA_DIR: "{DATA_DIR}/discord_data"

launch_arguments:
  - "--start-minimized"

symlink_whitelist:
  - "~/Library/Audio"
```

* Macros dynamiques disponibles : `{DATA_DIR}`, `{CLONE_NAME}`, `{BUNDLE_ID}`, `{HOST_APP}`.
"""

ch04 = """# Chapitre 4 : FAQ, Diagnostic système & Support

Réponses aux questions courantes, conseils de sécurité et instructions pour signaler un bug sur GitHub.

---

## 📑 Sommaire

- [Foire aux questions (FAQ)](#foire-aux-questions-faq)
  - [1. Un clone affecte-t-il les données de l'application hôte ?](#1-un-clone-affecte-t-il-les-donnees-de-lapplication-hote-)
  - [2. Où sont stockées les données ? Comment faire une sauvegarde ?](#2-ou-sont-stockees-les-donnees--comment-faire-une-sauvegarde-)
  - [3. Y a-t-il un risque de bannissement de compte ?](#3-y-a-t-il-un-risque-de-bannissement-de-compte-)
  - [4. Des droits administrateur (Root/Sudo) sont-ils requis ?](#4-des-droits-administrateur-rootsudo-sont-ils-requis-)
  - [5. Que faire face aux avertissements Gatekeeper ("application endommagée") ?](#5-que-faire-face-aux-avertissements-gatekeeper-application-endommagee-)
- [Diagnostic avec l'outil Doctor](#diagnostic-avec-loutil-doctor)
- [Signaler un problème sur GitHub](#signaler-un-probleme-sur-github)

---

## ❓ Foire aux questions (FAQ)

### 1. Un clone affecte-t-il les données de l'application hôte ?
**Non, absolument pas.** ATBClone isole l'ensemble des données dans `~/ATBClone/Data/<NomDuClone>`. Les données originales ne sont jamais touchées.

### 2. Où sont stockées les données ? Comment faire une sauvegarde ?
Toutes les données sont dans `~/ATBClone/Data/<NomDuClone>`. Il suffit de copier ce dossier pour transférer vos données vers un autre Mac.

### 3. Y a-t-il un risque de bannissement de compte ?
ATBClone repose sur une redirection d'environnement non invasive et n'altère ni la mémoire ni les protocoles réseau. Du point de vue système, l'application s'exécute normalement. L'utilisation d'un proxy dédié permet en outre de masquer l'adresse IP partagée.

### 4. Des droits administrateur (Root/Sudo) sont-ils requis ?
**Non.** Tout fonctionne dans l'espace utilisateur sans modifier les fichiers système.

### 5. Que faire face aux avertissements Gatekeeper ("application endommagée") ?
Exécutez la commande suivante dans le Terminal :
```bash
xattr -cr ~/ATBClone/Apps/<NomDuClone>.app
```

---

## 🩺 Diagnostic avec l'outil Doctor

```bash
atbclone doctor
```

Vérifie la compatibilité macOS, la présence des outils de commande Xcode et les droits d'écriture.

---

## 🐞 Signaler un problème sur GitHub

1. Dans ATBClone, ouvrez les **"Détails du clone"**.
2. Cliquez sur **"Copier les informations de diagnostic"**.
3. Créez un rapport sur [GitHub Issues](https://github.com/aitobox/ATBClone/issues) et collez le contenu.
"""

for fn, content in [("README.md", readme), ("01-basic-operations.md", ch01), ("02-advanced-custom-recipes.md", ch02), ("03-under-the-hood-and-internals.md", ch03), ("04-faq-and-troubleshooting.md", ch04)]:
    with open(f"{FR_DIR}/{fn}", "w", encoding="utf-8") as f:
        f.write(content)
    print(f"✓ Created fr/{fn}")
