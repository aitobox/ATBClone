[English](ReleaseNote.md) | [简体中文](ReleaseNote_zh.md) | [繁體中文](ReleaseNote_zh_TW.md) | [日本語](ReleaseNote_ja.md) | [한국어](ReleaseNote_ko.md) | [Deutsch](ReleaseNote_de.md) | [Français](ReleaseNote_fr.md) | [Русский](ReleaseNote_ru.md) | [Español](ReleaseNote_es.md)

# ATBClone Versionshinweise (Release Notes)

Dieses Dokument erfasst alle wesentlichen Aktualisierungen, neuen Funktionen, Optimierungen und Fehlerbehebungen für **ATBClone**.

---

## [v0.9.1] - 2026-08-21

### 🛡️ Erkennung und Blockierung von iOS-on-Mac-Apps
- **Sichere Behandlung nicht unterstützter Architekturen**:
  - Erweiterung von `AppProber`, `SoftCloneEngine` und `HardCloneEngine` zur präzisen Erkennung von iOS/iPadOS-Wrapper-Apps auf Apple Silicon (Apps mit `Wrapper/` oder `UIDeviceFamily` / `LSRequiresIPhoneOS=True`).
  - Sicheres Abweisen von Klonversuchen für iOS-Wrapper-Apps in CLI (`atbclone clone`, `atbclone wizard`) und GUI mit verständlicher Fehlermeldung (`error_ios_wrapper_unsupported`), um fehlerhafte Bundles zu verhindern.

### 🎨 Automatische Icon-Generierung in Build-Skripten
- **Dynamische `.icns`-Erstellung**:
  - Optimierung von `scripts/build_gui.sh` zur automatischen Umwandlung von PNG-Dateien in `.icns`-Symboldateien mittels `sips` und `iconutil` während der DMG-Erstellung.
  - Erweiterte Ressourcenvalidierung im Build-Prozess.

### 🌐 Lokalisierung & Test-Suite
- **Mehrsprachige Fehlermeldungen**:
  - Vollständige Übersetzung der iOS-Wrapper-Warnung in alle 9 unterstützten Sprachen.
- **Test-Suite**:
  - Ausbau auf 336 automatisierte Tests.

---

## [v0.9.0] - 2026-08-21

### 🌐 Unabhängige Sprach- und Gebietsschema-Isolation pro Klon
- **Benutzerdefinierte Spracheinstellungen (`--language` / `--locale`)**:
  - Unterstützung für die Ausführung von Klonen in dedizierten Sprachen, unabhängig von der Sprache des macOS-Wirtssystems oder der Hauptanwendung.
  - Erweiterung von `atbclone clone` und `atbclone wizard` um `--language` / `--locale` sowie grafische Sprachauswahl im GUI-Assistenten und Bearbeitungsdialog.
  - Automatische Injektion von `AppleLanguages` und `AppleLocale` in Start-Wrapper und Binärdateien.
  - Neues Modul `atbclone.core.locale` zur BCP-47-Sprachcode- und Regionsanalyse.

### 🆔 Eindeutige Bundle-ID-Generierung bei Mehrfachklonen
- **Kollisionsfreie Bundle-IDs**:
  - `AppInspector.find_next_bundle_id` zur dynamischen Erkennung bestehender Klone und automatischen Vergabe kollisionsfreier IDs (`com.vendor.app.atb1`, `atb2` usw.).

### 🍏 Menüleisten-Tray-Aktivierung und Fenster-Lebenszyklus
- **Zuverlässige Fensterwiederherstellung**:
  - Optimierte Reaktivierung, Fokusübernahme und Deminiaturisierung beim Öffnen aus dem Statusmenü (`TrayService`).
  - Abfangen des Fensterschließens (`Cmd+W` / rote Schließen-Schaltfläche) bei aktiviertem „In Menüleiste minimieren“.
  - Verbesserte Handhabung von Klickereignissen im Menüleistensymbol.

### ⚡ Klon-Aktualisierung und Bereinigung des Zielverzeichnisses
- **Atomare Aktualisierungsprozesse**:
  - Beseitigung von Race-Conditions bei Klon-Updates durch gründliche Vorbereinigung des Zielverzeichnisses.
  - Verbesserte reaktive Synchronisierung von Klon-Karten in der Benutzeroberfläche.

### 🎨 Typografie, Widget-Größen und Dokumentation
- **Visueller Feinschliff**:
  - Optimierung der Tabellenzeilenhöhe (34px) und Beseitigung von Textüberläufen in Dropdown-Menüs.
  - Erweiterung der README um Download-Hinweise, GUI-Anleitung und Screenshots.
- **Test-Suite**:
  - Ausbau auf 329 automatisierte Tests.

---

## [v0.8.0] - 2026-08-20

### 🎨 macOS Human Interface Guidelines (HIG) Visuelle Neugestaltung
- **Natives Apple-Designsystem & Verbesserte Barrierefreiheit**:
  - Vollständige Überarbeitung des GUI-Designs gemäß Apple Human Interface Guidelines (HIG): Standardisierte Farbpaletten, Systemschrift-Hierarchie (11pt–22pt) und großzügige Abstände.
  - Optimierung der Cocoa-Tabellendarstellung via Runtime-Patch (`patch_cocoa`): Erhöhte Zeilenhöhe (40px), modernisierte Tabellenköpfe und vergrößerte Schriftarten für optimale Lesbarkeit.
  - Vergrößerung von Eingabefeldern, Dropdowns, Schaltern, Schaltflächen und Beschriftungen in Assistenten, Einstellungen und Bearbeitungsdialogen.
  - Umgestaltung der Tabellenaktionsleisten im nativen macOS-Toolbar-Stil.
  - Standardmäßige Aktivierung der **Listenansicht (List View)** für alle Verwaltungsbereiche.

### 💾 Einheitliche Speicherverwaltung mit automatischer Pfadsynchronisierung
- **Optimierte Speichereinstellungen**:
  - Neugestaltung der `SettingsView`: Die Änderung des Hauptspeicherverzeichnisses aktualisiert automatisch alle abgeleiteten Unterverzeichnisse (`clones.yaml`, `Data/`, `logs/`, `recipes/`).
  - Echtzeit-Gültigkeitsprüfung für Verzeichnispfade.

### 🌐 Unterstützung für HTTPS-Proxy-Protokolle
- **Erweiterte Netzwerkkonfiguration**:
  - Vollständige Unterstützung für `https://`-Proxy-Schemas in Recipe-Modellen, CLI (`atbclone clone`, `atbclone wizard`) und GUI.

### 📦 Paketierung & Test-Suite-Erweiterung
- **Modul-Einstiegspunkt & DMG-Prüfung**:
  - Hinzugefügter Einstiegspunkt `src/atbclone/__main__.py` für `python -m atbclone`.
  - Erweiterung des Build-Skripts `scripts/build_gui.sh` um Bundle-Integritäts- und Signaturprüfungen.
- **Test-Suite**:
  - Erweiterung auf 304 automatisierte Unit- und GUI-Integrationstests.

---

## [v0.7.0] - 2026-08-20

### 🖥️ Native BeeWare Toga Desktop-GUI-Anwendung
- **Moderne grafische Ice-Blue-Benutzeroberfläche**:
  - Einführung der vollwertigen nativen macOS-Desktop-Anwendung (`atbclone-gui`) auf Basis von BeeWare Toga.
  - Flüssige Seitenleistennavigation und Karten-Rasterlayout: Klonverwaltung (`ClonesView`), App-Analyse (`ProbeView`), Rezeptverwaltung (`RecipesView`), Protokollanzeige (`LogsView`) und Einstellungen (`SettingsView`).
  - Interaktiver visueller Assistent mit Drag-and-Drop-Unterstützung für `.app`-Pakete.

### 🍏 Natives macOS Menüleisten-Tray & Fenster-Minimierung
- **Menüleisten-Tray-Dienst (TrayService)**:
  - Integration von Menüleistensymbolen via `NSStatusBar` und `NSStatusItem` mit Schnellmenü (Hauptfenster öffnen, Klon erstellen, Schnellstart, Einstellungen, Beenden).
  - Option „In Menüleiste minimieren“ mit nahtloser Cocoa-Selector-Registrierung und `NSWindowDelegate`-Unterstützung.

### 📖 Mehrsprachiger Release-Notes-Betrachter in der GUI
- **Integriertes Versionshinweise-Fenster**:
  - Neuer Release-Notes-Dialog, direkt aufrufbar über die Einstellungen.
  - Dynamisches Dropdown-Menü für alle 9 Sprachen mit Echtzeit-Markdown-Darstellung.

### 📝 Einheitliches Betriebsprotokollsystem (Unified Logger)
- **Dateipersistenz & Live-Stream**:
  - Einführung von `atbclone.core.logger` zur Vereinheitlichung von CLI- und GUI-Protokollen (`~/.atbclone/logs/atbclone.log`) mit Live-Broadcast-Stream (`LogBroadcastHandler`).
  - GUI-Protokollansicht mit Live-Aktualisierung, Level-Filterung, Suche, Export und Protokollbereinigung.

### 📦 Rezept-Erweiterungen & Test-Suite
- **Neue Rezepte**: Offizielle Rezepte für **Claude Desktop** (`com.anthropic.claudefordesktop`), **Telegram** (`ru.keepcoder.Telegram`), **Cursor** und weitere Anwendungen.
- **Umfassende Tests**: Erweiterung der Test-Suite auf 299 automatisierte Tests für GUI- und Backend-Funktionen.

---

## [v0.6.0] - 2026-08-19

### 📂 Unterstützung benutzerdefinierter Datenverzeichnisse
- **Anpassbarer Datenspeicherort (`--data-dir`)**:
  - Neuer Parameter `--data-dir` für `atbclone clone` zur flexiblen Festlegung des Datenspeicherorts (z. B. auf externen SSDs oder spezifischen Arbeitsverzeichnissen).
  - Integration der Verzeichniskonfiguration in den interaktiven Assistenten (`atbclone wizard`).
  - Erweiterung der Recipe-Modelle und Klon-Engines zur dynamischen Auflösung von Datenverzeichnisvariablen.

### 🗑️ Verbesserte Klon-Deinstallation & Datenbereinigung (`atbclone remove`)
- **Sichere Steuerungsoptionen für Datenbereinigung**:
  - Option `--purge-data` für `atbclone remove` zum automatisierten, vollständigen Löschen von App-Bundles und zugehörigen Datenverzeichnissen.
  - Option `--keep-data` zum Beibehalten isolierter Benutzerdaten bei der Deinstallation.
  - Interaktive Bestätigungsdialoge mit klarer Auswahl zwischen Datenbeibehaltung und Datenbereinigung.
  - Optimierte Diagnose und Fehlerbehandlung für verwaiste Verzeichnisse und Berechtigungskonflikte.

### 🆔 Standardisierung der Bundle-ID & Mehrsprachigkeit
- **Standardisierte Bundle-ID-Generierung**:
  - Neuer `AppInspector.generate_bundle_id`-Standard für konsistente Bundle-IDs über `clone`, `wizard` und `update`.
- **Lokalisierung**:
  - Vollständige Übersetzung aller neuen Dialoge, Abfragen und Protokollmeldungen in alle 9 unterstützten Sprachen.
- **Test-Suite**:
  - Erweiterung auf 213 automatisierte Tests zur Überprüfung benutzerdefinierter Pfade und Löschroutinen.

---

## [v0.5.0] - 2026-08-19

### 🔐 Apple Code-Signing & Notarisierungs-Pipeline
- **Hardened Runtime & Offizielle Signierung**:
  - Vollständige Integration von Apple Developer ID Application Signaturen mit Hardened Runtime (`--options runtime`), Zeitstempeln und benutzerdefinierten JIT-Berechtigungen (`scripts/entitlements.plist`).
  - Neues Notarisierungsskript `scripts/notarize.sh` zur automatischen Einreichung via `xcrun notarytool` unter Verwendung von Keychain-Profilen (`--keychain-profile`).
  - Erweiterung von `scripts/build_cli.sh` und `scripts/release.sh` um `--sign-identity`, `--skip-sign` und `--notarize` mit automatischem Ad-hoc-Fallback.

### 🚀 Chromium Hard-Clone & Übergabe von Startargumenten
- **Unterstützung von Startargumenten in `HardCloneEngine`**:
  - Erweiterung der `HardCloneEngine` zur dynamischen Injektion von Argumenten wie `--user-data-dir={{ATB_DATA_DIR}}` in Start-Wrapper.
  - Upgrade der integrierten Rezepte für **Google Chrome**, **Microsoft Edge** und **Arc Browser** auf die `hard_clone`-Strategie für vollständige App-Bundle-Duplikation und eigenständige Dock-/Finder-Identitäten.
- **CLI-Strategieüberschreibung**:
  - Neuer Parameter `--strategy` für `atbclone clone` (`--strategy hard_clone` / `--strategy soft_clone`).

### ⚡ Prozessweiterleitung & Test-Suite-Erweiterung
- **Prozessverwaltung**: Optimierung des `SoftCloneEngine`-Wrappers auf standardmäßige `exec "$@"`-Weiterleitung.
- **Umfassende Tests**: Erweiterung der Test-Suite auf 199 automatisierte Tests für Signierung, Notarisierung und Klonstrategien.

---

## [v0.4.0] - 2026-08-19

### 🌐 Umfassende 9-Sprachen-Lokalisierung für CLI und Dokumentation
- **Vollständige CLI-Internationalisierung in 9 Sprachen**:
  - Erweiterung des `atbclone.core.i18n`-Moduls um vollständige Lokalisierung für Englisch, vereinfachtes Chinesisch, traditionelles Chinesisch, Japanisch, Koreanisch, Deutsch, Französisch, Russisch und Spanisch.
  - Alle CLI-Befehle (`wizard`, `clone`, `probe`, `list`, `recipe`, `doctor`, `update`, `remove`, `version`) unterstützen lokalisierte Dialoge, Tabellen und Fehlermeldungen.
- **Standardisierte mehrsprachige Release Notes**:
  - Bereitstellung und Pflege von Versionshinweisen in 9 Sprachen im Verzeichnis `docs/release/`.

### 🔄 Automatisierte Release- und Versionssynchronisations-Pipeline
- **Automatische Validierung der 9-Sprachen-Release-Notes**:
  - Optimierung von `scripts/manage_version.py` und `scripts/release.sh` zur automatischen Überprüfung der Versionsabschnitte in allen 9 Release-Notes-Dateien vor der Tag-Erstellung.
  - Neuer Validierungsbefehl `--check-notes` zur Vermeidung fehlender Versionsdokumentation.
- **Erweitertes Test-Suite**:
  - Erweiterung der automatisierten Tests auf 191 Testfälle mit vollständiger Abdeckung der Lokalisierung und des Release-Workflows.

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
