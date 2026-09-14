import os

DE_DIR = "docs/guide/de"
os.makedirs(DE_DIR, exist_ok=True)

# README.md
readme = """# 📖 ATBClone Benutzerhandbuch (Deutsche Version)

[English Version](../en/) | [簡體中文](../zh/) | [繁體中文](../zh-hant/) | [日本語](../ja/) | [한국어](../ko/) | Deutsche Version

Willkommen beim offiziellen **ATBClone Benutzerhandbuch**. Dieses Handbuch führt Sie Schritt für Schritt durch alle Funktionen zur Multi-Instanz-Ausführung und Sandbox-Isolation von macOS-Anwendungen — von grundlegenden Workflows für Einsteiger über benutzerdefinierte Rezepte bis hin zu internen Architekturanalysen und Systemdiagnosen.

---

## 🧭 Kapitel-Navigation

| Kapitel | Titel | Zielgruppe | Hauptthemen |
| :--- | :--- | :--- | :--- |
| **[Kapitel 1](01-basic-operations.md)** | **[Grundlegende Bedienung & Klon-Verwaltung](01-basic-operations.md)** | 👶 **Einsteiger / Standardnutzer** | 7-Schritte-Assistent, Starten, Datenverzeichnis direkt öffnen, **verlustfreie Synchronisation** nach Updates der Haupt-App, Tabellenansicht (**Batch-Update & Batch-Löschen**), sicheres Entfernen. |
| **[Kapitel 2](02-advanced-custom-recipes.md)** | **[Benutzerdefinierte Rezepte & Basisparameter](02-advanced-custom-recipes.md)** | ⚡ **Fortgeschrittene Nutzer** | **App Prober (Intelligenter Scanner)** zur Erkennung unbekannter Apps, visueller Rezept-Editor, **Erklärung der Basisparameter** (`bundle_id`, `strategy`, `strip_sandbox`, `proxy`). |
| **[Kapitel 3](03-under-the-hood-and-internals.md)** | **[Funktionsweise & Erweiterte Parameter](03-under-the-hood-and-internals.md)** | 🔬 **Power-User / Entwickler** | Soft- vs. Hard-Clone-Mechanismen, **Hard-Clone Kerntechnologien & Binary Wrapper Hijack**, Trennung von Logik und Daten, **Erweiterte YAML-Parameter** (`environment_injection`, `symlink_whitelist`, Pfad-Makros). |
| **[Kapitel 4](04-faq-and-troubleshooting.md)** | **[Häufig gestellte Fragen (FAQ), Diagnose & Feedback](04-faq-and-troubleshooting.md)** | 🩺 **Alle Nutzer** | Wichtige FAQs (Datensicherheit, Speicherpfade & Migration, Bann-Prävention, kein Root erforderlich), Doctor-Systemprüfung, **Klon-Details kopieren & GitHub Issues melden**. |

---

## 🌟 Warum ATBClone?

Auf macOS scheitern herkömmliche Klon-Methoden (wie einfaches Kopieren per `cp -R` oder Terminal-Aliase) häufig, da moderne Apps Benutzerpräferenzen, SQLite-Datenbanken und Keychain-Schlüsselbundelemente systemweit teilen.

ATBClone löst dies durch eine eigens entwickelte **Vierfach-Isolation (Quadruple Isolation)**:

```mermaid
graph TD
    A[ATBClone Isolations-Engine] --> B[1. Daten- & Cache-Isolation]
    A --> C[2. Visuelle & Dock-Identität]
    A --> D[3. macOS TCC-Sicherheitsberechtigungen]
    A --> E[4. Netzwerk-Proxy-Isolation]
    
    B --> B1["Eigenes $HOME & $TMPDIR, keine SQLite-Sperrkonflikte"]
    C --> C1["Separates Dock-Icon, eigener App-Name, Spotlight-Suche"]
    D --> D1["Unabhängige Kamera-, Mikrofon- und Festplattenzugriffe"]
    E --> E1["Eigener HTTP/SOCKS5-Proxy pro Klon (Anti-Fingerprinting)"]
```

1. **📦 Daten- & Cache-Isolation**: Jeder Klon erhält ein eigenes isoliertes Benutzerverzeichnis (`$HOME`) oder `--user-data-dir`. Mehrere Konten können parallel laufen, ohne lokale Datenbanken zu blockieren.
2. **🎨 Visuelle & Dock-Identität**: Klone besitzen individuelle Namen und Icons. Sie erscheinen separat in Spotlight, Launchpad und im macOS Dock.
3. **🛡️ Systemberechtigungen (TCC) Isolation**: Durch modifizierte `CFBundleIdentifier`-Werte behandelt macOS Klone als eigenständige Apps mit separaten TCC-Berechtigungen (Kamera, Mikrofon etc.).
4. **🌐 Netzwerk-Proxy-Isolation**: Leiten Sie den Datenverkehr bestimmter Klone über dedizierte HTTP- oder SOCKS5-Proxys, ohne das Host-Netzwerk zu beeinträchtigen.

---

## 📚 Wichtige Begriffe & Glossar

* **Haupt-App (Host App)**: Das Originalprogramm auf Ihrem Mac (meist in `/Applications`).
* **Klon-App (Clone App)**: Die von ATBClone erzeugte Instanz (Standard: `~/ATBClone/Apps`).
* **Hard Clone (Physische Kopie & Wrapper Hijack)**: Dupliziert das Bundle, ändert die Bundle-ID, schleust Umgebungsvariablen ein und signiert neu. Ideal für Messenger wie WeChat, Telegram, Slack und Discord.
* **Soft Clone (Launcher-Wrapper)**: Erstellt einen schlanken Starter mit individuellen Parametern (`--user-data-dir`). Perfekt für Browser und Editoren (Cursor, VS Code, Chrome).
* **Rezept (Recipe)**: YAML-Konfigurationsdatei mit Klon- und Startanweisungen.
* **Isoliertes Datenverzeichnis**: Der Speicherort für Chats, Caches und Datenbanken (Standard: `~/ATBClone/Data/<KlonName>`).

---

## 🚀 Schnellstart

1. **Herunterladen & Installieren**: Laden Sie `ATBClone-*.dmg` von [GitHub Releases](https://github.com/aitobox/ATBClone/releases) herunter und ziehen Sie `ATBClone.app` in `/Applications`.
2. **Starten**: Öffnen Sie ATBClone aus dem Launchpad.
3. **Assistent starten**: Klicken Sie oben rechts auf **"+ Neuer Klon"**.
4. **7 Schritte ausführen**: App wählen ➔ Rezept prüfen ➔ Namen vergeben ➔ Pfade bestätigen ➔ **"Jetzt klonen"**.
5. **Loslegen**: Klicken Sie auf **"Starten"** oder öffnen Sie den Klon via Spotlight!

---

> [!NOTE]
> **Mehrsprachigkeit**: Diese Dokumentation ist in 9 Sprachen verfügbar. Nutzen Sie das Sprachauswahlmenü in der oberen Leiste.
"""

# 01-basic-operations.md
ch01 = """# Kapitel 1: Grundlegende Bedienung & Klon-Verwaltung

In diesem Kapitel erfahren Sie, wie Sie mithilfe des 7-Schritte-Assistenten Ihre erste Klon-Anwendung erstellen und im Alltag verwalten (Starten, Datenordner öffnen, Updates synchronisieren und sicher löschen).

---

## 📑 Inhaltsverzeichnis

- [Klon-Anwendung erstellen (7-Schritte-Assistent)](#klon-anwendung-erstellen-7-schritte-assistent)
  - [Schritt 1: Zielanwendung auswählen](#schritt-1-zielanwendung-auswahlen)
  - [Schritt 2: Rezept und Strategie prüfen](#schritt-2-rezept-und-strategie-prufen)
  - [Schritt 3: Identität und Sprache festlegen](#schritt-3-identitat-und-sprache-festlegen)
  - [Schritt 4: Installationspfad bestätigen](#schritt-4-installationspfad-bestatigen)
  - [Schritt 5: Datenverzeichnis festlegen](#schritt-5-datenverzeichnis-festlegen)
  - [Schritt 6: Netzwerk-Proxy einrichten (Optional)](#schritt-6-netzwerk-proxy-einrichten-optional)
  - [Schritt 7: Bestätigen und Klonen](#schritt-7-bestatigen-und-klonen)
- [Klon-Anwendungen verwalten](#klon-anwendungen-verwalten)
  - [Klon-App starten](#klon-app-starten)
  - [Datenordner mit einem Klick öffnen](#datenordner-mit-einem-klick-offnen)
  - [Klon-Konfiguration bearbeiten](#klon-konfiguration-bearbeiten)
  - [Verlustfreie Synchronisation nach App-Updates](#verlustfreie-synchronisation-nach-app-updates)
  - [Batch-Operationen in der Tabellenansicht](#batch-operationen-in-der-tabellenansicht)
  - [Sicheres Löschen (Daten behalten vs. vollständig entfernen)](#sicheres-loschen-daten-behalten-vs-vollstandig-entfernen)

---

## 🪄 Klon-Anwendung erstellen (7-Schritte-Assistent)

Klicken Sie im Dashboard auf **"+ Neuer Klon"**, um den Assistenten zu öffnen.

```text
+-------------------------------------------------------------+
|  🧙 Neuer Klon - Schritt 1 von 7                            |
|                                                             |
|  Zielanwendung (.app) auswählen                             |
|  [/Applications/WeChat.app                   ] [ Durchsuchen]|
|                                                             |
|  [ Abbrechen ]                                 [ Weiter > ] |
+-------------------------------------------------------------+
```

### Schritt 1: Zielanwendung auswählen
1. Klicken Sie auf **"Durchsuchen..."** (öffnet standardmäßig `/Applications`).
2. Wählen Sie das App-Bundle (z. B. `WeChat.app`, `Telegram.app`, `Cursor.app`).
3. Klicken Sie auf **"Weiter >"**.

> [!TIP]
> Sie können auch den absoluten Pfad einer beliebigen App auf externen Laufwerken manuell eingeben.

---

### Schritt 2: Rezept und Strategie prüfen
ATBClone analysiert die ausgewählte Anwendung automatisch:

* **Integriertes Rezept**: Bei über 33 bekannten Apps wird automatisch die beste Strategie gewählt (`Hard Clone` für Messenger, `Soft Clone` für Browser/Editoren).
* **Smart Prober**: Bei unbekannten Apps scannt der Scanner Mach-O-Binärdateien und Sandbox-Entitlements dynamisch.
* **Strategie-Auswahl**:
  * `hard_clone`: Vollständige Bundle-Kopie mit modifizierter ID und Wrapper-Injektion.
  * `soft_clone`: Schlanker Launcher, der isolierte Parameter übergibt.

---

### Schritt 3: Identität und Sprache festlegen
1. **Klon-Name**: Vergeben Sie einen aussagekräftigen Namen (z. B. `WeChat-Arbeit`, `Telegram-Zweitkonto`).
2. **Bundle Identifier**: Wird automatisch generiert (z. B. `com.tencent.xinWeChat.atbclone.work`).
3. **App-Icon**: Ziehen Sie optional ein beliebiges `.png` oder `.icns` auf das Icon-Feld, um es anzupassen.
4. **Sprache überschreiben**: Legen Sie fest, in welcher Oberflächensprache der Klon starten soll.

---

### Schritt 4: Installationspfad bestätigen
Speicherort des Klon-Bundles (Standard: `~/ATBClone/Apps/<KlonName>.app`).

---

### Schritt 5: Datenverzeichnis festlegen
Speicherort für Chats, Caches und Datenbanken (Standard: `~/ATBClone/Data/<KlonName>`).
* **Architektur-Vorteil**: Die vollständige Trennung von Programmcode (`Apps/`) und Daten (`Data/`) garantiert, dass Ihre Daten bei Programm-Updates niemals angetastet werden.

---

### Schritt 6: Netzwerk-Proxy einrichten (Optional)
Konfigurieren Sie bei Bedarf einen separaten `HTTP`- oder `SOCKS5`-Proxy (z. B. `127.0.0.1:7890`) inklusive Authentifizierung.

---

### Schritt 7: Bestätigen und Klonen
Überprüfen Sie die Zusammenfassung und klicken Sie auf **"Jetzt klonen"**. Sobald der Fortschrittsbalken 100 % erreicht, ist Ihr Klon einsatzbereit!

---

## 🖥️ Klon-Anwendungen verwalten

### Klon-App starten
* Direkt im Dashboard auf **"Starten"** klicken.
* Per Spotlight (`Cmd + Space`) nach dem Klon-Namen suchen.
* Die `.app` an Ihr macOS Dock anheften.

### Datenordner mit einem Klick öffnen
Klicken Sie auf das Ordner-Symbol einer Klon-Karte, um das Verzeichnis `~/ATBClone/Data/<KlonName>` direkt im Finder zu öffnen.

### Verlustfreie Synchronisation nach App-Updates
Wenn die offizielle Original-App aktualisiert wird:
1. Klicken Sie auf der Klon-Karte auf **"Aktualisieren"**.
2. ATBClone synchronisiert die Binärdateien auf den neuesten Stand — **Ihre Chatverläufe und Einstellungen bleiben zu 100 % erhalten**.

### Batch-Operationen in der Tabellenansicht
In der Tabellenansicht können Sie mehrere Klone markieren und mit einem Klick **stapelweise aktualisieren** oder **stapelweise löschen**.

### Sicheres Löschen (Daten behalten vs. vollständig entfernen)
Beim Löschen haben Sie die Wahl:
* **Nur App-Bundle löschen**: Entfernt die Programmdatei, behält aber Chats und Daten für eine spätere Wiederherstellung.
* **Vollständig entfernen**: Löscht sowohl die App als auch das zugehörige Datenverzeichnis.
"""

# 02-advanced-custom-recipes.md
ch02 = """# Kapitel 2: Benutzerdefinierte Rezepte & Basisparameter

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
"""

# 03-under-the-hood-and-internals.md
ch03 = """# Kapitel 3: Funktionsweise & Erweiterte Parameter

Erfahren Sie mehr über die Low-Level-Architektur von ATBClone, Binary Wrapper Hijacking, Code-Resigning und fortgeschrittene YAML-Makros.

---

## 📑 Inhaltsverzeichnis

- [Architektur-Vergleich: Soft vs. Hard Clone](#architektur-vergleich-soft-vs-hard-clone)
- [Die 3 Kerntechnologien des Hard Clone](#die-3-kerntechnologien-des-hard-clone)
  - [1. Mutation der Bundle-ID](#1-mutation-der-bundle-id)
  - [2. Binary Wrapper Hijack & Umgebungsvariablen](#2-binary-wrapper-hijack--umgebungsvariablen)
  - [3. Sandbox-Stripping und Ad-hoc-Codesign](#3-sandbox-stripping-und-ad-hoc-codesign)
- [Trennung von Daten und Programmlogik](#trennung-von-daten-und-programmlogik)
- [Erweiterte Rezept-Parameter](#erweiterte-rezept-parameter)
  - [1. environment_injection](#1-environment_injection)
  - [2. symlink_whitelist](#2-symlink_whitelist)
  - [3. launch_arguments](#3-launch_arguments)
  - [4. plist_overrides](#4-plist_overrides)
  - [5. Dynamische Pfad-Makros](#5-dynamische-pfad-makros)
- [Vollständiges Beispiel](#vollstandiges-beispiel)

---

## ⚡ Die 3 Kerntechnologien des Hard Clone

### 1. Mutation der Bundle-ID
`Info.plist` erhält eine neue, einzigartige Kennung (`CFBundleIdentifier`). macOS behandelt den Klon daraufhin als völlig separate Anwendung mit eigenen TCC-Rechten.

### 2. Binary Wrapper Hijack & Umgebungsvariablen
1. Die echte Binärdatei `Contents/MacOS/<App>` wird zu `<App>.real` umbenannt.
2. Ein POSIX-Shellskript tritt an ihre Stelle und biegt Systemvariablen um:
   * `export HOME="<Datenverzeichnis>"`
   * `export TMPDIR="<Datenverzeichnis>/tmp"`
   * `export XDG_DATA_HOME="<Datenverzeichnis>/Library/Application Support"`
3. Anschließend wird die `.real`-Binärdatei gestartet.

### 3. Sandbox-Stripping und Ad-hoc-Codesign
Die App-Sandbox-Berechtigung wird aus den Entitlements entfernt und das Bundle mit `codesign -f -s -` lokal neu signiert.

---

## ⚙️ Erweiterte Rezept-Parameter

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

* **Dynamische Makros**: `{DATA_DIR}` (Klon-Datenpfad), `{CLONE_NAME}` (Name des Klons), `{BUNDLE_ID}` (neue Bundle-ID), `{HOST_APP}` (Pfad zur Original-App).
"""

# 04-faq-and-troubleshooting.md
ch04 = """# Kapitel 4: Häufig gestellte Fragen (FAQ), Diagnose & Feedback

Hier finden Sie Antworten auf häufige Fragen, Sicherheitshinweise und Anleitungen zur Systemdiagnose sowie Fehlerberichterstattung auf GitHub.

---

## 📑 Inhaltsverzeichnis

- [Häufig gestellte Fragen (FAQ)](#haufig-gestellte-fragen-faq)
  - [1. Beeinflusst ein Klon die Daten der Original-App?](#1-beeinflusst-ein-klon-die-daten-der-original-app)
  - [2. Wo werden Klon-Daten gespeichert? Wie funktioniert ein Backup?](#2-wo-werden-klon-daten-gespeichert-wie-funktioniert-ein-backup)
  - [3. Besteht die Gefahr einer Kontosperre (Bann)?](#3-besteht-die-gefahr-einer-kontosperre-bann)
  - [4. Werden Administratorrechte (Root/Sudo) benötigt?](#4-werden-administratorrechte-rootsudo-benotigt)
  - [5. Was tun bei macOS Gatekeeper-Warnungen ("beschädigt")?](#5-was-tun-bei-macos-gatekeeper-warnungen-beschadigt)
  - [6. Wie kann das Icon eines Klons geändert werden?](#6-wie-kann-das-icon-eines-klons-geandert-werden)
- [Systemdiagnose mit dem Doctor-Tool](#systemdiagnose-mit-dem-doctor-tool)
- [Fehler melden via GitHub Issues](#fehler-melden-via-github-issues)
- [Community & Support](#community--support)

---

## ❓ Häufig gestellte Fragen (FAQ)

### 1. Beeinflusst ein Klon die Daten der Original-App?
**Nein, keineswegs.** ATBClone isoliert alle Daten vollständig unter `~/ATBClone/Data/<KlonName>`. Die Originaldaten bleiben völlig unberührt.

### 2. Wo werden Klon-Daten gespeichert? Wie funktioniert ein Backup?
Alle Daten liegen in `~/ATBClone/Data/<KlonName>`. Für ein Backup genügt es, diesen Ordner auf ein externes Medium zu kopieren.

### 3. Besteht die Gefahr einer Kontosperre (Bann)?
ATBClone nutzt nicht-invasive Umgebungsumleitungen. Es verändert keine Speicherinhalte oder Netzwerkprotokolle. Die Ausführung entspricht der offiziellen App. Durch Nutzung individueller Proxys können Sie zusätzlich IP-Verknüpfungen vermeiden.

### 4. Werden Administratorrechte (Root/Sudo) benötigt?
**Nein.** Alle Operationen finden ausschließlich im Benutzerkontext statt.

### 5. Was tun bei macOS Gatekeeper-Warnungen ("beschädigt")?
Führen Sie im Terminal folgenden Befehl aus:
```bash
xattr -cr ~/ATBClone/Apps/<KlonName>.app
```

---

## 🩺 Systemdiagnose mit dem Doctor-Tool

```bash
atbclone doctor
```

Überprüft macOS-Kompatibilität, Command Line Tools, Schreibrechte und Rezept-Integrität.

---

## 🐞 Fehler melden via GitHub Issues

1. Öffnen Sie in ATBClone die **"Klon-Details"** der betroffenen Instanz.
2. Klicken Sie auf **"Diagnosedaten kopieren"**.
3. Erstellen Sie einen Issue auf [GitHub Issues](https://github.com/aitobox/ATBClone/issues) und fügen Sie den Report ein.
"""

for fn, content in [("README.md", readme), ("01-basic-operations.md", ch01), ("02-advanced-custom-recipes.md", ch02), ("03-under-the-hood-and-internals.md", ch03), ("04-faq-and-troubleshooting.md", ch04)]:
    with open(f"{DE_DIR}/{fn}", "w", encoding="utf-8") as f:
        f.write(content)
    print(f"✓ Created de/{fn}")
