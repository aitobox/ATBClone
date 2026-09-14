# Глава 2: Пользовательские рецепты & Базовые параметры

Использование инструмента **App Prober** для сканирования программ и создание правил в визуальном редакторе.

---

## 📑 Содержание

- [Автоматический анализ с App Prober](#автоматический-анализ-с-app-prober)
- [Структура YAML рецепта](#структура-yaml-рецепта)
  - [1. bundle_id](#1-bundle_id)
  - [2. strategy](#2-strategy)
  - [3. strip_sandbox](#3-strip_sandbox)
  - [4. proxy](#4-proxy)

---

## 🔍 Автоматический анализ с App Prober

```bash
atbclone probe /Applications/Slack.app
```

Вывод:

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

---

## 📜 Структура YAML рецепта

```yaml
version: "1.0"
name: "Slack"
description: "Изолированная конфигурация для Slack"

bundle_id: "com.tinyspeck.slackmacgap"
strategy: "hard_clone"
strip_sandbox: true

proxy:
  type: "http"
  host: "127.0.0.1"
  port: 7890
```

* `bundle_id`: Идентификатор исходного бандла.
* `strategy`: `hard_clone` или `soft_clone`.
* `strip_sandbox`: Снятие ограничений песочницы для использования произвольных путей данных.
* `proxy`: Опциональный сетевой прокси.
