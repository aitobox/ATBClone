[English](ReleaseNote.md) | [简体中文](ReleaseNote_zh.md) | [繁體中文](ReleaseNote_zh_TW.md) | [日本語](ReleaseNote_ja.md) | [한국어](ReleaseNote_ko.md) | [Deutsch](ReleaseNote_de.md) | [Français](ReleaseNote_fr.md) | [Русский](ReleaseNote_ru.md) | [Español](ReleaseNote_es.md)

# Notas de la versión de ATBClone (Release Notes)

En este documento se registran todas las actualizaciones principales, nuevas características, mejoras de rendimiento y correcciones de errores para **ATBClone**.

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
