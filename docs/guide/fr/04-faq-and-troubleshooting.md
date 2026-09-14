# Chapitre 4 : FAQ, Diagnostic système & Support

Réponses aux questions courantes, conseils de sécurité et instructions pour signaler un bug sur GitHub.

---

## 📑 Sommaire

- [Foire aux questions (FAQ)](#foire-aux-questions-faq)
  - [1. Un clone affecte-t-il les données de l'application hôte ?](#1-un-clone-affecte-t-il-les-donnees-de-lapplication-hote-)
  - [2. Où sont stockées les données ? Comment faire une sauvegarde ?](#2-ou-sont-stockees-les-donnees--comment-faire-une-sauvegarde-)
  - [3. Y a-t-il un risque de bannissement de compte ?](#3-y-a-t-il-un-risque-de-bannissement-de-compte-)
  - [4. Des droits administrateur (Root/Sudo) sont-ils requis ?](#4-des-droits-administrateur-rootsudo-sont-ils-requis-)
  - [5. Que faire face aux avertissements Gatekeeper ("application endommagée") ?](#5-que-faire-face-aux-avertissements-gatekeeper-application-endommagee-)
- [Diagnostic avec l'outil Doctor](#diagnostic-avec-loutil-doctor)
- [Signaler un problème sur GitHub](#signaler-un-probleme-sur-github)

---

## ❓ Foire aux questions (FAQ)

### 1. Un clone affecte-t-il les données de l'application hôte ?
**Non, absolument pas.** ATBClone isole l'ensemble des données dans `~/ATBClone/Data/<NomDuClone>`. Les données originales ne sont jamais touchées.

### 2. Où sont stockées les données ? Comment faire une sauvegarde ?
Toutes les données sont dans `~/ATBClone/Data/<NomDuClone>`. Il suffit de copier ce dossier pour transférer vos données vers un autre Mac.

### 3. Y a-t-il un risque de bannissement de compte ?
ATBClone repose sur une redirection d'environnement non invasive et n'altère ni la mémoire ni les protocoles réseau. Du point de vue système, l'application s'exécute normalement. L'utilisation d'un proxy dédié permet en outre de masquer l'adresse IP partagée.

### 4. Des droits administrateur (Root/Sudo) sont-ils requis ?
**Non.** Tout fonctionne dans l'espace utilisateur sans modifier les fichiers système.

### 5. Que faire face aux avertissements Gatekeeper ("application endommagée") ?
Exécutez la commande suivante dans le Terminal :
```bash
xattr -cr ~/ATBClone/Apps/<NomDuClone>.app
```

---

## 🩺 Diagnostic avec l'outil Doctor

```bash
atbclone doctor
```

Vérifie la compatibilité macOS, la présence des outils de commande Xcode et les droits d'écriture.

---

## 🐞 Signaler un problème sur GitHub

1. Dans ATBClone, ouvrez les **"Détails du clone"**.
2. Cliquez sur **"Copier les informations de diagnostic"**.
3. Créez un rapport sur [GitHub Issues](https://github.com/aitobox/ATBClone/issues) et collez le contenu.
