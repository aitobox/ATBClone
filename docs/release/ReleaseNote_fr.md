[English](ReleaseNote.md) | [简体中文](ReleaseNote_zh.md) | [繁體中文](ReleaseNote_zh_TW.md) | [日本語](ReleaseNote_ja.md) | [한국어](ReleaseNote_ko.md) | [Deutsch](ReleaseNote_de.md) | [Français](ReleaseNote_fr.md) | [Русский](ReleaseNote_ru.md) | [Español](ReleaseNote_es.md)

# Notes de publication d'ATBClone (Release Notes)

Ce document répertorie l'ensemble des mises à jour majeures, nouvelles fonctionnalités, optimisations et correctifs apportés à **ATBClone**.

---

## [v0.9.9] - 2026-08-24

### 📋 Texte sélectionnable & « Copier toutes les infos » dans les détails du clone
- **Sélection et export interactif**:
  - Activation de la sélection de texte Cocoa native (`setSelectable_`) dans `CloneDetailWindow` pour copier aisément chemins, identifiants et arguments.
  - Ajout du bouton « Copier toutes les infos » pour copier un rapport de diagnostic formaté en Markdown dans le presse-papiers.

### 🎨 Design d'interface natif macOS & Espacements optimisés
- **Raffinement des thèmes et composants**:
  - Ajustement des jetons de couleur de `Theme` en modes clair et sombre (`BG_APP`, `BG_CARD`, `BG_HOVER`, `BORDER`, `TEXT_PRIMARY`, `TEXT_MUTED`, `ACCENT`).
  - Amélioration de l'arrondi des cartes, des marges internes et de l'espacement visuel général.

### 📖 Manuel utilisateur multilingue complet (`docs/guide/`)
- **Documentation exhaustive**:
  - Publication des manuels utilisateurs complets en anglais (`docs/guide/en/`) et en chinois (`docs/guide/zh-cn/`).
  - Contient le chapitre 1 (Opérations de base), chapitre 2 (Recettes avancées), chapitre 3 (Fonctionnement interne) et chapitre 4 (FAQ et diagnostic).

### 🧪 Tests
- **Couverture de tests**:
  - Suite de tests portée à 431 tests automatisés.

---

## [v0.9.8] - 2026-08-24

### 🔒 Extraction des autorisations (Entitlements) & Stabilité du moteur Hard Clone
- **Préservation des autorisations de l'application source**:
  - Amélioration de `HardCloneEngine` pour extraire fidèlement les autorisations Mach-O d'origine avec `codesign -d --entitlements :-`.
  - Protection contre la génération d'autorisations vides ou corrompues lors de la resignature.
- **Isolation renforcée des conteneurs sandbox**:
  - Configuration de `strip_sandbox: false` sur l'ensemble des recettes en hard clone (WeChat, QQ, WeWork, WPS Office, LINE, Skype, CapCut, etc.).
  - Assure l'isolation stricte des conteneurs macOS (`~/Library/Containers/<new_bundle_id>`), évitant toute interférence de session.

### 📚 Documentation & Synchronisation des schémas
- **Mise à jour des documentations**:
  - Synchronisation de `README.md` et `README_zh.md` avec les nouvelles options `app_type`, `strip_sandbox` et les guides CLI/GUI.

### 🧪 Tests
- **Fiabilité**:
  - Validation réussie des 428 tests automatisés.

---

## [v0.9.7] - 2026-08-24

### 🔍 Détection intelligente d'architecture & Adaptation linguistique
- **Reconnaissance du framework d'exécution (`app_type`)**:
  - Introduction du champ `app_type` (`electron`, `chromium`, `qt`, `flutter`, `native_cocoa`, `java`, `unknown`) dans le modèle Recipe.
  - `AppProber.detect_app_type` analyse les frameworks, dylibs et structures JVM pour détecter le moteur sous-jacent.
  - Standardisation des 34 recettes intégrées avec configuration explicite de `app_type` et `strip_sandbox`.
- **Injection linguistique adaptative selon le framework**:
  - Paramètres linguistiques personnalisés (`--lang=` pour Chromium/Electron, `-AppleLanguages` pour Native Cocoa, `-user.language` pour Java).

### 🧬 Analyse et validation des arguments binaires Mach-O
- **Détection automatique des arguments de données**:
  - Implémentation de `BinaryArgumentProber` pour scanner les exécutables Mach-O et détecter les arguments de répertoire de données (`--user-data-dir`, `--profile-directory`, `--datadir`, etc.).
- **Validation des arguments de lancement**:
  - `LaunchArgumentValidator` filtre les arguments incompatibles ou conflictuels lors de la création du clone.

### 📋 Inspection et copie des paramètres injectés
- **Inspecteur de paramètres injectés (`CloneInspector`)**:
  - `CloneInspector` extrait les variables d'environnement, proxys, remplacements de langue et arguments de lancement des bundles clones.
  - Nouvelle section « Paramètres injectés » dans `CloneDetailWindow` avec bouton de copie rapide.

### ⚙️ Personnalisation avancée dans l'éditeur de recettes
- **Édition visuelle enrichie (`RecipeEditWindow`)**:
  - Sélection du type de framework, personnalisation des arguments de lancement, configuration proxy, variables d'environnement et listes blanches de liens symboliques.

### 🧪 Tests
- **Extension de la suite de tests**:
  - Suite de tests portée à 428 tests automatisés.

---

## [v0.9.6] - 2026-08-24

### 🖱️ Tri natif par clic sur l'en-tête de tableau Cocoa
- **Tri interactif des colonnes**:
  - Intégration du tri par clic d'en-tête `NSTableViewHeaderView` dans `CloneListView` et `RecipeListView`.
  - Prise en charge du tri ascendant/descendant avec indicateurs visuels et synchronisation avec la barre d'outils.
  - Préservation automatique de la sélection lors du tri.

### 📦 Sélection multiple et opérations par lot
- **Gestion groupée des clones (`CloneListView`)**:
  - Prise en charge de la sélection multiple (`multiple_select=True`) et mise à jour dynamique des boutons d'action.
  - Mises à jour groupées et suppressions par lot avec confirmation de purge des données.
- **Suppression groupée de règles et protection (`RecipeListView`)**:
  - Sélection multiple et suppression de règles personnalisées.
  - Boîtes de dialogue adaptées selon le contexte (protection des règles intégrées en lecture seule, filtrage des sélections mixtes).
  - Verrouillage d'état occupé (busy lock) pour sécuriser les traitements par lot.

### 🛠️ Diagnostic Xcode Command Line Tools dans la vue Doctor
- **Vérification de la chaîne d'outils**:
  - Détection automatique de la présence des outils Xcode (`xcode-select -p`, `codesign`, `lipo`, `otool`, `install_name_tool`) avec instructions d'installation dans la vue Doctor.

### ℹ️ Métadonnées de la boîte « À propos » macOS
- **Affichage standardisé**:
  - Transmission propre des numéros de version et des mentions légales dans `orderFrontStandardAboutPanelWithOptions:`.

### 🧪 Tests
- **Extension de la suite de tests**:
  - Suite de tests portée à 369 tests automatisés.

---

## [v0.9.5] - 2026-08-23

### 📝 Nouveau composant `WrappingLabel` & Retour à la ligne automatique
- **Gestion du texte multiligne sous macOS**:
  - Création du composant `WrappingLabel` pour contourner les limitations d'affichage sur une seule ligne de Toga Cocoa.
  - Recalcul dynamique de la hauteur (`cellSizeForBounds_`) selon la largeur du conteneur, évitant l'élargissement excessif des fenêtres lors de l'affichage de chemins longs.
- **Amélioration des rapports d'analyse et détails**:
  - Intégration de `WrappingLabel` dans `ProbeView` (rapport de diagnostic, évaluation de compatibilité), `CloneDetailWindow` et `WizardWindow`.

### 🧪 Isolation des tests et gestion de configuration
- **Résolution dynamique des chemins**:
  - Amélioration de `StateManager` et `RecipeLoader` pour évaluer les chemins à l'exécution, garantissant l'isolation des tests unitaires vis-à-vis des données locales de l'utilisateur.
- **Tests**:
  - Suite de tests portée à 347 tests automatisés.

---

## [v0.9.4] - 2026-08-23

### 📁 Migration du répertoire de données par défaut vers `~/ATBClone`
- **Gestion intuitive des données utilisateur**:
  - Déplacement du dossier racine par défaut de `~/.atbclone` vers le répertoire accessible `~/ATBClone` (`~/ATBClone/Data/`, `~/ATBClone/clones.yaml`).
  - Facilite l'accès, la sauvegarde et l'inspection des données de clones dans le Finder et le Terminal.

### 🏷️ Application stricte du nom d'affichage personnalisé
- **Nettoyage des localisations**:
  - Suppression de `LSHasLocalizedDisplayName` et nettoyage des fichiers `InfoPlist.strings` dans `SoftCloneEngine` et `HardCloneEngine`.
  - Garantit que le Finder, le Dock, Spotlight et le Moniteur d'activité affichent précisément le nom choisi par l'utilisateur.

### 🔄 Enregistrement automatique LaunchServices
- **Actualisation instantanée du cache**:
  - Enregistrement immédiat via `lsregister -f` lors de la création ou mise à jour pour rafraîchir les icônes et métadonnées sans redémarrage.

### 📦 Documentation et tests
- **Mise à jour globale**:
  - Actualisation des guides, des paramètres GUI et des 341 tests automatisés.

---

## [v0.9.3] - 2026-08-21

### 🛡️ Inspection d'applications renforcée et validation dans l'assistant
- **Détection préventive des applications iOS-on-Mac**:
  - Mise à niveau de `AppInspector.inspect_app` pour vérifier immédiatement `UIDeviceFamily` et `LSRequiresIPhoneOS` lors de la sélection de fichier.
  - Dans l'assistant de création (`WizardWindow`), la sélection d'une application iOS wrapper déclenche instantanément une boîte de dialogue d'avertissement et réinitialise la sélection.

### 🍏 Fermeture propre sous macOS et nettoyage mémoire Cocoa
- **Prévention des plantages à la fermeture**:
  - Amélioration de `TrayService.disable()` et `ATBCloneApp.exit_app()` pour détacher proprement les cibles et sélecteurs de l'icône de barre des menus.
  - Arrêt sécurisé de la boucle d'événements Cocoa (`NSApp.terminate_` / `os._exit(0)`), éliminant tout risque de crash lors de la fermeture via le menu de la barre d'état ou `Cmd+Q`.

### 📦 Tests
- **Suite de tests**:
  - Extension à 341 tests automatisés.

---

## [v0.9.2] - 2026-08-21

### 🍏 Masquage dynamique de l'icône du Dock macOS et amélioration du Tray
- **Gestion automatique de la visibilité dans le Dock**:
  - Gestion dynamique de l'icône du Dock via les politiques d'activation AppKit (`NSApplicationActivationPolicy`).
  - Lors de la réduction ou de la fermeture vers la barre des menus, l'icône du Dock est automatiquement masquée (`NSApplicationActivationPolicyAccessory`).
  - Lors de la restauration depuis la barre des menus, l'icône réapparaît instantanément (`NSApplicationActivationPolicyRegular`) avec le focus sur la fenêtre.
- **Gestionnaire de réouverture depuis le Dock**:
  - Ajout du support de `applicationShouldHandleReopen:hasVisibleWindows:` dans `AppDelegate` pour réafficher la fenêtre principale lors d'un clic sur l'icône du Dock.

### 📦 Optimisation des ressources et tests
- **Allègement des icônes**:
  - Compression et optimisation des fichiers d'icônes (`logo.icns`, `logo.png`) pour réduire la taille du bundle.
- **Tests**:
  - Suite de tests portée à 338 tests automatisés.

---

## [v0.9.1] - 2026-08-21

### 🛡️ Détection et rejet sécurisé des applications iOS-on-Mac
- **Gestion sécurisée des architectures non prises en charge**:
  - Amélioration de `AppProber`, `SoftCloneEngine` et `HardCloneEngine` pour détecter précisément les applications portées depuis iOS/iPadOS sur Apple Silicon (contenant `Wrapper/` ou `UIDeviceFamily` / `LSRequiresIPhoneOS=True`).
  - Rejet sécurisé des tentatives de clonage de ces applications dans la CLI (`atbclone clone`, `atbclone wizard`) et l'assistant GUI avec message explicatif (`error_ios_wrapper_unsupported`), évitant tout crash au lancement.

### 🎨 Génération automatique d'icônes dans les scripts de build
- **Compilation dynamique `.icns`**:
  - Ajout de la génération automatisée d'icônes `.icns` via `sips` et `iconutil` dans `scripts/build_gui.sh` lors de la création du fichier DMG.
  - Intégration et validation renforcées des ressources dans le packaging.

### 🌐 Localisation et tests
- **Messages d'erreur multilingues**:
  - Traduction du message de rejet des applications iOS dans les 9 langues.
- **Tests**:
  - Extension de la suite de tests à 336 tests automatisés.

---

## [v0.9.0] - 2026-08-21

### 🌐 Isolation linguistique et régionale indépendante par clone
- **Sélection de la langue et du locale (`--language` / `--locale`)**:
  - Possibilité d'exécuter chaque clone dans une langue dédiée, indépendamment de la langue de macOS et de l'application principale.
  - Prise en charge des options `--language` / `--locale` dans la CLI (`atbclone clone`, `atbclone wizard`) et sélecteur de langue interactif dans l'interface graphique.
  - Injection automatique des préférences `AppleLanguages` et `AppleLocale` dans les scripts lanceurs et exécutables.
  - Nouveau module `atbclone.core.locale` pour l'analyse des identifiants BCP-47.

### 🆔 Résolution robuste des identifiants Bundle multi-instances
- **Identifiants uniques sans collision**:
  - Introduction de `AppInspector.find_next_bundle_id` pour attribuer automatiquement des Bundle ID incrémentaux et sans conflit (`com.vendor.app.atb1`, `atb2`, etc.).

### 🍏 Restauration depuis la barre des menus et cycle de vie de la fenêtre
- **Réactivation fluide depuis le System Tray**:
  - Correction de l'activation, de la déminiaturisation et de la mise au premier plan lors de l'ouverture via `TrayService`.
  - Interception de la fermeture de fenêtre (`Cmd+W` / bouton rouge) pour masquer vers la barre des menus lorsque l'option est active.
  - Prise en charge affinée des clics sur l'icône de statut (gauche, droite, Ctrl+clic).

### ⚡ Mise à jour de clone et nettoyage de la destination
- **Mises à jour atomiques**:
  - Résolution des conditions de concurrence lors des mises à jour grâce à un nettoyage préalable complet du répertoire cible.
  - Synchronisation réactive des cartes et listes de clones dans l'interface.

### 🎨 Typographie, dimensions des widgets et documentation
- **Améliorations visuelles**:
  - Hauteur de ligne des tableaux ajustée à 34px et correction du débordement de texte dans les menus déroulants.
  - README enrichi avec guide de démarrage, instructions GUI et captures d'écran.
- **Tests**:
  - Extension de la suite de tests à 329 tests automatisés.

---

## [v0.8.0] - 2026-08-20

### 🎨 Refonte visuelle conforme aux directives macOS HIG
- **Système de design Apple natif et accessibilité**:
  - Refonte complète de l'interface graphique selon les Apple Human Interface Guidelines (HIG) : palettes de couleurs natives, hiérarchie typographique (11pt–22pt) et espacements confortables.
  - Amélioration de l'affichage des tableaux Cocoa via des correctifs d'exécution (`patch_cocoa`) : hauteur de ligne augmentée à 40px, en-têtes modernisés et typographie agrandie.
  - Agrandissement des champs de saisie, menus déroulants, commutateurs, boutons et libellés dans l'assistant et les paramètres.
  - Pieds de page d'actions transformés en barres d'outils natives macOS compactes.
  - Activation de la **Vue Liste (List View)** par défaut pour toutes les sections de gestion.

### 💾 Gestion unifiée du stockage et synchronisation automatique
- **Paramètres de stockage simplifiés**:
  - Réorganisation de la vue Paramètres (`SettingsView`) : la modification du dossier racine met à jour automatiquement tous les sous-dossiers dérivés (`clones.yaml`, `Data/`, `logs/`, `recipes/`).
  - Validation et indicateurs d'état des chemins en temps réel.

### 🌐 Support du protocole proxy HTTPS
- **Configuration réseau enrichie**:
  - Prise en charge complète des URL de proxy en `https://` dans les modèles de recettes, la CLI (`atbclone clone`, `atbclone wizard`) et l'interface graphique.

### 📦 Améliorations du packaging et extension des tests
- **Point d'entrée de module et création de DMG**:
  - Ajout de `src/atbclone/__main__.py` pour l'exécution directe via `python -m atbclone`.
  - Amélioration de `scripts/build_gui.sh` avec vérification de l'intégrité du bundle d'application et validation de la signature.
- **Tests**:
  - Suite de tests portée à 304 tests automatisés unitaires et d'intégration GUI.

---

## [v0.7.0] - 2026-08-20

### 🖥️ Application de bureau native BeeWare Toga GUI
- **Interface graphique moderne Ice-Blue**:
  - Lancement de l'application de bureau native macOS (`atbclone-gui`) basée sur BeeWare Toga.
  - Navigation par barre latérale et disposition en cartes : gestion des clones (`ClonesView`), analyse d'applications (`ProbeView`), gestion des recettes (`RecipesView`), visualiseur de journaux (`LogsView`) et paramètres (`SettingsView`).
  - Assistant visuel interactif avec support du glisser-déposer de fichiers `.app`.

### 🍏 Barre des menus système macOS et réduction en arrière-plan
- **Service de barre des menus (TrayService)**:
  - Intégration dans la barre des menus via `NSStatusBar` et `NSStatusItem` avec menu contextuel (Ouvrir, Créer un clone, Lancement rapide, Préférences, Quitter).
  - Option « Réduire dans la barre des menus » avec gestion transparente via Cocoa Selector et `NSWindowDelegate`.

### 📖 Visualiseur de notes de version multilingue intégré
- **Fenêtre dédiée aux notes de version**:
  - Accès direct aux notes de version depuis les paramètres de l'application.
  - Sélecteur dynamique parmi les 9 langues supportées avec rendu Markdown en temps réel.

### 📝 Système unifié de journalisation des opérations (Unified Logger)
- **Persistance fichier et diffusion en direct**:
  - Implémentation de `atbclone.core.logger` unifiant les journaux CLI et GUI (`~/.atbclone/logs/atbclone.log`) avec diffusion mémoire (`LogBroadcastHandler`).
  - Vue Journaux dans l'interface graphique avec flux en direct, filtrage par niveau, recherche, export et purge.

### 📦 Nouvelles recettes et couverture de tests
- **Recettes populaires**: Intégration de **Claude Desktop** (`com.anthropic.claudefordesktop`), **Telegram** (`ru.keepcoder.Telegram`), **Cursor**, etc.
- **Tests automatisés**: 299 tests unitaires et d'intégration validant l'interface et le cœur du moteur.

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
