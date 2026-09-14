# Chapitre 1 : Opérations de base & Gestion des clones

![Démo de l'interface ATBClone](assets/images/screenshot-20260821-110121.png)

Ce chapitre vous guide dans la création de votre premier clone à l'aide de l'assistant interactif en 7 étapes, puis détaille les opérations quotidiennes (lancement, accès aux données, synchronisation des mises à jour et suppression sécurisée).

---

## 📑 Sommaire

- [Créer une application clonée (Assistant en 7 étapes)](#creer-une-application-clonee-assistant-en-7-etapes)
  - [Étape 1 : Sélectionner l'application cible](#etape-1-selectionner-lapplication-cible)
  - [Étape 2 : Vérifier la recette et la stratégie](#etape-2-verifier-la-recette-et-la-strategie)
  - [Étape 3 : Définir l'identité et la langue](#etape-3-definir-lidentite-et-la-langue)
  - [Étape 4 : Confirmer l'emplacement d'installation](#etape-4-confirmer-lemplacement-dinstallation)
  - [Étape 5 : Configurer le répertoire de données](#etape-5-configurer-le-repertoire-de-donnees)
  - [Étape 6 : Configurer un proxy réseau (Optionnel)](#etape-6-configurer-un-proxy-reseau-optionnel)
  - [Étape 7 : Confirmer et lancer le clonage](#etape-7-confirmer-et-lancer-le-clonage)
- [Gérer vos applications clonées](#gerer-vos-applications-clonees)
  - [Lancer un clone](#lancer-un-clone)
  - [Ouvrir directement le dossier de données](#ouvrir-directement-le-dossier-de-donnees)
  - [Synchronisation sans perte lors des mises à jour](#synchronisation-sans-perte-lors-des-mises-a-jour)
  - [Opérations par lot dans la vue tableau](#operations-par-lot-dans-la-vue-tableau)
  - [Suppression sécurisée (Conserver vs Purger les données)](#suppression-securisee-conserver-vs-purger-les-donnees)

---

## 🪄 Créer une application clonée (Assistant en 7 étapes)

Cliquez sur **"+ Nouveau clone"** sur le tableau de bord pour ouvrir l'assistant.

### Étape 1 : Sélectionner l'application cible
Sélectionnez le fichier `.app` à cloner (ex. `/Applications/WeChat.app` ou `Cursor.app`).

### Étape 2 : Vérifier la recette et la stratégie
ATBClone analyse automatiquement l'application et choisit la meilleure stratégie (`Hard Clone` ou `Soft Clone`).

### Étape 3 : Définir l'identité et la langue
Définissez un nom clair (ex. `WeChat-Pro`), personnalisez l'icône si souhaité, et fixez la langue d'interface.

### Étape 4 : Confirmer l'emplacement d'installation
Par défaut : `~/ATBClone/Apps/<NomDuClone>.app`.

### Étape 5 : Configurer le répertoire de données
Par défaut : `~/ATBClone/Data/<NomDuClone>`.
* **Architecture découplée** : La séparation stricte entre l'exécutable (`Apps/`) et les données utilisateur (`Data/`) garantit que vos fichiers ne sont jamais supprimés lors d'une mise à jour de l'app.

### Étape 6 : Configurer un proxy réseau (Optionnel)
Configurez un proxy `HTTP` ou `SOCKS5` dédié si nécessaire.

### Étape 7 : Confirmer et lancer le clonage
Vérifiez le récapitulatif et cliquez sur **"Cloner maintenant"**.

---

## 🖥️ Gérer vos applications clonées

* **Lancement** : Depuis l'interface ATBClone, via la recherche Spotlight (`Cmd + Espace`), ou directement depuis le Dock.
* **Accès aux données** : Cliquez sur l'icône de dossier d'une carte pour ouvrir le répertoire de données dans le Finder.
* **Mises à jour synchronisées** : Cliquez sur **"Mettre à jour"** après une mise à jour de l'application hôte. Le clone est mis à jour sans aucune perte de données.
* **Suppression sécurisée** : Choisissez entre supprimer uniquement l'application ou effacer également le dossier de données.
