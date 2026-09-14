# Kapitel 3: Funktionsweise & Erweiterte Parameter

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
