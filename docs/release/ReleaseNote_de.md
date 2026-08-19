[English](ReleaseNote.md) | [简体中文](ReleaseNote_zh.md) | [繁體中文](ReleaseNote_zh_TW.md) | [日本語](ReleaseNote_ja.md) | [한국어](ReleaseNote_ko.md) | [Deutsch](ReleaseNote_de.md) | [Français](ReleaseNote_fr.md) | [Русский](ReleaseNote_ru.md) | [Español](ReleaseNote_es.md)

# ATBClone Versionshinweise (Release Notes)

Dieses Dokument erfasst alle wesentlichen Aktualisierungen, neuen Funktionen, Optimierungen und Fehlerbehebungen für **ATBClone**.

---

## [v0.3.0] - 2026-08-19

### 🌐 Internationalisierung & Mehrsprachigkeit (i18n)
- **Automatische Erkennung der macOS-Systemsprache**:
  - Integration des `atbclone.core.i18n`-Moduls zur automatischen Erkennung der bevorzugten Sprache über `AppleLanguages` und `AppleLocale`.
  - Dynamische Umschaltung von interaktiven Assistenten, Eingabeaufforderungen, Tabellenköpfen und Protokollen zwischen Deutsch, Englisch und Chinesisch.
  - Manuelle Sprachauswahl über die Umgebungsvariable `ATBCLONE_LANG` (z. B. `ATBCLONE_LANG=en` / `ATBCLONE_LANG=zh`).
- **Mehrsprachige Dokumentation**:
  - `Readme.md` als standardmäßiges englisches Dokument mit chinesischer Version in `Readme_zh.md`.
  - Veröffentlichung von Versionshinweisen in 9 Sprachen: Englisch, vereinfachtes Chinesisch, traditionelles Chinesisch, Japanisch, Koreanisch, Deutsch, Französisch, Russisch und Spanisch.

### 🛠️ CLI & Build-Verbesserungen
- **Assistenten-Lokalisierung**: Vollständige Lokalisierung von `atbclone wizard` inklusive benutzerdefinierter Anzeigenamen, `.icns`-Symbole und Proxy-Konfigurationen.
- **Eigenständige Binärdatei**: Neu kompiliertes `./dist/ATBCloneCli` mit Nuitka inklusive eingebetteter Wörterbücher und verbesserter Sandbox-Kompatibilität (`PYTHONNOUSERSITE=1`).
- **Umfangreiche Test-Suite**: Hinzufügen von `test_i18n.py` und erfolgreiche Ausführung aller 186 Unit-Tests.

---

## [v0.2.0] - 2026-08-18

### 🚀 Wichtige Neuerungen
- **Interaktiver Klon-Assistent (`atbclone wizard`)**:
  - Schritt-für-Schritt-Führung im Terminal mit Unterstützung für Drag & Drop von `.app`-Pfaden.
  - Automatische Erkennung und Inkrementierung von Klonnamen (z. B. `WeChat2`, `WeChat3`).
  - Unterstützung für benutzerdefinierte Anwendungsnamen und eigene `.icns`-Symbole.
  - Interaktive Einrichtung von Netzwerk-Proxys (HTTP & SOCKS5) mit Authentifizierung.
- **Intelligente App-Tiefenanalyse (`atbclone probe`)**:
  - Automatische Analyse von Mach-O-Architekturen (arm64, x86_64, Universal), Frameworks (Electron, Flutter, Chromium, Qt, Cocoa) und Sandbox-Berechtigungen (`com.apple.security.app-sandbox`).
  - Dynamische Empfehlung der optimalen Klonstrategie (`hard_clone` / `soft_clone`) für unbekannte Anwendungen und Erstellung passender Recipe-YAML-Dateien.
  - Automatische Ausführung des Analysetools in `atbclone clone`, falls kein integriertes Rezept vorhanden ist.
- **Kompilierung eigenständiger Binärdateien**:
  - Bereitstellung von `scripts/build_cli.sh` zur Erstellung nativer, abhängigkeitsfreier macOS arm64-Binärdateien (`dist/ATBCloneCli`) via Nuitka.

### ⚡ Verbesserungen & Fehlerbehebungen
- Optimierte Rechteerweiterung über native macOS `osascript`-Dialoge bei der Ausgabe in `/Applications`.
- Robuste Pfadmaskierung mit `shlex.quote` gegen Leerzeichen und Sonderzeichen.

---

## [v0.1.0] - 2026-08-17

### 🌟 Erstveröffentlichung
- **Dual-Engine-Klonarchitektur**:
  - **Hard Clone Engine**: Vollständige Duplizierung des App-Bundles, Anpassung von `Info.plist`, Isolation von `HOME` / `TMPDIR`, optionale Sandbox-Entfernung und ad-hoc Re-Signierung.
  - **Soft Clone Engine**: Schlanke Starter-Hülle für Chromium-Browser und Editoren mit automatischer Injektion von `--user-data-dir`.
- **18+ integrierte Anwendungsrezepte**:
  - Messenger: WeChat, QQ, Telegram, LINE, Slack, Discord, Skype.
  - KI-Clients: ChatGPT (Codex), Gemini, Antigravity, Antigravity IDE.
  - Browser & Entwicklung: Google Chrome, Microsoft Edge, Firefox, Arc, Cursor, VS Code, Zed.
- **Vollständige CLI-Befehle**:
  - `clone`: Erstellen von Klonen mit individuellen Namen und Proxys.
  - `list`: Tabellarische Übersicht über alle aktiven Klone.
  - `update`: Klon-Aktualisierung nach Haupt-App-Updates unter Beibehaltung aller Benutzerdaten.
  - `remove`: Sicheres Entfernen von Klonen mit optionaler Datenbereinigung.
  - `recipe`: Auflisten und Verwalten von Anwendungsrezepten.
  - `doctor`: Automatisierte Überprüfung der Systemwerkzeuge (`codesign`, `xcode-select`, `PlistBuddy`).
