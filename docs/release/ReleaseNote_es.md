[English](ReleaseNote.md) | [简体中文](ReleaseNote_zh.md) | [繁體中文](ReleaseNote_zh_TW.md) | [日本語](ReleaseNote_ja.md) | [한국어](ReleaseNote_ko.md) | [Deutsch](ReleaseNote_de.md) | [Français](ReleaseNote_fr.md) | [Русский](ReleaseNote_ru.md) | [Español](ReleaseNote_es.md)

# Notas de la versión de ATBClone (Release Notes)

En este documento se registran todas las actualizaciones principales, nuevas características, mejoras de rendimiento y correcciones de errores para **ATBClone**.

---

## [v0.7.0] - 2026-08-20

### 🖥️ Aplicación de escritorio nativa con interfaz BeeWare Toga
- **Moderna interfaz gráfica Ice-Blue**:
  - Lanzamiento de la aplicación nativa para macOS (`atbclone-gui`) desarrollada con BeeWare Toga.
  - Navegación lateral intuitiva y diseño en cuadrícula de tarjetas: gestión de clones (`ClonesView`), análisis profundo (`ProbeView`), recetas (`RecipesView`), visor de registros (`LogsView`) y ajustes (`SettingsView`).
  - Asistente visual interactivo con soporte para arrastrar y soltar archivos `.app`.

### 🍏 Integración en la barra de menús de macOS y minimización
- **Servicio de barra de menús (TrayService)**:
  - Integración nativa mediante `NSStatusBar` y `NSStatusItem` con menú rápido (Abrir ventana principal, Crear clon, Inicio rápido, Preferencias, Salir).
  - Opción de «Minimizar a la barra de menús» mediante selectores Cocoa y `NSWindowDelegate`.

### 📖 Visor multilingüe de notas de versión en la GUI
- **Ventana integrada de Release Notes**:
  - Acceso directo a las notas de versión desde la pantalla de configuración.
  - Menú desplegable dinámico en 9 idiomas con renderizado Markdown en tiempo real.

### 📝 Sistema unificado de registro de operaciones (Unified Logger)
- **Persistencia en disco y transmisión en directo**:
  - Módulo `atbclone.core.logger` que unifica los registros de CLI y GUI (`~/.atbclone/logs/atbclone.log`) con difusión en memoria (`LogBroadcastHandler`).
  - Visor de registros en la GUI con filtrado por niveles, búsqueda, exportación y vaciado.

### 📦 Nuevas recetas y ampliación de pruebas
- **Recetas integradas**: Soporte para **Claude Desktop** (`com.anthropic.claudefordesktop`), **Telegram** (`ru.keepcoder.Telegram`), **Cursor** y más.
- **Pruebas integrales**: Conjunto de pruebas ampliado a 299 pruebas unitarias y de integración GUI.

---

## [v0.6.0] - 2026-08-19

### 📂 Soporte para directorio de datos personalizado
- **Ubicación de almacenamiento configurable (`--data-dir`)**:
  - Añadida la opción `--data-dir` en `atbclone clone` para personalizar la ruta de datos del clon (ej. discos SSD externos o carpetas de trabajo).
  - Configuración del directorio de datos integrada en el asistente interactivo (`atbclone wizard`).
  - Soporte para variables dinámicas de directorio de datos en modelos de recetas y motores de clonación.

### 🗑️ Desinstalación y limpieza de clones mejorada (`atbclone remove`)
- **Control seguro de eliminación de datos**:
  - Añadido el parámetro `--purge-data` en `atbclone remove` para la eliminación completa y automatizada del clon y sus datos asociados.
  - Añadido el parámetro `--keep-data` para desinstalar únicamente la aplicación conservando los datos de usuario.
  - Diálogos interactivos de confirmación con opciones claras entre conservar o purgar datos.
  - Diagnóstico y manejo de errores optimizado para directorios huérfanos y permisos.

### 🆔 Estandarización de Bundle ID y soporte multilingüe
- **Generación estandarizada de identificadores de paquete**:
  - Integración de `AppInspector.generate_bundle_id` para garantizar formatos coherentes de Bundle ID en `clone`, `wizard` y `update`.
- **Localización**:
  - Traducción completa de diálogos de directorios, confirmaciones de eliminación y registros de estado en los 9 idiomas.
- **Pruebas integrales**:
  - Ampliación del conjunto de pruebas a 213 pruebas unitarias automatizadas.

---

## [v0.5.0] - 2026-08-19

### 🔐 Firma de código Apple y canalización de notarización
- **Hardened Runtime y firma certificada**:
  - Integración completa de la firma de código con certificados Apple Developer ID Application, Hardened Runtime (`--options runtime`), marcas de tiempo y derechos JIT personalizados (`scripts/entitlements.plist`).
  - Script `scripts/notarize.sh` para la notarización automatizada ante Apple mediante `xcrun notarytool` utilizando perfiles del llavero (`--keychain-profile`).
  - Opciones `--sign-identity`, `--skip-sign` y `--notarize` agregadas a `scripts/build_cli.sh` y `scripts/release.sh` con respaldo ad-hoc automático.

### 🚀 Clonación profunda de Chromium e inyección de argumentos de inicio
- **Inyección de argumentos de inicio en `HardCloneEngine`**:
  - Mejora de `HardCloneEngine` para inyectar dinámicamente argumentos como `--user-data-dir={{ATB_DATA_DIR}}` en el script ejecutable.
  - Actualización de las recetas para **Google Chrome**, **Microsoft Edge** y **Arc Browser** a la estrategia `hard_clone` para una duplicación completa del App Bundle.
- **Anulación de estrategia en CLI**:
  - Nueva opción `--strategy` (`hard_clone` o `soft_clone`) en el comando `atbclone clone`.

### ⚡ Redirección de procesos y conjunto de pruebas ampliado
- **Gestión de procesos**: Optimización del script envoltorio de `SoftCloneEngine` mediante `exec "$@"`.
- **Pruebas integrales**: Ampliación del conjunto de pruebas a 199 pruebas unitarias automatizadas.

---

## [v0.4.0] - 2026-08-19

### 🌐 Soporte multilingüe integral en 9 idiomas para CLI y documentación
- **Internacionalización completa del CLI en 9 idiomas**:
  - Expansión del motor `atbclone.core.i18n` con soporte completo para inglés, chino simplificado, chino tradicional, japonés, coreano, alemán, francés, ruso y español.
  - Todos los comandos del CLI (`wizard`, `clone`, `probe`, `list`, `recipe`, `doctor`, `update`, `remove`, `version`) ofrecen mensajes, tablas y diagnósticos traducidos.
- **Estructura estandarizada de notas de versión multilingües**:
  - Organización y mantenimiento de notas de versión en 9 idiomas dentro del directorio `docs/release/`.

### 🔄 Flujo automatizado de lanzamiento y sincronización de versiones
- **Validación automática de ReleaseNotes en 9 idiomas**:
  - Optimización de `scripts/manage_version.py` y `scripts/release.sh` con verificación previa para garantizar que los 9 archivos en `docs/release/` contengan la versión antes de etiquetar en Git.
  - Opción `--check-notes` incorporada para evitar omisiones de documentación.
- **Suite de pruebas ampliada**:
  - Ampliación a 191 pruebas automatizadas con cobertura total de internacionalización y flujo de publicación.

---

## [v0.3.0] - 2026-08-19

### 🌐 Internacionalización y compatibilidad multilingüe (i18n)
- **Detección automática del idioma del sistema macOS**:
  - Integración del motor `atbclone.core.i18n` que detecta automáticamente las preferencias de idioma de la interfaz de macOS mediante `AppleLanguages` y `AppleLocale`.
  - Cambio dinámico e inteligente de asistentes interactivos, avisos de terminal, encabezados de tablas y registros de errores entre español, inglés y chino.
  - Compatibilidad con la variable de entorno `ATBCLONE_LANG` (`ATBCLONE_LANG=en` / `ATBCLONE_LANG=zh`) para anular manualmente el idioma.
- **Documentación multilingüe**:
  - `Readme.md` estandarizado en inglés por defecto y versión completa en chino en `Readme_zh.md`.
  - Publicación de notas de versión en 9 idiomas: inglés, chino simplificado, chino tradicional, japonés, coreano, alemán, francés, ruso y español.

### 🛠️ Mejoras de CLI y compilación
- **Internacionalización del asistente**: Compatibilidad multilingüe completa en `atbclone wizard` (nombres personalizados, iconos `.icns` y configuración de proxies).
- **Binario independiente**: Recompilación de `./dist/ATBCloneCli` mediante Nuitka con diccionario multilingüe integrado y mayor compatibilidad con sandbox (`PYTHONNOUSERSITE=1`).
- **Suite de pruebas**: Añadido `test_i18n.py` y validación exitosa de las 186 pruebas unitarias.

---

## [v0.2.0] - 2026-08-18

### 🚀 Nuevas características principales
- **Asistente interactivo de clonación (`atbclone wizard`)**:
  - Guía paso a paso en el terminal con soporte para arrastrar y soltar rutas `.app`.
  - Detección automática del incremento de nombres de clones (p. ej., `WeChat2`, `WeChat3`).
  - Personalización de nombres de visualización y asignación de iconos personalizados `.icns`.
  - Configuración interactiva de proxies de red dedicados (HTTP y SOCKS5) con autenticación.
- **Sonda avanzada de aplicaciones (`atbclone probe`)**:
  - Análisis automático de arquitectura Mach-O (arm64, x86_64, Universal), frameworks (Electron, Flutter, Chromium, Qt, Cocoa) y privilegios de sandbox (`com.apple.security.app-sandbox`).
  - Recomendación dinámica de la estrategia óptima (`hard_clone` o `soft_clone`) para aplicaciones no registradas y generación de archivos Recipe YAML.
  - Ejecución automática de la sonda dentro de `atbclone clone` cuando una aplicación no tiene receta predefinida.
- **Compilación de ejecutable único**:
  - Inclusión de `scripts/build_cli.sh` para compilar un binario nativo macOS arm64 de un solo archivo y sin dependencias externas (`dist/ATBCloneCli`) mediante Nuitka.

### ⚡ Mejoras y correcciones
- Elevación de privilegios optimizada a través del cuadro de diálogo nativo de macOS `osascript` para el directorio `/Applications`.
- Escape riguroso de rutas con `shlex.quote` para prevenir incidencias provocadas por espacios y caracteres especiales.

---

## [v0.1.0] - 2026-08-17

### 🌟 Lanzamiento inicial
- **Arquitectura de clonación con motor dual**:
  - **Motor Hard Clone**: Duplicación completa del App Bundle, modificación de `Info.plist`, aislamiento de `HOME` / `TMPDIR`, eliminación opcional de sandbox y refirma ad-hoc.
  - **Motor Soft Clone**: Envoltura ligera de inicio para navegadores Chromium y editores con inyección de `--user-data-dir`.
- **Más de 18 recetas predefinidas**:
  - Mensajería: WeChat, QQ, Telegram, LINE, Slack, Discord, Skype.
  - Clientes de IA: ChatGPT (Codex), Gemini, Antigravity, Antigravity IDE.
  - Navegadores y herramientas: Google Chrome, Microsoft Edge, Firefox, Arc, Cursor, VS Code, Zed.
- **Conjunto completo de comandos CLI**:
  - `clone`: Crear clones de aplicaciones.
  - `list`: Ver lista de clones activos en formato de tabla Rich.
  - `update`: Sincronizar clones tras la actualización de la aplicación principal conservando todos los datos del usuario.
  - `remove`: Eliminar clones de forma segura.
  - `recipe`: Consultar recetas integradas y modificaciones locales.
  - `doctor`: Autodiagnóstico del entorno del sistema (`codesign`, `xcode-select`, `PlistBuddy`).
