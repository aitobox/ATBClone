# Kapitel 4: Häufig gestellte Fragen (FAQ), Diagnose & Feedback

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
