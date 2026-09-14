import os

ES_DIR = "docs/guide/es"
os.makedirs(ES_DIR, exist_ok=True)

readme = """# 📖 Manual de Usuario de ATBClone (Versión en español)

[English Version](../en/) | [簡體中文](../zh/) | [繁體中文](../zh-hant/) | [日本語](../ja/) | [한국어](../ko/) | [Deutsch](../de/) | [Français](../fr/) | Versión en español

Bienvenido al **Manual Oficial de Usuario de ATBClone**. Esta guía le acompañará paso a paso en el dominio de las capacidades de ejecución multi-instancia y aislamiento en sandbox para aplicaciones de macOS, desde operaciones básicas hasta diagnósticos y arquitectura interna.

---

## 🧭 Navegación por capítulos

| Capítulo | Título | Audiencia | Temas principales |
| :--- | :--- | :--- | :--- |
| **[Capítulo 1](01-basic-operations.md)** | **[Operaciones básicas & Gestión de clones](01-basic-operations.md)** | 👶 **Principiantes / Todos** | Asistente interactivo en 7 pasos, lanzamiento, acceso directo a la carpeta de datos, **actualizaciones sincronizadas sin pérdida de datos**, vista de tabla (**actualización y eliminación por lotes**), desinstalación segura. |
| **[Capítulo 2](02-advanced-custom-recipes.md)** | **[Recetas personalizadas & Parámetros básicos](02-advanced-custom-recipes.md)** | ⚡ **Usuarios intermedios** | Uso de **App Prober (Sonda inteligente)** para escanear apps no listadas, editor visual de recetas, **parámetros esenciales** (`bundle_id`, `strategy`, `strip_sandbox`, `proxy`). |
| **[Capítulo 3](03-under-the-hood-and-internals.md)** | **[Funcionamiento interno & Parámetros avanzados](03-under-the-hood-and-internals.md)** | 🔬 **Avanzados / Desarrolladores** | Mecanismos de Soft vs Hard Clone, **pilares de Hard Clone y secuestro de wrapper binario (Wrapper Hijack)**, arquitectura desacoplada de datos y lógica, **parámetros YAML avanzados** (`environment_injection`, `symlink_whitelist`, macros dinámicas). |
| **[Capítulo 4](04-faq-and-troubleshooting.md)** | **[Preguntas frecuentes (FAQ), Diagnóstico & Soporte](04-faq-and-troubleshooting.md)** | 🩺 **Todos los usuarios** | Preguntas frecuentes (seguridad de datos, rutas de almacenamiento y migración, prevención de bloqueos, sin necesidad de permisos root), diagnóstico con Doctor, **extracción de detalles de clones y reporte de Issues en GitHub**. |

---

## 🌟 ¿Por qué elegir ATBClone?

En macOS, los métodos tradicionales de clonación (como simplemente copiar `.app` con `cp -R` o crear alias en la Terminal) fallan constantemente porque las aplicaciones modernas comparten preferencias, bases de datos y elementos del llavero a nivel del sistema.

ATBClone resuelve esto ofreciendo un **Aislamiento Cuádruple (Quadruple Isolation)**:

```mermaid
graph TD
    A[Motor de Aislamiento ATBClone] --> B[1. Aislamiento de datos & caché]
    A --> C[2. Identidad visual & Dock independiente]
    A --> D[3. Permisos de seguridad macOS TCC]
    A --> E[4. Aislamiento de red mediante proxy]
    
    B --> B1["$HOME y $TMPDIR independientes, cero bloqueos en SQLite"]
    C --> C1["Icono de Dock independiente, nombre personalizado, soporte Spotlight"]
    D --> D1["Permisos de cámara, micrófono y disco gestionados por separado"]
    E --> E1["Enrutamiento de proxy HTTP/SOCKS5 dedicado por clon"]
```

1. **📦 Aislamiento de datos y caché**: Cada clon opera con su propio `$HOME` o `--user-data-dir`. Múltiples cuentas pueden coexistir sin colisión de bases de datos.
2. **🎨 Identidad visual y Dock**: Cada clon tiene su propio nombre e icono en Spotlight, Launchpad y el Dock.
3. **🛡️ Aislamiento de permisos (TCC)**: Al contar con un `CFBundleIdentifier` único, macOS gestiona los permisos de privacidad de forma aislada.
4. **🌐 Tráfico de red por proxy**: Posibilidad de asignar un proxy HTTP o SOCKS5 dedicado a cada clon sin alterar la red del sistema anfitrión.

---

## 📚 Glosario y conceptos clave

* **Aplicación anfitriona (Host App)**: La aplicación original instalada en su Mac (generalmente en `/Applications`).
* **Aplicación clonada (Clone App)**: La instancia generada por ATBClone (por defecto en `~/ATBClone/Apps`).
* **Hard Clone (Duplicación física y secuestro de wrapper)**: Duplica el bundle, modifica el Bundle ID, inyecta scripts de entorno y refirma. Ideal para apps de mensajería (WeChat, Telegram, Discord, Slack).
* **Soft Clone (Lanzador wrapper)**: Crea un lanzador ligero que pasa parámetros de datos aislados (`--user-data-dir`). Ideal para navegadores y editores (Cursor, VS Code, Chrome).
* **Receta (Recipe)**: Archivo YAML con las instrucciones de aislamiento y arranque.
* **Directorio de datos aislado**: Carpeta donde se guardan chats, cachés y ajustes (`~/ATBClone/Data/<NombreClon>`).
"""

ch01 = """# Capítulo 1: Operaciones básicas & Gestión de clones

Aprenda a crear su primer clon paso a paso con el asistente interactivo en 7 pasos y descubra las funciones de gestión cotidiana.

---

## 📑 Índice

- [Crear una aplicación clonada (Asistente en 7 pasos)](#crear-una-aplicacion-clonada-asistente-en-7-pasos)
  - [Paso 1: Seleccionar la aplicación de destino](#paso-1-seleccionar-la-aplicacion-de-destino)
  - [Paso 2: Comprobar la receta y la estrategia](#paso-2-comprobar-la-receta-y-la-estrategia)
  - [Paso 3: Identidad y personalización de idioma](#paso-3-identidad-y-personalizacion-de-idioma)
  - [Paso 4: Confirmar la ruta de instalación](#paso-4-confirmar-la-ruta-de-instalacion)
  - [Paso 5: Configurar el directorio de datos](#paso-5-configurar-el-directorio-de-datos)
  - [Paso 6: Configurar proxy de red (Opcional)](#paso-6-configurar-proxy-de-red-opcional)
  - [Paso 7: Confirmar y clonar](#paso-7-confirmar-y-clonar)
- [Gestión de aplicaciones clonadas](#gestion-de-aplicaciones-clonadas)
  - [Iniciar un clon](#iniciar-un-clon)
  - [Abrir directamente la carpeta de datos](#abrir-directamente-la-carpeta-de-datos)
  - [Actualizaciones sincronizadas sin pérdida de datos](#actualizaciones-sincronizadas-sin-perdida-de-datos)
  - [Operaciones por lotes en la vista de tabla](#operaciones-por-lotes-en-la-vista-de-tabla)
  - [Eliminación segura (Conservar vs Purgar datos)](#eliminacion-segura-conservar-vs-purgar-datos)

---

## 🪄 Crear una aplicación clonada (Asistente en 7 pasos)

Pulse en **"+ Nuevo clon"** en el panel de control para iniciar el asistente.

### Paso 1: Seleccionar la aplicación de destino
Seleccione el paquete `.app` que desea clonar (por defecto en `/Applications`).

### Paso 2: Comprobar la receta y la estrategia
ATBClone analiza la app y selecciona automáticamente entre `Hard Clone` o `Soft Clone`.

### Paso 3: Identidad y personalización de idioma
Asigne un nombre representativo (ej. `WeChat-Trabajo`), cambie el icono si lo desea y fije el idioma de la interfaz.

### Paso 4: Confirmar la ruta de instalación
Ruta predeterminada: `~/ATBClone/Apps/<NombreClon>.app`.

### Paso 5: Configurar el directorio de datos
Ruta predeterminada: `~/ATBClone/Data/<NombreClon>`.
* **Arquitectura desacoplada**: La separación estricta entre el ejecutable (`Apps/`) y los datos (`Data/`) asegura que sus chats y ajustes jamás se pierdan al actualizar la app.

### Paso 6: Configurar proxy de red (Opcional)
Configure un proxy `HTTP` o `SOCKS5` si necesita aislar el tráfico de red.

### Paso 7: Confirmar y clonar
Revise la configuración y pulse en **"Clonar ahora"**.

---

## 🖥️ Gestión de aplicaciones clonadas

* **Lanzamiento**: Desde ATBClone, mediante Spotlight (`Cmd + Espacio`) o desde el Dock.
* **Acceso a datos**: Pulse en el icono de carpeta de cualquier tarjeta para abrir su carpeta en Finder.
* **Actualización sin pérdidas**: Pulse en **"Actualizar"** tras actualizar la aplicación original en su Mac.
* **Eliminación segura**: Elija entre eliminar solo el ejecutable o borrar también los datos asociados.
"""

ch02 = """# Capítulo 2: Recetas personalizadas & Parámetros básicos

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
"""

ch03 = """# Capítulo 3: Funcionamiento interno & Parámetros avanzados

Mecanismos internos de ATBClone, secuestro de wrapper binario y macros dinámicas.

---

## 📑 Índice

- [Comparación: Soft vs Hard Clone](#comparacion-soft-vs-hard-clone)
- [Los 3 pilares tecnológicos de Hard Clone](#los-3-pilares-tecnologicos-de-hard-clone)
  - [1. Mutación del Bundle ID](#1-mutacion-del-bundle-id)
  - [2. Secuestro de wrapper binario (Wrapper Hijack)](#2-secuestro-de-wrapper-binario-wrapper-hijack)
  - [3. Eliminación de sandbox y refirma ad-hoc](#3-eliminacion-de-sandbox-y-refirma-ad-hoc)
- [Parámetros YAML avanzados](#parametros-yaml-avanzados)

---

## ⚡ Los 3 pilares tecnológicos de Hard Clone

### 1. Mutación del Bundle ID
`Info.plist` recibe un `CFBundleIdentifier` único para que macOS lo trate como una aplicación independiente.

### 2. Secuestro de wrapper binario (Wrapper Hijack)
1. El ejecutable real se renombra a `<App>.real`.
2. Un script shell POSIX ocupa su lugar redefiniendo las variables de entorno:
   * `export HOME="<RutaDeDatos>"`
   * `export TMPDIR="<RutaDeDatos>/tmp"`
   * `export XDG_DATA_HOME="<RutaDeDatos>/Library/Application Support"`
3. El script ejecuta a continuación el binario `.real`.

### 3. Eliminación de sandbox y refirma ad-hoc
Se elimina el permiso `com.apple.security.app-sandbox` y se firma localmente con `codesign -f -s -`.

---

## ⚙️ Parámetros YAML avanzados

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

* Macros disponibles: `{DATA_DIR}`, `{CLONE_NAME}`, `{BUNDLE_ID}`, `{HOST_APP}`.
"""

ch04 = """# Capítulo 4: Preguntas frecuentes (FAQ), Diagnóstico & Soporte

Respuestas a preguntas habituales, consejos de seguridad y reporte de errores en GitHub.

---

## 📑 Índice

- [Preguntas frecuentes (FAQ)](#preguntas-frecuentes-faq)
  - [1. ¿Afecta un clon a los datos de la aplicación original?](#1-afecta-un-clon-a-los-datos-de-la-aplicacion-original)
  - [2. ¿Dónde se guardan los datos? ¿Cómo hacer una copia de seguridad?](#2-donde-se-guardan-los-datos-como-hacer-una-copia-de-seguridad)
  - [3. ¿Existe riesgo de baneo o suspensión de cuenta?](#3-existe-riesgo-de-baneo-o-suspension-de-cuenta)
  - [4. ¿Se requieren permisos de administrador (Root/Sudo)?](#4-se-requieren-permisos-de-administrador-rootsudo)
  - [5. ¿Qué hacer ante advertencias de Gatekeeper ("dañado")?](#5-que-hacer-ante-advertencias-de-gatekeeper-danado)
- [Diagnóstico del sistema con Doctor](#diagnostico-del-sistema-con-doctor)
- [Notificar incidencias en GitHub](#notificar-incidencias-en-github)

---

## ❓ Preguntas frecuentes (FAQ)

### 1. ¿Afecta un clon a los datos de la aplicación original?
**No, en absoluto.** ATBClone aísla los datos en `~/ATBClone/Data/<NombreClon>`. Los datos del anfitrión permanecen intactos.

### 2. ¿Dónde se guardan los datos? ¿Cómo hacer una copia de seguridad?
Están en `~/ATBClone/Data/<NombreClon>`. Copiar esta carpeta a otra unidad basta para realizar una copia completa.

### 3. ¿Existe riesgo de baneo o suspensión de cuenta?
ATBClone utiliza redirecciones de entorno nativas sin modificar memoria ni protocolos de red. A nivel de sistema, la app se ejecuta con normalidad.

### 4. ¿Se requieren permisos de administrador (Root/Sudo)?
**No.** Todas las operaciones se realizan en el espacio de usuario.

### 5. ¿Qué hacer ante advertencias de Gatekeeper ("dañado")?
Ejecute en la Terminal:
```bash
xattr -cr ~/ATBClone/Apps/<NombreClon>.app
```

---

## 🩺 Diagnóstico del sistema con Doctor

```bash
atbclone doctor
```

---

## 🐞 Notificar incidencias en GitHub

1. En ATBClone, abra los **"Detalles del clon"**.
2. Haga clic en **"Copiar información de diagnóstico"**.
3. Abra un Issue en [GitHub Issues](https://github.com/aitobox/ATBClone/issues) y pegue el informe.
"""

for fn, content in [("README.md", readme), ("01-basic-operations.md", ch01), ("02-advanced-custom-recipes.md", ch02), ("03-under-the-hood-and-internals.md", ch03), ("04-faq-and-troubleshooting.md", ch04)]:
    with open(f"{ES_DIR}/{fn}", "w", encoding="utf-8") as f:
        f.write(content)
    print(f"✓ Created es/{fn}")
