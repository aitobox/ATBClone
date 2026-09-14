# Chapitre 3 : Fonctionnement interne & Paramètres avancés

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
