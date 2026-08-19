[English](ReleaseNote.md) | [简体中文](ReleaseNote_zh.md) | [繁體中文](ReleaseNote_zh_TW.md) | [日本語](ReleaseNote_ja.md) | [한국어](ReleaseNote_ko.md) | [Deutsch](ReleaseNote_de.md) | [Français](ReleaseNote_fr.md) | [Русский](ReleaseNote_ru.md) | [Español](ReleaseNote_es.md)

# Notes de publication d'ATBClone (Release Notes)

Ce document répertorie l'ensemble des mises à jour majeures, nouvelles fonctionnalités, optimisations et correctifs apportés à **ATBClone**.

---

## [v0.6.0] - 2026-08-19

### 📂 Support des répertoires de données personnalisés
- **Personnalisation de l'emplacement des données (`--data-dir`)**:
  - Ajout de l'option `--data-dir` à la commande `atbclone clone` pour choisir l'emplacement de stockage des données (SSD externe, dossier de travail personnalisé, etc.).
  - Intégration de la configuration du répertoire de données dans l'assistant interactif (`atbclone wizard`).
  - Prise en charge des variables dynamiques de répertoire de données dans les modèles de recettes et les moteurs de clonage.

### 🗑️ Désinstallation et nettoyage des clones améliorés (`atbclone remove`)
- **Contrôle sécurisé de la suppression des données**:
  - Ajout de l'option `--purge-data` à `atbclone remove` pour supprimer complètement l'application et les dossiers de données associés.
  - Ajout de l'option `--keep-data` pour désinstaller l'application tout en conservant les données utilisateur.
  - Boîtes de dialogue interactives de confirmation permettant de choisir entre conservation et purge des données.
  - Gestion améliorée des dossiers orphelins et des avertissements de permissions.

### 🆔 Standardisation des identifiants Bundle & Multilinguisme
- **Génération standardisée des Bundle ID**:
  - Ajout de `AppInspector.generate_bundle_id` pour uniformiser la création des identifiants entre `clone`, `wizard` et `update`.
- **Localisation complète**:
  - Traduction intégrale des invites de répertoire, des confirmations de suppression et des statuts de purge dans les 9 langues.
- **Tests**:
  - Augmentation de la suite de tests à 213 tests unitaires automatisés.

---

## [v0.5.0] - 2026-08-19

### 🔐 Signature de code Apple et pipeline de notarisation
- **Hardened Runtime et signature certifiée**:
  - Intégration complète de la signature avec certificat Apple Developer ID Application, Hardened Runtime (`--options runtime`), horodatage et autorisations JIT (`scripts/entitlements.plist`).
  - Script automatisé `scripts/notarize.sh` pour la soumission directe à Apple Notary via `xcrun notarytool` avec profils Keychain (`--keychain-profile`).
  - Prise en charge des options `--sign-identity`, `--skip-sign` et `--notarize` dans `scripts/build_cli.sh` et `scripts/release.sh` avec repli ad-hoc automatique.

### 🚀 Clonage dur Chromium et injection d'arguments de lancement
- **Injection d'arguments dans `HardCloneEngine`**:
  - Amélioration de `HardCloneEngine` pour injecter dynamiquement des paramètres tels que `--user-data-dir={{ATB_DATA_DIR}}` dans les scripts de lancement.
  - Mise à niveau des recettes intégrées pour **Google Chrome**, **Microsoft Edge** et **Arc Browser** vers la stratégie `hard_clone`.
- **Surcharge de stratégie en ligne de commande**:
  - Nouvelle option `--strategy` (`hard_clone` ou `soft_clone`) dans la commande `atbclone clone`.

### ⚡ Transmission de processus et tests enrichis
- **Gestion des processus**: Amélioration des scripts d'emballage `SoftCloneEngine` avec transmission `exec "$@"`.
- **Suite de tests**: 199 tests automatisés couvrant la signature, la notarisation et les moteurs de clonage.

---

## [v0.4.0] - 2026-08-19

### 🌐 Support multilingue complet en 9 langues pour le CLI et la documentation
- **Internationalisation complète du CLI en 9 langues**:
  - Extension du moteur `atbclone.core.i18n` avec le support complet de l'anglais, du chinois simplifié, du chinois traditionnel, du japonais, du coréen, de l'allemand, du français, du russe et de l'espagnol.
  - Toutes les commandes CLI (`wizard`, `clone`, `probe`, `list`, `recipe`, `doctor`, `update`, `remove`, `version`) intègrent des invites, des tableaux et des diagnostics d'erreur localisés.
- **Structure standardisée des notes de version multilingues**:
  - Gestion unifiée des notes de version en 9 langues sous le répertoire `docs/release/`.

### 🔄 Pipeline automatisé de publication et de synchronisation des versions
- **Validation automatique des ReleaseNotes en 9 langues**:
  - Amélioration de `scripts/manage_version.py` et `scripts/release.sh` pour vérifier automatiquement la présence de la section de version dans les 9 fichiers avant la création du tag Git.
  - Ajout de l'option `--check-notes` pour prévenir tout oubli de documentation de version.
- **Suite de tests enrichie**:
  - Augmentation des tests automatisés à 191 tests couvrant l'internationalisation et le flux de publication.

---

## [v0.3.0] - 2026-08-19

### 🌐 Internationalisation et support multilingue (i18n)
- **Détection automatique de la langue du système macOS** :
  - Intégration du moteur `atbclone.core.i18n` détectant automatiquement la langue de l'interface macOS via `AppleLanguages` et `AppleLocale`.
  - Adaptation intelligente de l'assistant interactif, des invites du terminal, des en-têtes de tableau et des journaux d'erreurs en fonction de l'environnement (Français, Anglais, Chinois, etc.).
  - Prise en charge de la variable d'environnement `ATBCLONE_LANG` (`ATBCLONE_LANG=en` / `ATBCLONE_LANG=zh`) pour forcer manuellement la langue d'exécution.
- **Documentation multilingue** :
  - Standardisation de la documentation en anglais (`Readme.md`) et mise à disposition de la version chinoise (`Readme_zh.md`).
  - Publication des notes de version en 9 langues : anglais, chinois simplifié, chinois traditionnel, japonais, coréen, allemand, français, russe et espagnol.

### 🛠️ Améliorations du CLI et de la compilation
- **Internationalisation de l'assistant** : Prise en charge multilingue complète d'`atbclone wizard` (noms personnalisés, icônes `.icns` et proxys).
- **Binaire autonome** : Recompilation de `./dist/ATBCloneCli` via Nuitka avec dictionnaire multilingue intégré et compatibilité sandbox accrue (`PYTHONNOUSERSITE=1`).
- **Suite de tests** : Ajout de `test_i18n.py` et validation des 186 tests unitaires automatisés.

---

## [v0.2.0] - 2026-08-18

### 🚀 Fonctionnalités majeures
- **Assistant interactif de clonage (`atbclone wizard`)** :
  - Guidage pas-à-pas dans le terminal avec support du glisser-déposer de chemins `.app`.
  - Incrémentation automatique du nom du clone (ex. `WeChat2`, `WeChat3`).
  - Personnalisation du nom d'affichage de l'application et sélection d'icônes `.icns`.
  - Configuration interactive de proxys réseau dédiés (HTTP et SOCKS5) avec authentification.
- **Sondeur d'application avancé (`atbclone probe`)** :
  - Analyse automatique de l'architecture Mach-O (arm64, x86_64, Universal), des frameworks (Electron, Flutter, Chromium, Qt, Cocoa) et des privilèges sandbox (`com.apple.security.app-sandbox`).
  - Recommandation dynamique de la meilleure stratégie de clonage (`hard_clone` ou `soft_clone`) et génération de fichiers Recipe YAML.
  - Exécution automatique du sondeur lors d'un `atbclone clone` pour toute application non répertoriée.
- **Création d'un exécutable unique** :
  - Ajout de `scripts/build_cli.sh` pour compiler un binaire macOS arm64 autonome et sans dépendances (`dist/ATBCloneCli`) à l'aide de Nuitka.

### ⚡ Améliorations et correctifs
- Élévation des privilèges optimisée avec la boîte de dialogue native macOS `osascript` pour le dossier `/Applications`.
- Échappement rigoureux des chemins via `shlex.quote` pour prévenir les erreurs liées aux espaces et caractères spéciaux.

---

## [v0.1.0] - 2026-08-17

### 🌟 Première version officielle
- **Architecture de clonage à double moteur** :
  - **Moteur Hard Clone** : Duplication intégrale du bundle, modification du fichier `Info.plist`, isolation des répertoires `HOME` / `TMPDIR`, suppression optionnelle du sandbox et resignature ad-hoc.
  - **Moteur Soft Clone** : Lanceur léger pour navigateurs Chromium et éditeurs de code avec injection automatisée de `--user-data-dir`.
- **Plus de 18 recettes intégrées** :
  - Messageries : WeChat, QQ, Telegram, LINE, Slack, Discord, Skype.
  - Clients IA : ChatGPT (Codex), Gemini, Antigravity, Antigravity IDE.
  - Navigateurs et outils de développement : Google Chrome, Microsoft Edge, Firefox, Arc, Cursor, VS Code, Zed.
- **Commandes CLI complètes** :
  - `clone` : Créer un clone d'application.
  - `list` : Afficher la liste des clones actifs sous forme de tableau Rich.
  - `update` : Mettre à jour un clone après la mise à niveau de l'application principale sans perte de données.
  - `remove` : Supprimer un clone en toute sécurité.
  - `recipe` : Inspecter les recettes intégrées et locales.
  - `doctor` : Vérification automatique de l'environnement système (`codesign`, `xcode-select`, `PlistBuddy`).
