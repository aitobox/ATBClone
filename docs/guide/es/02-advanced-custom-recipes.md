# Capítulo 2: Recetas personalizadas & Parámetros básicos

Uso de **App Prober** para auditar aplicaciones y creación de reglas con el editor visual de recetas.

---

## 📑 Índice

- [Diagnóstico automático con App Prober](#diagnostico-automatico-con-app-prober)
- [Estructura YAML de una receta](#estructura-yaml-de-una-receta)
  - [1. bundle_id](#1-bundle_id)
  - [2. strategy](#2-strategy)
  - [3. strip_sandbox](#3-strip_sandbox)
  - [4. proxy](#4-proxy)

---

## 🔍 Diagnóstico automático con App Prober

```bash
atbclone probe /Applications/Slack.app
```

Salida:

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

## 📜 Estructura YAML de una receta

```yaml
version: "1.0"
name: "Slack"
description: "Configuración multi-instancia aislada para Slack"

bundle_id: "com.tinyspeck.slackmacgap"
strategy: "hard_clone"
strip_sandbox: true

proxy:
  type: "http"
  host: "127.0.0.1"
  port: 7890
```

* `bundle_id`: Identificador del bundle original.
* `strategy`: `hard_clone` o `soft_clone`.
* `strip_sandbox`: Elimina la restricción de sandbox para permitir carpetas de datos personalizadas.
* `proxy`: Enrutamiento por proxy opcional.
