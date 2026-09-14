# Kapitel 2: Benutzerdefinierte Rezepte & Basisparameter

ATBClone liefert für die gängigsten Apps fertige Rezepte mit. Möchten Sie weniger verbreitete Tools oder Inhouse-Software klonen, nutzen Sie den **App Prober** und den visuellen Rezept-Editor.

---

## 📑 Inhaltsverzeichnis

- [Automatische Diagnose mit App Prober](#automatische-diagnose-mit-app-prober)
  - [One-Click-Analyse in der GUI](#one-click-analyse-in-der-gui)
  - [Terminal-Diagnose via CLI](#terminal-diagnose-via-cli)
- [Der visuelle Rezept-Editor](#der-visuelle-rezept-editor)
- [YAML-Rezeptstruktur & Basisparameter](#yaml-rezeptstruktur--basisparameter)
  - [1. bundle_id (Bundle-Kennung)](#1-bundle_id-bundle-kennung)
  - [2. strategy (Klon-Strategie)](#2-strategy-klon-strategie)
  - [3. strip_sandbox (Sandbox-Entfernung)](#3-strip_sandbox-sandbox-entfernung)
  - [4. proxy (Netzwerk-Proxy)](#4-proxy-netzwerk-proxy)
- [Rezepte testen und speichern](#rezepte-testen-und-speichern)

---

## 🔍 Automatische Diagnose mit App Prober

Der integrierte Scanner analysiert Binärdateien, Frameworks und Berechtigungen in Sekundenschnelle.

```bash
atbclone probe /Applications/Slack.app
```

Ausgabe:

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

* **Electron / Chromium**: Kann mit `soft_clone` betrieben werden. Sollen Benachrichtigungen und Dock-Status komplett unabhängig sein, empfiehlt sich `hard_clone` mit `strip_sandbox: true`.
* **Native Cocoa / Sandbox-Apps**: Erfordern stets `hard_clone` und `strip_sandbox: true`.

---

## 📜 YAML-Rezeptstruktur & Basisparameter

```yaml
version: "1.0"
name: "Slack"
description: "Isolierte Multi-Instanz-Konfiguration für Slack"

bundle_id: "com.tinyspeck.slackmacgap"
strategy: "hard_clone"
strip_sandbox: true

proxy:
  type: "http"
  host: "127.0.0.1"
  port: 7890
```

### 1. bundle_id
Der Bundle Identifier des Originals (z. B. `com.tinyspeck.slackmacgap`).

### 2. strategy
* `hard_clone`: Dupliziert Binärdateien und injiziert Wrapper.
* `soft_clone`: Ruft das Original mit modifizierten Datenpfad-Parametern auf.

### 3. strip_sandbox
Entfernt das Flag `com.apple.security.app-sandbox` aus Binärdateien und Signaturen, sodass die App ohne Beschränkung auf `~/Library/Containers/` beliebige Pfade nutzen kann.

### 4. proxy
Leitet den Datenverkehr des Klons über HTTP, HTTPS oder SOCKS5 weiter.
