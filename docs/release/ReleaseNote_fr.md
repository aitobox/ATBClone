[English](ReleaseNote.md) | [简体中文](ReleaseNote_zh.md) | [繁體中文](ReleaseNote_zh_TW.md) | [日本語](ReleaseNote_ja.md) | [한국어](ReleaseNote_ko.md) | [Deutsch](ReleaseNote_de.md) | [Français](ReleaseNote_fr.md) | [Русский](ReleaseNote_ru.md) | [Español](ReleaseNote_es.md)

# Notes de publication d'ATBClone (Release Notes)

Ce document répertorie l'ensemble des mises à jour majeures, nouvelles fonctionnalités, optimisations et correctifs apportés à **ATBClone**.

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
