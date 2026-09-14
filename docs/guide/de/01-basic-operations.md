# Kapitel 1: Grundlegende Bedienung & Klon-Verwaltung

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
