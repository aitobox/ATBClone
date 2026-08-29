[English](ReleaseNote.md) | [简体中文](ReleaseNote_zh.md) | [繁體中文](ReleaseNote_zh_TW.md) | [日本語](ReleaseNote_ja.md) | [한국어](ReleaseNote_ko.md) | [Deutsch](ReleaseNote_de.md) | [Français](ReleaseNote_fr.md) | [Русский](ReleaseNote_ru.md) | [Español](ReleaseNote_es.md)

# ATBClone Versionshinweise (Release Notes)

Dieses Dokument erfasst alle wesentlichen Aktualisierungen, neuen Funktionen, Optimierungen und Fehlerbehebungen für **ATBClone**.

---

## [v1.1.0] - 2026-08-29

### 🤖 Vollständige Unterstützung von AI-Clients & LLM-Tools
- **Claude Desktop & Claude Code Multi-Instanz**:
  - Automatische Injektion von `CLAUDE_CONFIG_DIR` sowie Replikation und Isolation von `~/.claude` und `~/.claude.json`.
  - Beibehaltung von `CFBundleName` zur Vermeidung von Lookup-Abstürzen von Claude-Helper-Prozessen.
- **Google Antigravity & Gemini-Ökosystem**:
  - Injektion von `GEMINI_HOME` und `ANTIGRAVITY_HOME` zur sauberen Isolation von `~/.gemini`.
- **OpenAI ChatGPT & Codex CLI**:
  - Injektion von `CODEX_HOME` und Replikation von `~/.codex` für gleichzeitige Mehrkontennutzung.

### 🔑 Automatische macOS Keychain-Verknüpfung
- **Zertifikats- und Schlüsselbundschutz**:
  - Automatische Symlink-Erstellung auf `Library/Keychains` bei `HOME`-Umleitung verhindert Schlüsselbundfehler und Abstürze.

### 🛡️ AMFI-Entitlements-Bereinigung & Hardened Runtime-Stabilität
- **Optimierung für macOS Sonoma & Sequoia**:
  - Automatische Bereinigung restriktiver Team-Entitlements (`com.apple.application-identifier` etc.) beim Ad-Hoc-Signieren.
  - Verhindert das `SIGKILL`-Beenden von Hilfsprozessen durch Apple Mobile File Integrity (AMFI).

### 🚀 Universelles ProcessSingleton-Mach-O-Patching
- **Multi-Instanz für Electron & AI-Apps**:
  - Verallgemeinerung des ProcessSingleton-Binärpatches und Injektion von `--user-data-dir` für AI-Client-Rezepte.

### 🧪 Test-Suite
- **Erweiterte Abdeckung**:
  - Test-Suite auf 453 automatisierte Tests ausgebaut (100 % bestanden).

---

## [v1.0.2] - 2026-08-26

### 🛡️ Optimiertes Sandbox-Stripping & Verbesserte Hard-Clone-Stabilität
- **Universelles Sandbox-Stripping für Hard Clones (`strip_sandbox: true`)**:
  - Standardmäßige Aktivierung von Sandbox-Stripping für Hard-Clone-Rezepte zur Vermeidung von Rechtekonflikten und Deadlocks modifizierter Mach-O-Pakete.
  - Optimierung des WeChat-Hard-Clone-Rezepts mit garantierter Initialisierung der Laufzeitverzeichnisse (`Caches`, `Containers`, `Preferences`).

### 📚 Rezept-Bereinigung & Dokumentation von Architektur-Einschränkungen
- **Rezept-Aktualisierungen**:
  - Entfernung des experimentellen WeCom-Rezepts aufgrund vorgelagerter CEF-IPC-Einschränkungen und Aufnahme detaillierter Erläuterungen in den Fehlerbehebungsleitfaden.
  - Aktualisierung der Best Practices zur Erstellung benutzerdefinierter Rezepte.

### 🧪 Test-Suite
- **Vollständige Abdeckung**:
  - Alle 443 automatisierten Tests erfolgreich bestanden.

---

## [v1.0.1] - 2026-08-26

### 🎨 Apple Design HIG-Konformität & Visuelle Optimierungen
- **Einhaltung der macOS Human Interface Guidelines**:
  - Umfassendes Apple Design HIG-Audit für alle Ansichten und Dialoge.
  - Bereinigung von Emoji-Dekorationen zugunsten nativer SF Pro-Typografie und klarer visueller Hierarchien.
  - Verbesserte Seitenleistennavigation mit nativer Cocoa-Auswahlhervorhebung.
  - Kontrastverhältnisse für Hell- und Dunkelmodus optimiert (erfüllt WCAG 2.1 AA).
  - Verbesserte Leerzustandsanzeigen, Kartenschatten, Fenster-Ziehbereiche und einheitliche Abstände.

### 📜 Chronologisch umgekehrte Protokollanzeige & Layout-Anpassungen
- **Echtzeit-Diagnose (`LogsView`)**:
  - Protokolleinträge werden jetzt in umgekehrter Reihenfolge (neueste Einträge ganz oben) angezeigt.
  - Feste Breitenbeschränkungen für „Aktualisieren“- und „Durchsuchen“-Schaltflächen entfernt, um Textkürzungen in allen Sprachen zu verhindern.

### 🛡️ Klon-Engine-Stabilität & Fehlerbehandlung bei erweiterten Attributen
- **Schreibberechtigungen & `xattr`-Fehlertoleranz**:
  - Stellt sicher, dass Klon-Pakete vor der Mach-O-Bearbeitung und Signierung Schreibrechte (`chmod -R u+w`) besitzen.
  - Fehlertolerante Bereinigung erweiterter Attribute (`xattr -cr`) verhindert Abbrüche auf schreibgeschützten System-Snapshots.

### 🧪 Test-Suite
- **Erweiterte Abdeckung**:
  - Test-Suite auf 443 automatisierte Tests ausgebaut.

---

## [v1.0.0] - 2026-08-24

### 🚀 Offizieller Meilenstein: ATBClone 1.0.0
- **Produktionsreife macOS-App-Klonlösung**:
  - ATBClone erreicht Version 1.0.0 und bietet ein ausgereiftes, hochperformantes Ökosystem für Multi-Instanz-Anwendungen unter macOS (Apple Silicon & Intel).
  - Umfassende Dual-Engine-Architektur: speicherschonende Soft Clones und vollständig isolierte Hard Clones mit nativer Mach-O-Manipulation und Sandbox-Virtualisierung.

### 🧬 Tiefgreifendes CEF-Patching & WeCom-Unterstützung
- **Unterstützung komplexer Hybrid-Frameworks**:
  - Spezielles CEF-Binär-Patching für komplexe Enterprise-Anwendungen wie WeCom (企业微信).
  - Behebt den `GpuDataManager`-FATAL-Absturz in Helper-Prozessen und bereinigt verschachtelte Helper-Bundle-IDs (`.helper.atbclone.X`).
  - Integration von Symlink-Whitelists und Vermeidung interner Sandbox-Konflikte für stabilen Dauerbetrieb.

### 🛡️ Vollständige rekursive Neusignierung & Singleton-Patching
- **Rekursive Signierung aller eingebetteten Komponenten**:
  - `HardCloneEngine` signiert alle verschachtelten Binärdateien, Frameworks, Helper-Apps, XPC-Dienste und dylibs tiefgreifend neu.
  - Erhält JIT- und Hardened-Runtime-Entitlements ohne Verschmutzung der Signaturstrukturen.
- **Framework-ProcessSingleton-Patch**:
  - Neues Rezept-Attribut `patch_framework_singleton` zur Deaktivierung von Prozess-Singleton-Sperren direkt in der Mach-O-Binärdatei.

### 📋 Erweiterte Detailansicht & Zwischenablagen-Integration
- **Diagnose-Export & Textauswahl**:
  - Überarbeitung von `CloneDetailWindow` mit nativen Cocoa-Mehrzeilen-Textansichten und direkter `NSPasteboard`-Anbindung.

### 🧪 Test-Suite & Qualitätssicherung
- **Umfassende Abdeckung**:
  - Ausbau der automatisierten Test-Suite auf 441 Tests mit 100 % Erfolgsquote.

---

## [v0.9.9] - 2026-08-24

### 📋 Textauswahl & „Alle Details kopieren“ im Klon-Detailfenster
- **Interaktive Textkopie & Export**:
  - Aktivierung des nativen Textauswahlmodus (`setSelectable_`) in `CloneDetailWindow` zum direkten Kopieren beliebiger Pfade, Bundle-IDs oder Parameter.
  - Neue Schaltfläche „Alle Details kopieren“ in der Fußzeile zum Exportieren des vollständigen Diagnoseberichts in die Zwischenablage.

### 🎨 macOS-natives UI-Design & Abstandsoptimierungen
- **Design-Token & Karten-Layout**:
  - Überarbeitung der Farb-Tokens in `Theme` für den Hell- und Dunkelmodus (`BG_APP`, `BG_CARD`, `BG_HOVER`, `BORDER`, `TEXT_PRIMARY`, `TEXT_MUTED`, `ACCENT`).
  - Harmonisierte Eckenradien, Innenabstände und Widget-Größen in allen Ansichten.

### 📖 Umfassendes mehrsprachiges Benutzerhandbuch (`docs/guide/`)
- **Offizielle Handbücher**:
  - Bereitstellung detaillierter Benutzerhandbücher auf Englisch (`docs/guide/en/`) und Chinesisch (`docs/guide/zh-cn/`).
  - Deckt Kapitel 1 (Grundfunktionen), Kapitel 2 (Benutzerdefinierte Rezepte), Kapitel 3 (Architektur & Interna) und Kapitel 4 (FAQ & Diagnose) ab.

### 🧪 Test-Suite
- **Erweiterte Abdeckung**:
  - Test-Suite auf 431 automatisierte Tests erweitert.

---

## [v0.9.8] - 2026-08-24

### 🔒 Entitlements-Extraktion & Stabilität der Hard-Clone-Engine
- **Erhaltung der Sandbox-Berechtigungen (Entitlements)**:
  - Verbesserung der `HardCloneEngine`, um native Entitlements direkt aus der Quell-Mach-O-Binärdatei via `codesign -d --entitlements :-` zu extrahieren.
  - Zusätzliche Sicherheitsüberprüfungen verhindern leere oder beschädigte Berechtigungsdateien beim erneuten Signieren.
- **Strikte Sandbox-Container-Isolierung in integrierten Rezepten**:
  - Standardisierung von `strip_sandbox: false` für alle Hard-Clone-Rezepte (u. a. WeChat, QQ, WeWork, WPS Office, LINE, Skype, CapCut).
  - Gewährleistet getrennte Container-Verzeichnisse (`~/Library/Containers/<new_bundle_id>`) zur Vermeidung von Datenkonflikten zwischen Instanzen.

### 📚 Dokumentation & Schemasynchronisation
- **Aktualisierung der Projektdokumentation**:
  - Angleichung der englischen (`README.md`) und chinesischen (`README_zh.md`) Dokumentation an aktuelle `app_type`- und `strip_sandbox`-Spezifikationen.

### 🧪 Test-Suite
- **Umfassende Qualitätssicherung**:
  - Alle 428 Tests der Test-Suite erfolgreich validiert.

---

## [v0.9.7] - 2026-08-24

### 🔍 Intelligente Erkennung der App-Architektur & Sprachparameter-Anpassung
- **Erkennung des Runtime-Frameworks (`app_type`)**:
  - Einführung des Feldes `app_type` (`electron`, `chromium`, `qt`, `flutter`, `native_cocoa`, `java`, `unknown`) im Recipe-Modell.
  - `AppProber.detect_app_type` analysiert Frameworks, dylibs und JVM-Strukturen zur automatischen Architekturbestimmung.
  - Standardisierung aller 34 integrierten Rezepte mit expliziten `app_type`- und `strip_sandbox`-Attributen.
- **Framework-spezifische Sprachparameter-Injektion**:
  - Dynamische Injektion passender Sprachflags je nach Framework (`--lang=` für Chromium/Electron, `-AppleLanguages` für Native Cocoa, `-user.language` für Java).

### 🧬 Mach-O-Binärargument-Analyse & Validierung
- **Automatische Erkennung von Datenpfad-Argumenten**:
  - `BinaryArgumentProber` durchsucht Mach-O-Binärdateien nach unterstützten CLI-Flags (`--user-data-dir`, `--profile-directory`, `--datadir` etc.) für unbekannte Anwendungen.
- **Validierung von Startargumenten**:
  - `LaunchArgumentValidator` filtert inkompatible oder fehlerhafte Flags vor der Klonerstellung heraus.

### 📋 Inspektion & Kopieren injizierter Parameter
- **Parameter-Inspektion (`CloneInspector`)**:
  - `CloneInspector` extrahiert injizierte Umgebungsvariablen, Proxyeinstellungen, Sprachüberschreibungen und Startargumente aus Klon-Bundles.
  - Neue Karte „Injizierte Parameter“ im `CloneDetailWindow` mit praktischem Kopier-Button.

### ⚙️ Erweiterte Rezepteinstellungen im GUI-Editor
- **Erweiterter Rezeptideitor (`RecipeEditWindow`)**:
  - Konfiguration von Anwendungs-Framework-Typen, Startargumenten, Proxyregeln, Umgebungsvariablen und Symlink-Whitelists.

### 🧪 Test-Suite
- **Umfassende Abdeckung**:
  - Ausbau auf 428 automatisierte Tests.

---

## [v0.9.6] - 2026-08-24

### 🖱️ Natives Cocoa-Tabellenkopf-Sortieren
- **Interaktive Spaltensortierung**:
  - Implementierung von Klick-Sortierung über `NSTableViewHeaderView` in `CloneListView` und `RecipeListView`.
  - Unterstützt aufsteigende und absteigende Sortierung mit Sortierpfeilen im Header und Synchronisation mit der Symbolleiste.
  - Automatische Beibehaltung der Zeilenauswahl bei Sortieroperationen.

### 📦 Mehrfachauswahl & Stapelverarbeitung
- **Klon-Stapelverwaltung (`CloneListView`)**:
  - Unterstützung für Mehrfachzeilenauswahl (`multiple_select=True`) mit dynamischer Schaltflächenaktivierung.
  - Gleichzeitiges Aktualisieren oder Löschen mehrerer Klone inklusive Datenlöschungsoption.
- **Regellöschung mit Schutzmechanismen (`RecipeListView`)**:
  - Mehrfachauswahl und Stapellöschung für benutzerdefinierte Regeln.
  - Kontextbezogene Bestätigungsdialoge zum Schutz schreibgeschützter integrierter Regeln.
  - Busy-Sperre zur Verhinderung gleichzeitiger Operationen während der Stapelverarbeitung.

### 🛠️ Xcode Command Line Tools Diagnose & Doctor View
- **Überprüfung der Build-Werkzeuge**:
  - Automatische Überprüfung der Xcode-Befehlszeilenwerkzeuge (`xcode-select -p`, `codesign`, `lipo`, `otool`, `install_name_tool`) im `DoctorService`.

### ℹ️ Standard-macOS-Infodialog-Metadaten
- **Korrektur des Cocoa-Über-Dialogs**:
  - Saubere Übergabe von Versionsnummern und Metadaten an `orderFrontStandardAboutPanelWithOptions:`.

### 🧪 Test-Suite
- **Umfassende Abdeckung**:
  - Ausbau auf 369 automatisierte Tests.

---

## [v0.9.5] - 2026-08-23

### 📝 Neue `WrappingLabel`-Komponente & Mehrzeiliger Textumbruch
- **Automatischer Textumbruch für macOS**:
  - Implementierung der `WrappingLabel`-Komponente zur Behebung von einzeiligen Layout-Einschränkungen unter Cocoa Toga.
  - Dynamische Höhenberechnung (`cellSizeForBounds_`) basierend auf der zugewiesenen Breite verhindert das unschöne Verbreitern von Fenstern bei langen Pfaden oder Argumenten.
- **Optimierung von Diagnoseberichten & Detailansichten**:
  - Anwendung von `WrappingLabel` in `ProbeView` (Prober-Analyseberichte, Kompatibilitätsprüfung), `CloneDetailWindow` und `WizardWindow`.

### 🧪 Test-Hermetizität & Zustandsisolierung
- **Dynamische Pfadauflösung**:
  - Überarbeitung von `StateManager` und `RecipeLoader` zur dynamischen Auswertung von Konfigurationspfaden zur Laufzeit, wodurch Unit-Tests vollständig isoliert von lokalen Benutzerzuständen laufen.
- **Test-Suite**:
  - Ausbau auf 347 automatisierte Tests.

---

## [v0.9.4] - 2026-08-23

### 📁 Migration des Standard-Datenverzeichnisses nach `~/ATBClone`
- **Intuitive Benutzerdatenverwaltung**:
  - Verlagerung des Basisverzeichnisses von `~/.atbclone` in das sichtbare Benutzerverzeichnis `~/ATBClone` (`~/ATBClone/Data/`, `~/ATBClone/clones.yaml`).
  - Erleichtert die Verwaltung und Sicherung von Klondaten über Finder und Terminal.

### 🏷️ Zuverlässige Durchsetzung benutzerdefinierter Anzeigenamen
- **Bereinigung lokalisierter Strings**:
  - Entfernung von `LSHasLocalizedDisplayName` und Bereinigung von `InfoPlist.strings` in `SoftCloneEngine` und `HardCloneEngine`.
  - Stellt sicher, dass Finder, Dock, Spotlight und Aktivitätsanzeige stets den benutzerdefinierten Klonnamen anzeigen.

### 🔄 Automatische LaunchServices-Registrierung
- **Sofortige Metadaten-Aktualisierung**:
  - Automatische Ausführung von `lsregister -f` nach Klon-Operationen zur sofortigen Aktualisierung von Symbol- und Bundle-Caches.

### 📦 Dokumentation & Test-Suite
- **Vollständige Anpassung**:
  - Anpassung der Dokumentation, GUI-Einstellungen und aller 341 Tests an das neue Verzeichnis.

---

## [v0.9.3] - 2026-08-21

### 🛡️ Erweiterte App-Prüfung & Vorab-Validierung im Assistenten
- **Vorzeitige Erkennung von iOS-Wrapper-Apps**:
  - Aktualisierung von `AppInspector.inspect_app`, um `UIDeviceFamily` und `LSRequiresIPhoneOS` direkt beim Auswählen oder Drag-and-Drop zu analysieren.
  - Im GUI-Assistenten (`WizardWindow`) wird bei der Auswahl einer nicht unterstützten iOS-Wrapper-App sofort ein lokalisierter Warndialog angezeigt und das Eingabefeld zurückgesetzt.

### 🍏 Sauberer macOS-Beendigungsprozess & Cocoa-Freigabe
- **Verhinderung von Beendigungsabstürzen**:
  - Optimierung von `TrayService.disable()` und `ATBCloneApp.exit_app()` zum sicheren Entbinden von Cocoa-Status-Item-Targets und Selektoren beim Beenden.
  - Saubere Beendigung der Cocoa-Ereignisschleife (`NSApp.terminate_` / `os._exit(0)`), wodurch Abstürze beim Beenden über das Tray-Menü oder `Cmd+Q` behoben wurden.

### 📦 Test-Suite
- **Erweiterung der Testabdeckung**:
  - Ausbau auf 341 automatisierte Tests.

---

## [v0.9.2] - 2026-08-21

### 🍏 Dynamisches Ausblenden des macOS Dock-Icons & Tray-Optimierung
- **Automatische Dock-Icon-Verwaltung**:
  - Dynamische Steuerung der Dock-Sichtbarkeit über AppKit-Aktivierungsrichtlinien (`NSApplicationActivationPolicy`).
  - Beim Minimieren oder Schließen in die Menüleiste wird das Dock-Icon vollständig ausgeblendet (`NSApplicationActivationPolicyAccessory`).
  - Beim Wiederherstellen aus der Menüleiste erscheint das Dock-Icon nahtlos wieder (`NSApplicationActivationPolicyRegular`) mit sofortigem Fensterfokus.
- **Dock-Reopen-Handler**:
  - Implementierung von `applicationShouldHandleReopen:hasVisibleWindows:` im `AppDelegate`, um das Hauptfenster beim Klick auf das Dock-Symbol zuverlässig wiederherzustellen.

### 📦 Ressourcenoptimierung & Test-Suite
- **Dateigrößenoptimierung**:
  - Optimierung und Kompression der Icon-Ressourcen (`logo.icns`, `logo.png`).
- **Test-Suite**:
  - Erweiterung auf 338 automatisierte Tests.

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
