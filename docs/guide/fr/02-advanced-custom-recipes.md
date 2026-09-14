# Chapitre 2 : Recettes personnalisées & Paramètres de base

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
