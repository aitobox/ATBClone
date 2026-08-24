[English](ReleaseNote.md) | [简体中文](ReleaseNote_zh.md) | [繁體中文](ReleaseNote_zh_TW.md) | [日本語](ReleaseNote_ja.md) | [한국어](ReleaseNote_ko.md) | [Deutsch](ReleaseNote_de.md) | [Français](ReleaseNote_fr.md) | [Русский](ReleaseNote_ru.md) | [Español](ReleaseNote_es.md)

# Notas de la versión de ATBClone (Release Notes)

En este documento se registran todas las actualizaciones principales, nuevas características, mejoras de rendimiento y correcciones de errores para **ATBClone**.

---

## [v0.9.8] - 2026-08-24

### 🔒 Extracción precisa de Entitlements y estabilidad de Hard Clone
- **Preservación de permisos de la aplicación de origen**:
  - Mejora de `HardCloneEngine` para extraer y mantener los derechos del binario Mach-O mediante `codesign -d --entitlements :-`.
  - Detección y prevención de archivos de permisos vacíos o corruptos al volver a firmar el clon.
- **Aislamiento estricto de contenedores de sandbox**:
  - Ajuste de `strip_sandbox: false` en todas las recetas integradas de hard clone (WeChat, QQ, WeWork, WPS Office, LINE, Skype, CapCut, etc.).
  - Garantiza la ejecución en contenedores independientes (`~/Library/Containers/<new_bundle_id>`) para evitar colisiones de datos o credenciales.

### 📚 Actualización de documentación
- **Sincronización de guías**:
  - Actualización de `README.md` y `README_zh.md` reflejando las nuevas opciones de `app_type`, `strip_sandbox` y flujos de trabajo.

### 📦 Calidad del software
- **Validación completa**:
  - Superadas satisfactoriamente las 428 pruebas automatizadas.

---

## [v0.9.7] - 2026-08-24

### 🔍 Detección inteligente de arquitectura y adaptación de idioma
- **Reconocimiento del framework de la aplicación (`app_type`)**:
  - Incorporación del campo `app_type` (`electron`, `chromium`, `qt`, `flutter`, `native_cocoa`, `java`, `unknown`) en el modelo Recipe.
  - `AppProber.detect_app_type` inspecciona los frameworks, dylibs y estructuras JVM para identificar el motor de la aplicación.
  - Estandarización de las 34 recetas integradas con `app_type` y `strip_sandbox` declarados.
- **Inyección adaptativa de argumentos de idioma**:
  - Configuración dinámica de opciones de idioma según el entorno (`--lang=` para Chromium/Electron, `-AppleLanguages` para Native Cocoa, `-user.language` para Java).

### 🧬 Detección y validación de argumentos en binarios Mach-O
- **Detección automática de argumentos de directorio de datos**:
  - Implementación de `BinaryArgumentProber` para escanear ejecutables Mach-O y encontrar flags compatibles (`--user-data-dir`, `--profile-directory`, `--datadir`, etc.) en aplicaciones no registradas.
- **Validación de argumentos de inicio**:
  - `LaunchArgumentValidator` descarta parámetros incompatibles antes de crear el clon.

### 📋 Inspección y copia de parámetros inyectados
- **Análisis de parámetros inyectados (`CloneInspector`)**:
  - `CloneInspector` desglosa variables de entorno, configuración de proxy, idioma e instrucciones de arranque de cada clon.
  - Nueva tarjeta «Parámetros inyectados» en `CloneDetailWindow` con botón de copia rápida al portapapeles.

### ⚙️ Opciones avanzadas en el editor de recetas
- **Edición visual de recetas (`RecipeEditWindow`)**:
  - Ajuste de tipo de framework, argumentos de inicio personalizados, configuración de proxy, variables de entorno y listas de enlaces simbólicos permitidos.

### 📦 Pruebas integrales
- **Ampliación de pruebas**:
  - Conjunto de pruebas ampliado a 428 pruebas automatizadas.

---

## [v0.9.6] - 2026-08-24

### 🖱️ Ordenación nativa al hacer clic en encabezados de tabla Cocoa
- **Ordenación interactiva de columnas**:
  - Implementación de ordenación en `NSTableViewHeaderView` para las tablas de `CloneListView` y `RecipeListView`.
  - Alternancia entre orden ascendente y descendente con indicadores de flecha y sincronización bidireccional con la barra de herramientas.
  - Mantenimiento automático de la selección al reordenar.

### 📦 Selección múltiple y operaciones por lotes
- **Gestión por lotes de clones (`CloneListView`)**:
  - Selección de múltiples filas (`multiple_select=True`) con activación dinámica de botones de acción.
  - Actualización y eliminación por lotes de clones (con confirmación de borrado de datos).
- **Eliminación por lotes de recetas y protección (`RecipeListView`)**:
  - Selección múltiple y eliminación de recetas personalizadas.
  - Diálogos de confirmación inteligentes (protección de recetas integradas, filtrado de selecciones mixtas).
  - Bloqueo de estado ocupado (busy lock) durante las operaciones en lote.

### 🛠️ Diagnóstico de Xcode Command Line Tools en la vista Doctor
- **Verificación del entorno de compilación**:
  - Comprobación automática de las herramientas de Xcode (`xcode-select -p`, `codesign`, `lipo`, `otool`, `install_name_tool`) y guía de instalación en Doctor View.

### ℹ️ Metadatos en el cuadro «Acerca de» nativo de macOS
- **Visualización corregida en Cocoa About**:
  - Envío adecuado de la versión y derechos de autor en `orderFrontStandardAboutPanelWithOptions:`.

### 📦 Pruebas integrales
- **Ampliación de pruebas**:
  - Conjunto de pruebas ampliado a 369 pruebas automatizadas.

---

## [v0.9.5] - 2026-08-23

### 📝 Nuevo componente `WrappingLabel` y ajuste automático de texto
- **Salto de línea dinámico en texto multilínea**:
  - Implementación del componente `WrappingLabel` para solucionar las limitaciones de etiquetas de una sola línea en Toga Cocoa.
  - Cálculo dinámico de altura (`cellSizeForBounds_`) según el ancho disponible, evitando el ensanchamiento horizontal no deseado de ventanas y diálogos.
- **Mejora en informes de análisis y detalles**:
  - Incorporación de `WrappingLabel` en `ProbeView` (informe del analizador, compatibilidad), `CloneDetailWindow` y `WizardWindow`.

### 🧪 Aislamiento de pruebas y estado
- **Evaluación dinámica de rutas**:
  - Optimización de `StateManager` y `RecipeLoader` para resolver rutas dinámicamente, asegurando la total independencia de las pruebas frente al estado local del usuario.
- **Pruebas integrales**:
  - Conjunto de pruebas ampliado a 347 pruebas automatizadas.

---

## [v0.9.4] - 2026-08-23

### 📁 Migración del directorio de datos predeterminado a `~/ATBClone`
- **Gestión intuitiva de datos de usuario**:
  - Migración del directorio raíz desde la carpeta oculta `~/.atbclone` hacia la carpeta visible `~/ATBClone` (`~/ATBClone/Data/`, `~/ATBClone/clones.yaml`).
  - Facilita la consulta, respaldo y gestión de los datos de las aplicaciones clonadas mediante Finder y Terminal.

### 🏷️ Aplicación precisa del nombre de visualización personalizado
- **Limpieza de nombres localizados**:
  - Eliminación de `LSHasLocalizedDisplayName` y limpieza de `InfoPlist.strings` en `SoftCloneEngine` y `HardCloneEngine`.
  - Garantiza que Finder, Dock, Spotlight y el Monitor de Actividad muestren exactamente el nombre asignado por el usuario.

### 🔄 Registro automático en LaunchServices
- **Actualización inmediata de caché**:
  - Ejecución de `lsregister -f` tras cada clonación o actualización para refrescar iconos y metadatos de inmediato en macOS.

### 📦 Documentación y pruebas integrales
- **Actualización global**:
  - Actualización de documentación, ajustes de la GUI y sincronización de las 341 pruebas automatizadas.

---

## [v0.9.3] - 2026-08-21

### 🛡️ Inspección mejorada y validación preventiva en el asistente
- **Detección temprana de aplicaciones iOS-on-Mac**:
  - Actualización de `AppInspector.inspect_app` para analizar directamente `UIDeviceFamily` y `LSRequiresIPhoneOS` al arrastrar o seleccionar una aplicación.
  - En el asistente de la GUI (`WizardWindow`), al seleccionar una aplicación portada de iOS se muestra inmediatamente un cuadro de diálogo de aviso y se reinicia la entrada.

### 🍏 Cierre limpio en macOS y liberación de recursos Cocoa
- **Prevención de fallos al cerrar la aplicación (Crash on Exit)**:
  - Optimización de `TrayService.disable()` y `ATBCloneApp.exit_app()` para desvincular de forma segura los selectores y destinos del icono de la barra de menús.
  - Cierre ordenado del bucle de eventos Cocoa (`NSApp.terminate_` / `os._exit(0)`), eliminando cierres inesperados al salir mediante el menú de la bandeja o `Cmd+Q`.

### 📦 Pruebas integrales
- **Ampliación de pruebas**:
  - Conjunto de pruebas ampliado a 341 pruebas automatizadas.

---

## [v0.9.2] - 2026-08-21

### 🍏 Ocultación dinámica del icono del Dock en macOS y mejoras en la bandeja
- **Control automático de visibilidad en el Dock**:
  - Gestión dinámica del icono del Dock mediante las políticas de activación de AppKit (`NSApplicationActivationPolicy`).
  - Al minimizar o cerrar la ventana hacia la bandeja del sistema, el icono del Dock se oculta automáticamente (`NSApplicationActivationPolicyAccessory`).
  - Al restaurar la ventana desde la barra de menús, el icono reaparece de forma transparente (`NSApplicationActivationPolicyRegular`) con enfoque inmediato.
- **Controlador de reapertura desde el Dock**:
  - Implementación de `applicationShouldHandleReopen:hasVisibleWindows:` en `AppDelegate` para restaurar la ventana principal al hacer clic en el Dock.

### 📦 Optimización de recursos y pruebas
- **Reducción de peso de iconos**:
  - Optimización y compresión de recursos (`logo.icns` y `logo.png`) para reducir el tamaño del paquete.
- **Pruebas integrales**:
  - Conjunto de pruebas ampliado a 338 pruebas automatizadas.

---

## [v0.9.1] - 2026-08-21

### 🛡️ Detección y bloqueo seguro de aplicaciones iOS-on-Mac
- **Gestión de arquitecturas no compatibles**:
  - Mejora de `AppProber`, `SoftCloneEngine` y `HardCloneEngine` para identificar con precisión aplicaciones de iOS/iPadOS ejecutadas en Apple Silicon (aplicaciones con `Wrapper/` o `UIDeviceFamily` / `LSRequiresIPhoneOS=True`).
  - Bloqueo preventivo de la clonación de aplicaciones iOS en la CLI (`atbclone clone`, `atbclone wizard`) y en el asistente de la GUI con aviso descriptivo (`error_ios_wrapper_unsupported`), evitando la creación de paquetes corruptos.

### 🎨 Generación automática de iconos en scripts de compilación
- **Creación dinámica de `.icns`**:
  - Adición de la compilación automática de iconos `.icns` mediante `sips` e `iconutil` en `scripts/build_gui.sh` durante el empaquetado en DMG.
  - Validación reforzada de recursos y firmas en el empaquetado.

### 🌐 Localización y pruebas
- **Mensajes de error traducidos**:
  - Traducción del mensaje de advertencia sobre aplicaciones de iOS a los 9 idiomas.
- **Pruebas integrales**:
  - Conjunto de pruebas ampliado a 336 pruebas automatizadas.

---

## [v0.9.0] - 2026-08-21

### 🌐 Aislamiento independiente de idioma y configuración regional (Locale)
- **Configuración de idioma exclusivo por clon (`--language` / `--locale`)**:
  - Compatibilidad para ejecutar cada clon en un idioma exclusivo, independiente del idioma del sistema macOS y de la aplicación original.
  - Opciones `--language` / `--locale` agregadas a `atbclone clone` y `atbclone wizard`, con selector de idioma en el asistente visual y ventana de edición.
  - Inyección automática de `AppleLanguages` y `AppleLocale` en scripts de inicio y ejecutables.
  - Módulo `atbclone.core.locale` para análisis de códigos de idioma BCP-47.

### 🆔 Resolución robusta de identificadores Bundle multi-instancia
- **Identificadores de paquete únicos y secuenciales**:
  - Incorporación de `AppInspector.find_next_bundle_id` para generar Bundle IDs deterministas y sin colisiones (`com.vendor.app.atb1`, `atb2`, etc.) al clonar la misma aplicación varias veces.

### 🍏 Activación desde la barra de menús y ciclo de vida de la ventana
- **Restauración fluida desde el System Tray**:
  - Corrección de la activación, desminiaturización y enfoque de la ventana principal al abrir desde `TrayService`.
  - Intercepción del cierre de ventana (`Cmd+W` / botón rojo) para ocultar hacia la barra de menús cuando la opción está activa.
  - Soporte mejorado para eventos de ratón en el icono de estado.

### ⚡ Actualización de clones y limpieza de directorio destino
- **Actualizaciones atómicas**:
  - Corrección de condiciones de carrera durante la actualización de clones mediante limpieza previa del directorio de destino.
  - Sincronización en tiempo real de tarjetas y listas en la GUI.

### 🎨 Tipografía, ajuste de controles y documentación
- **Pulido visual**:
  - Altura de fila en tablas Cocoa ajustada a 34px y eliminación del truncamiento de texto en menús desplegables.
  - README actualizado con guía de uso de la interfaz gráfica y capturas de pantalla.
- **Pruebas integrales**:
  - Conjunto de pruebas ampliado a 329 pruebas automatizadas.

---

## [v0.8.0] - 2026-08-20

### 🎨 Renovación visual según las directrices macOS HIG
- **Diseño nativo de Apple y accesibilidad mejorada**:
  - Rediseño integral de la interfaz gráfica siguiendo las Apple Human Interface Guidelines (HIG): paletas de colores nativas, escala tipográfica (11pt–22pt) y espaciado armonioso.
  - Renderizado optimizado de tablas Cocoa mediante parche dinámico (`patch_cocoa`): altura de fila ampliada a 40px, encabezados modernizados y fuente de celdas aumentada.
  - Mayor tamaño en campos de entrada, menús desplegables, interruptores, botones y etiquetas en el asistente y configuración.
  - Barras de acciones inferiores transformadas en barras de herramientas nativas compactas de macOS.
  - Modo predeterminado cambiado a **Vista de Lista (List View)** en todas las secciones de administración.

### 💾 Configuración unificada de almacenamiento y sincronización de rutas
- **Gestión simplificada de almacenamiento**:
  - Reorganización de `SettingsView`: al modificar el directorio raíz de almacenamiento se actualizan automáticamente todas las subrutas derivadas (`clones.yaml`, `Data/`, `logs/`, `recipes/`).
  - Validación de rutas e indicadores de estado en tiempo real.

### 🌐 Soporte para protocolo de proxy HTTPS
- **Ampliación de opciones de red**:
  - Soporte completo para esquemas de proxy `https://` en modelos de recetas, CLI (`atbclone clone`, `atbclone wizard`) y GUI.

### 📦 Mejoras en el empaquetado de la aplicación y pruebas
- **Punto de entrada de módulo y generación de DMG**:
  - Incorporación de `src/atbclone/__main__.py` para ejecución directa con `python -m atbclone`.
  - Mejora del script `scripts/build_gui.sh` con verificación de integridad del App Bundle, iconos y firma de código.
- **Pruebas integrales**:
  - Conjunto de pruebas ampliado a 304 pruebas unitarias y de integración GUI.

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
