[English](ReleaseNote.md) | [简体中文](ReleaseNote_zh.md) | [繁體中文](ReleaseNote_zh_TW.md) | [日本語](ReleaseNote_ja.md) | [한국어](ReleaseNote_ko.md) | [Deutsch](ReleaseNote_de.md) | [Français](ReleaseNote_fr.md) | [Русский](ReleaseNote_ru.md) | [Español](ReleaseNote_es.md)

# Notas de la versión de ATBClone (Release Notes)

## [v2.3.1] - 2026-10-26

### 🛡️ Aislamiento multi-instancia de WorkBuddy en Hard Clone y corrección de singleton
- **Resolución de activación accidental y colisiones de singleton (#37, #38)**:
  - Corregido un fallo crítico por el cual los clones de WorkBuddy (`com.tencent.workbuddy.mac` y `com.workbuddy.workbuddy-ai`) no podían ejecutarse de forma independiente o reactivaban la instancia principal existente debido al bloqueo singleton de Electron.
  - Nuevas recetas integradas para WorkBuddy: preconfiguradas con estrategia `hard_clone`, eliminación de sandbox, aislamiento de esquemas URL, acceso a llavero y rutas dedicadas (`HOME`, `TMPDIR`, `WORKBUDDY_CONFIG_DIR`, `WORKBUDDY_USER_DATA_DIR`).
  - Implementada biblioteca dylib de hook dedicada (`libatbclone_workbuddy_hook.dylib`) junto al lanzador en C para interceptar el traspaso de instancias únicas.
  - `AppProber` optimizado: recomienda por defecto `hard_clone` con inyección de `HOME` y `TMPDIR` para todas las aplicaciones Electron, auto-detectando el entorno de WorkBuddy.
  - Inyección garantizada de `HOME` y `TMPDIR` en `HardCloneEngine` para cualquier aplicación Electron, incluso con argumentos de inicio personalizados.

### 🌐 Enlace de descarga en la cabecera de la documentación en 9 idiomas
- **Acceso directo al instalador (#35)**:
  - Añadido enlace de descarga directa en el menú superior de la documentación en las 9 versiones lingüísticas.

### 🧪 Ampliación de la suite de pruebas y calidad
- **Cobertura ampliada**:
  - Incorporadas pruebas unitarias sobre recetas de WorkBuddy, generación de dylibs, sondeo de aplicaciones e inyección de variables de entorno (`test_workbuddy_isolation.py`).
  - Conjunto de pruebas ampliado a **664 pruebas automáticas** con un 100% de aprobados.

---

## [v2.3.0] - 2026-09-23

### 🔄 Formato de error de actualización en una línea y estabilidad de la barra lateral
- **Prevención de desajustes verticales en el diseño**:
  - Reestructuración completa del sistema de información de comprobación de actualizaciones: evita que mensajes de error largos y multilínea deformen la barra lateral ante fallos de conexión o tiempos de espera.
  - Implementación de etiquetas nativas Cocoa con truncamiento final (`NSLineBreakByTruncatingTail`) y altura fija para asegurar dimensiones estables en la barra lateral.
  - Analizador de errores inteligente (`format_update_error`) que convierte excepciones de red y HTTP complejas en mensajes concisos y localizados en una sola línea (tiempo de espera agotado, error de red, códigos HTTP).
  - Temporizador de 5 segundos para limpiar automáticamente el mensaje de error y mantener una interfaz limpia.

### 🌐 Soporte multilingüe completo para mensajes de error
- **Cobertura en los 9 idiomas**:
  - Incorporadas 4 nuevas claves de traducción dedicadas a errores de actualización (`update_error_short`, `update_error_timeout`, `update_error_network`, `update_error_http`).

### 🧪 Ampliación de la suite de pruebas y calidad
- **Cobertura de pruebas**:
  - Incorporadas pruebas unitarias sobre el formateo de errores, el truncamiento y el temporizador de limpieza (`test_sidebar_update.py`, `test_i18n_update_keys.py`).
  - Conjunto de pruebas ampliado a **659 pruebas automáticas** con un 100% de aprobados.

---

## [v2.2.1] - 2026-09-23

### 🛡️ Protección de procesos helper en Electron/Chromium y estabilidad de Mojo IPC
- **Resolución de bucles de cierre inesperado (Crash Loops) en subprocesos**:
  - Corrección de un fallo crítico por el cual el renombrado de binarios en clones duros modificaba aplicaciones helper y subaplicaciones anidadas, rompiendo la comunicación Chromium Mojo IPC y puertos Mach en aplicaciones como QQ/QQNT, VS Code y Slack.
  - Alcance de renombrado estrictamente acotado para arquitecturas Chromium/Electron: únicamente se renombran el binario principal raíz (`CFBundleExecutable`) y el lanzador de entrada.
  - Conservación íntegra de todos los paquetes helper (`*Helper*.app`), complementos y subaplicaciones anidadas (ej. `QQEXGuild.app`) en `Frameworks`, `Resources` y `PlugIns`.

### 🔍 Detección multicapa de arquitecturas Electron y Chromium
- **Análisis de aplicaciones mejorado**:
  - Actualización de `AppProber` para reconocer `QQNT.framework`, variantes de paquetes asar (`app.asar`, `electron.asar`, `application.asar`) y patrones de paquetes helper.
  - Verificación dual en tiempo de ejecución en el motor de clonación mediante flags `is_chromium` e inspección de directorios.

### 📐 Documentación de arquitectura y registros ADR
- **Invariantes del sistema formalizados**:
  - Añadidos `CONTEXT.md` en la raíz y el ADR `0001-process-aliasing-scope-and-helper-preservation.md` para documentar los límites de alias de procesos y la integridad del IPC.

### 🧪 Aseguramiento de la calidad y pruebas automáticas
- **Suite de pruebas ampliada**:
  - Incorporadas pruebas unitarias dedicadas a la preservación de helpers y la detección de QQNT/asar (`test_process_names.py`, `test_app_prober.py`).
  - Conjunto de pruebas ampliado a **649 pruebas automáticas** con un 100% de aprobados.

---

## [v2.2.0] - 2026-09-22

### 📝 Notas en clones y filtrado de búsqueda instantáneo
- **Anotaciones personalizadas para clones**:
  - Añadido el campo `notes` en `CloneRecord` y en la ventana de edición `CloneEditWindow` para guardar notas sobre la cuenta, propósito, región o etiquetas.
  - Nueva columna «Notas» en la vista de tabla de `CloneListView` con ordenación por clic en el encabezado (ascendente/descendente).
  - La barra de búsqueda de la barra de herramientas superior ahora incluye búsqueda difusa en las notas, permitiendo localizar cualquier clon rápidamente.
  - En la vista de tarjetas (`CloneCard`) se muestra un resumen de las notas cuando existen.
  - Localización completa en los 9 idiomas para etiquetas de notas y marcadores de posición.

### 📐 Diseño ergonómico de ventana principal y barra lateral
- **Mayor espacio visual y comodidad**:
  - Las dimensiones predeterminadas de la ventana principal se amplían a `1300 x 760` (antes 1200 x 680), proporcionando un área más amplia para tablas y cuadrículas.
  - La barra lateral de navegación izquierda pasa de 200px a `240px` de ancho, garantizando una lectura despejada de apartados, contadores y comprobador de actualizaciones.

### 🔬 Verificación de compilación con Clang para bibliotecas dinámicas
- **Robustez de hooks de bajo nivel**:
  - Incorporadas pruebas de integración automatizadas que invocan el compilador real `clang` para validar todas las dylibs inyectadas:
    - Bibliotecas dylib de interposición Cocoa / POSIX (`libatbclone_hook`).
    - Dylibs personalizadas de aislamiento para Lark (Feishu) y ChatGPT.
    - Dylib de inyección de variables de entorno (`libatbclone_env`).
  - Garantiza la compilación limpia sin advertencias ni regresiones en las herramientas de desarrollo de macOS.

### 🧪 Ampliación de la suite de pruebas e independencia de pantalla
- **Mayor estabilidad en pruebas automáticas**:
  - Desacopladas las aserciones de tamaño de ventana en pruebas GUI respecto a la resolución de la pantalla anfitriona, garantizando ejecuciones predecibles en entornos CI.
  - Suite de pruebas ampliada a **648 pruebas automáticas** con un 100% de aprobados.

---

## [v2.1.1] - 2026-09-18

### 🔧 Corrección de alcance de variables en el lanzador C y robustez
- **Resolución de errores de compilación del lanzador para Lark y ChatGPT**:
  - Corrección de un fallo de compilación en C derivado del conflicto de nombres (redefinición de `dir`) en el lanzador generado para aplicaciones con inyección de bibliotecas dinámicas (como Lark/Feishu y ChatGPT).
  - Aislamiento del bloque `hook_block` dentro de un bloque compuesto independiente `{ ... }` en el generador, evitando colisiones de variables.
  - Incorporación de pruebas de compilación reales con `clang` para los lanzadores de Lark y ChatGPT.

### 🛡️ Mayor solidez al renombrar procesos y tolerancia a bundles no estándar
- **Manejo seguro de excepciones y degradación elegante**:
  - Robustecimiento del renombrado de binarios y sincronización de `Info.plist` ante estructuras de paquetes inusuales, plists ausentes o binarios corruptos.
  - Degradación segura a las rutas predeterminadas con avisos claros en el registro, sin interrumpir el proceso de clonación.
  - Pruebas adicionales para bundles anómalos y escenarios de respaldo.

### 🎨 Protección contra valores nulos en la vista previa de iconos del asistente
- **Estabilidad de la interfaz**:
  - Añadida verificación de seguridad contra nulos en el visor de iconos de `WizardWindow` para evitar excepciones de interfaz con aplicaciones de metadatos incompletos.

### 🧪 Aseguramiento de la calidad y pruebas automáticas
- **Suite de pruebas ampliada**:
  - Conjunto de pruebas ampliado a **645 pruebas automáticas** con un 100% de aprobación.

---

## [v2.1.0] - 2026-09-17

### 🚀 Nombres de proceso únicos para Hard Clones y enrutamiento en proxies
- **Enrutamiento proxy preciso basado en procesos**:
  - El motor de clonación Hard Clone ahora genera un nombre de binario ejecutable único y sincroniza la clave `CFBundleExecutable` para cada clon (p. ej., `<AppName>_<NombreClon>`).
  - Compatibilidad total con reglas de enrutamiento por proceso en gestores como Clash, Surge, Loon, Stash y Quantumult X (`PROCESS-NAME,<NombreProcesoClon>,<GrupoProxy>`), permitiendo asignar proxies o IPs independientes a cada clon.
  - Compatibilidad exhaustiva con los procesos auxiliares (Helper Apps) de Electron y Chromium, preservando la comunicación IPC sin colisiones de nombres.
  - Conservación automática de nombres de procesos e iconos personalizados al editar, actualizar o reconstruir clones.

### 🎨 Iconos de aplicación personalizados en el asistente de clonación
- **Personalización visual de clones**:
  - Incorporación de selección de icono personalizado (`.icns` o `.png`) directamente en el asistente de creación (`WizardWindow`).
  - Vista previa en tiempo real en la interfaz del asistente con opción para restablecer el icono predeterminado.
  - Reemplazo y conversión nativa dentro de `Contents/Resources/`, manteniendo el icono a través de futuras actualizaciones.
  - Traducción completa de los controles e indicadores en los 9 idiomas disponibles.

### 🔄 Control de actualización permanente en la parte inferior de la barra lateral
- **Experiencia de actualización unificada**:
  - Traslado de la comprobación de actualizaciones desde Ajustes hacia la parte inferior de la barra lateral de navegación para mayor accesibilidad.
  - Icono animado, información de versión en tiempo real y barra de progreso porcentual durante la descarga.
  - Vista de Ajustes simplificada y enfocada en las preferencias generales.

### 🧪 Aseguramiento de la calidad y pruebas automáticas
- **Suite de pruebas ampliada**:
  - Incorporación de pruebas unitarias y de integración para nombres de procesos, compatibilidad de Helpers, persistencia de iconos y UI de barra lateral (`test_process_names.py`, `test_update_icon.py`).
  - Suite de pruebas ampliada a **642 pruebas automáticas** con un 100% de aprobación.

---

## [v2.0.0] - 2026-09-17

### 🏥 Diagnóstico del entorno (Doctor) y verificación de permisos de carpetas
- **Verificación profunda de permisos del sistema de archivos**:
  - Ampliación del subsistema de diagnóstico (CLI `atbclone doctor` y GUI `DoctorView`) con comprobación en tiempo real de permisos de lectura y escritura en el directorio de aplicaciones (`~/ATBClone/Apps`) y en el de datos (`~/ATBClone/Data`).
  - Sondeo activo mediante tokens temporales seguros para detectar denegaciones de acceso antes de crear clones o iniciar instancias.
  - Informes detallados con distintivos de estado, desglose de errores del sistema y comandos de corrección prácticos (`chmod u+rwx <path>`).
  - Nuevas funciones auxiliares `check_directory_access()`, `get_apps_dir()` y `get_data_dir()` en `core.config`.
  - Traducción completa de los mensajes de diagnóstico y sugerencias de reparación en los 9 idiomas.

### 📐 Renderizado matemático KaTeX y diseño en el portal de documentación
- **Tipografía matemática**:
  - Integración del motor de renderizado KaTeX en las 9 versiones del portal oficial (`clone.aitobox.com`).
  - Optimización de espaciados y formato de fórmulas LaTeX en los capítulos de arquitectura técnica.

### ⚡ Madurez arquitectónica y aseguramiento de calidad (Hito v2.0.0)
- **Motor APFS de alto rendimiento y concurrencia**:
  - Consolidación de la base de v2.0: clonación APFS Copy-on-Write (`cp -Rc`) instantánea sin duplicar espacio en disco, sondeo binario SIMD y persistencia atómica con `flock`.
  - Ampliación de las pruebas unitarias y de GUI para el diagnóstico de directorios (`test_cmd_doctor.py`, `test_config.py`, `test_probe_and_doctor_ui.py`).
  - 614 pruebas automáticas superadas con éxito (tasa de aprobación del 100%).

---

## [v1.9.0] - 2026-09-16

### ⚡ Clonación APFS Copy-on-Write (CoW) y optimización del motor
- **Clonación instantánea sin consumo adicional de disco**:
  - Implementación completa de Copy-on-Write (`cp -Rc`) en volúmenes APFS de macOS: duplicación instantánea de aplicaciones de gran tamaño sin gasto inicial de espacio en disco.
  - Mecanismo de respaldo robusto a copia recursiva estándar (`cp -R`) con limpieza automática de directorios residuales para evitar corrupción por anidamiento en volúmenes no APFS.
  - Prefiltrado acelerado por hardware SIMD en el sondeo de cadenas binarias, mejorando notablemente la detección de argumentos y variables de entorno.
  - Omisión segura de binarios Mach-O durante la inspección de scripts envolventes y ajuste no destructivo de entitlements de firma.

### 🔒 Bloqueo de archivos interproceso y persistencia atómica
- **Eliminación total de condiciones de carrera**:
  - Implementación de bloqueos de archivo basados en `flock` para garantizar la consistencia de lectura y escritura ante ejecuciones concurrentes de clones o comandos CLI.
  - Escritura atómica de configuraciones y estado (archivo temporal + sincronización `fsync` + sustitución con `os.replace`) con permisos estrictos `0o600`.
  - Aislamiento seguro de `fake_pw` por hilo (thread-local) en el hook de interposición Cocoa para garantizar seguridad en entornos multihilo.

### 🖥️ Refinamiento de GUI / HIG y estabilidad de memoria
- **Experiencia nativa de macOS y ciclo de vida reforzado**:
  - Corrección de fuga de memoria en `LogsView` mediante retención de buffer delimitado y despacho seguro al hilo principal de Cocoa.
  - Registro de limpieza al salir de la aplicación (`_on_app_exit`) para desuscribir los oyentes de registros en tiempo real.
  - Corrección de la jerarquía de ventanas: las ventanas secundarias (asistente, edición, recetas, detalles) vuelven al nivel estándar de ventana (`0`), evitando que queden flotando sobre otras aplicaciones de macOS.
  - Mayor contraste en el modo oscuro, persistencia de rutas personalizadas (`base_dir`) y limpieza garantizada de credenciales de proxy en Keychain al eliminar un clon.
  - Estandarización del nombre oficial en chino a **ATB分身助手**.

### 📚 Portal de documentación oficial en 9 idiomas y aseguramiento de calidad
- **Nuevo portal de documentación (`clone.aitobox.com`)**:
  - Publicación del sitio de documentación estático con el tema Zensical y despliegue automático mediante GitHub Pages.
  - Cobertura completa en los 9 idiomas compatibles con navegación armonizada y capturas de pantalla de la interfaz.
  - Incorporación de 22 pruebas de regresión, alcanzando un total de **610 pruebas** superadas al 100%.

---

## [v1.8.0] - 2026-09-13

### 📢 Tarjeta de promoción de ATBCmder y distintivo [AD] en la barra lateral
- **Ecosistema de productividad e interfaz**:
  - Incorporación de una tarjeta de promoción adaptativa para ATBCmder (`https://aitobox.com/atbcmder`) en el espacio flexible de la barra lateral de navegación.
  - Diseño nativo de macOS con contenedor redondeado translúcido, etiqueta identificativa publicitaria `[AD]`, icono de aplicación de alta resolución, subtítulo multilingüe y botón de enlace externo en el navegador.
  - Integración completa en el sistema i18n de 9 idiomas, con actualización dinámica instantánea de título, subtítulo y botón de acción al cambiar el idioma en los ajustes.
  - Asistente de resolución de recursos para `ATBCmderIcon.png` / `.icns` con gestión de rutas de respaldo.

### 🛡️ Preservación de notas de versión en CI/CD y robustecimiento del empaquetado
- **Estabilidad de la automatización de publicaciones**:
  - Corrección de un problema por el cual la limpieza del directorio `dist/` en `build_cli.sh` eliminaba `dist/release_notes.md` antes de subirse a GitHub Releases.
  - Implementación de copia de seguridad y restauración automática de notas de versión en `scripts/build_release_packages.sh`.
  - Generación de respaldo en `.github/workflows/release.yml` mediante anotaciones de etiquetas Git e historial de commits para garantizar notas de versión completas.

### 🧪 Aseguramiento de la calidad y pruebas automáticas
- **Ampliación de la suite de pruebas**:
  - Conjunto de pruebas ampliado a 588 pruebas con una tasa de éxito del 100%, cubriendo el diseño de la tarjeta lateral, gestión de enlaces externos, reactividad multilingüe y scripts de publicación.

---

## [v1.7.0] - 2026-09-13

### 🔄 Subsistema de actualización automática integrada e instalación silenciosa
- **Actualización automática de extremo a extremo**:
  - Implementación de `UpdateService` para consultar automáticamente el manifiesto de GitHub `latest.json` y detectar nuevas versiones mediante versionado semántico.
  - Descarga según la arquitectura (Apple Silicon arm64 e Intel x86_64) con transferencia por bloques y visualización del porcentaje de progreso en tiempo real.
  - Verificación automática de la suma de comprobación SHA256 contra el manifiesto antes de la instalación para prevenir archivos dañados o alterados.
  - Compatibilidad completa con servidores proxy configurados (`HTTP_PROXY`, `HTTPS_PROXY`, `ALL_PROXY`) para garantizar la actualización en redes restringidas.
  - Instalación silenciosa: montaje automático del DMG en una carpeta temporal aislada, sustitución de `ATBClone.app`, eliminación de atributos de cuarentena de macOS Gatekeeper (`xattr -cr`) y desmontaje seguro del volumen.

### ⚙️ Flujo interactivo de actualización en la vista de ajustes
- **Gestión visual de actualizaciones**:
  - Incorporación del botón «Buscar actualizaciones» e indicador de estado en tiempo real en `SettingsView`.
  - Transición visual de estados: Comprobando → Actualización disponible (con versión y notas de la versión) / Ya está actualizado → Descargando (progreso en %) → Instalando → Completado / Solicitud de reinicio.
  - Mensajes de error claros ante tiempos de espera de red, fallos HTTP o discrepancias en las sumas de comprobación.

### 🌐 Traducción completa a 9 idiomas
- **Cobertura total de i18n**:
  - Traducción de todos los controles, etiquetas de estado y mensajes de diálogo del flujo de actualización en los 9 idiomas disponibles.

### 📦 Generación del manifiesto de versiones en CI/CD (`latest.json`)
- **Metadatos de lanzamiento automatizados**:
  - Actualización de `scripts/build_release_packages.sh` para extraer notas de versión, calcular sumas SHA256 de los DMG y generar `dist/latest.json`.
  - Integración en `.github/workflows/release.yml` para publicar `latest.json` en GitHub Releases con reintentos automáticos.

### 🧪 Aseguramiento de la calidad y pruebas
- **Ampliación de la suite de pruebas**:
  - Conjunto de pruebas ampliado a 585 pruebas automatizadas con una tasa de éxito del 100 %.

---

## [v1.6.0] - 2026-09-13

### 🪟 Eliminación del bloqueo al salir desde la bandeja del sistema y estabilización del cierre
- **Terminación fiable y limpia del proceso**:
  - Corrección de un bloqueo mutuo (deadlock) que impedía que la aplicación se cerrara al hacer clic en «Salir» desde el icono de la bandeja del sistema o el menú contextual del Dock mientras estaba minimizada.
  - Incorporación del indicador de protección `_is_exiting` en `ATBCloneApp`, asegurando que `_on_window_close` no intercepte ni bloquee la secuencia de cierre.
  - Eliminación de la llamada prematura a `set_macos_dock_visible(True)` en `exit_application()`, evitando transiciones de políticas de activación en el bucle de eventos de Cocoa que provocaban el reingreso al cierre de ventana.
  - Refuerzo en las rutas de salida tanto desde el Dock (`_on_app_exit`) como desde la bandeja (`exit_application`), garantizando la desactivación inmediata del icono y un cierre fluido.

---

## [v1.5.1] - 2026-09-13

### 💬 Receta integrada para KakaoTalk
- **Soporte nativo para múltiples instancias**:
  - Incorporación de la receta integrada para KakaoTalk (`com.kakao.KakaoTalkMac`) mediante clonación dura Cocoa, eliminación de sandbox y directorios de datos aislados (`HOME`/`TMPDIR`).
  - Ampliación de la biblioteca de recetas integradas a más de 34 aplicaciones.
  - Detalle del alcance de verificación en la documentación (ejecución simultánea y notificaciones verificadas).

### 🚀 Flujo automatizado de lanzamiento en GitHub Actions arm64
- **Integración continua y empaquetado de versiones**:
  - Creación de `.github/workflows/release.yml` para generar artefactos de versión automáticamente al enviar etiquetas (`v*`).
  - Compilación y empaquetado del archivo CLI (`ATBCloneCli-arm64.tar.gz`) y del instalador GUI (`ATBClone-*.dmg`) junto con sumas de comprobación SHA256.
  - Incorporación del script unificado `scripts/build_release_packages.sh`.
  - Corrección del error de bash `set -u` al expandir matrices vacías en `scripts/build_cli.sh` y `scripts/build_release_packages.sh`.

### 🛡️ Estructura de compilación GUI y resiliencia de red
- **Recuperación automática de compilaciones incompletas**:
  - Mejora en las verificaciones de integridad de `scripts/build_gui.sh` comprobando `Python.framework`, el ejecutable `ATBClone` y `Stub`.
  - Limpieza y recreación automática de estructuras incompletas derivadas de descargas interrumpidas.

### 🔒 Política de seguridad (SECURITY.md)
- **Divulgación responsable de vulnerabilidades**:
  - Publicación de `.github/SECURITY.md` con los canales para reportar vulnerabilidades de forma privada, plazos de respuesta y alcance.

### 🧪 Aseguramiento de calidad y pruebas
- **Ampliación de pruebas**:
  - Conjunto de pruebas automatizadas ampliado a 561 pruebas con un 100 % de éxito.

---

## [v1.5.0] - 2026-09-10

### 🔐 Autenticación de proxy y almacenamiento seguro en Keychain
- **Soporte para proxies autenticados e integración con el llavero de macOS**:
  - Adición de los campos `username` y `password` en el modelo `ProxyConfig`, admitiendo proxies SOCKS5 y HTTP con autenticación.
  - Implementación del módulo `atbclone.core.keychain` para almacenar de forma segura las contraseñas de proxy en el llavero del sistema macOS (Keychain Services / CLI `security`), evitando el almacenamiento en texto plano en archivos de configuración.
  - Nuevas opciones de CLI `--proxy-username` y `--proxy-password` con solicitud interactiva y segura de contraseña en los comandos `clone`, `update` y `wizard`.
  - Integración de campos de credenciales de proxy, alternancia de visibilidad de contraseña y control de Keychain en el asistente gráfico (`WizardWindow`), la ventana de edición (`CloneEditWindow`) y la configuración general (`SettingsView`).
  - Ocultación sistemática de credenciales (`redact_url_credentials`) en `clone_inspector`, la lista de la CLI y las vistas de la GUI para evitar filtraciones en la consola o los registros.

### 🛠️ Adaptación automática de la cadena de compilación de Xcode / CLT
- **Detección dinámica y vinculación con el SDK**:
  - Implementación del mecanismo dinámico `_resolve_clang_command` en `CloneEngine`.
  - Vinculación automática mediante `xcrun --sdk macosx clang` con el sysroot del SDK de macOS activo, solucionando fallos de compilación y enlace derivados de discrepancias de arquitectura (como `arm64e.x1-macos`) en versiones beta de Xcode y Command Line Tools.

### 💼 Receta integrada para WeCom (Enterprise WeChat)
- **Compatibilidad multinstancia lista para usar**:
  - Adición de la receta integrada para Enterprise WeChat / WeCom (`com.tencent.WeWorkMac`) con aislamiento del directorio de datos e inyección de variables de entorno.

### 🛡️ Refuerzo de seguridad y defensa contra inyecciones shell
- **Validación centralizada y protección contra eliminaciones accidentales**:
  - Introducción del módulo `atbclone.validation` con lista blanca estricta para Bundle IDs (`^[A-Za-z0-9][A-Za-z0-9._-]*$`), validación de variables de entorno, parámetros de proxy y prevención de salto de directorio (Path Traversal).
  - Activación de `validate_assignment = True` en los modelos `Recipe` y `ProxyConfig` para evitar eludir la validación mediante asignación directa.
  - Establecimiento de `CloneTask.__post_init__` como punto central de validación de seguridad en la CLI, la GUI y las actualizaciones.
  - Incorporación del guardián de eliminación (`validate_deletion_target`), que impide el borrado de directorios del sistema (`/System`, `/usr`, `/Library`), la raíz de `$HOME`, rutas de poca profundidad o destinos que no sean `.app`.
  - Aplicación forzada de permisos POSIX `0600` en `clones.yaml`.
  - Blindaje de scripts shell en los motores de clonación mediante `shlex.quote` y escape riguroso de metacaracteres (`$`, comillas invertidas, comillas dobles).

### 🧪 Automatización de CI y aseguramiento de la calidad
- **Integración continua y cobertura de pruebas**:
  - Incorporación del flujo de CI en GitHub Actions (`.github/workflows/test.yml`) para macOS (limitado a Python 3.12).
  - Plantilla estándar de Pull Request e insignias de estado de CI en la documentación.
  - Ampliación del conjunto de pruebas automatizadas a 554 pruebas con una tasa de éxito del 100 %.

---

## [v1.4.0] - 2026-09-05

### 🪶 Aislamiento multinstancia y bloqueo de procesos para Feishu / Lark (Fix #7)
- **Redirección de datos y bloqueo de singleton privado**:
  - Dylib especializada (`libatbclone_feishu_hook.dylib`) para interceptar rutas Cocoa y POSIX en Feishu/Lark (`com.electron.lark`).
  - Intercepta `NSSearchPathForDirectoriesInDomains` para crear `LarkShell`, `SingletonLock` y `SingletonSocket` en el directorio de datos privado del clon.
  - Eliminación automática de `CFBundleURLTypes` en `Info.plist` para prevenir conflictos con esquemas URL del sistema.
  - Limitado estrictamente a recetas de Feishu/Lark sin impacto en otras aplicaciones.

### 🤖 Aislamiento de cuentas para OpenAI ChatGPT Desktop y Codex
- **Sesiones de inicio de sesión independientes y saneamiento de enlaces**:
  - Incorporación del parche `patch_chatgpt_isolation` e inyección de `libatbclone_chatgpt_hook.dylib` para ChatGPT Desktop (`com.openai.chat`).
  - Corrección en la inicialización de `CODEX_HOME` (eliminada la copia involuntaria de `~/.codex/auth.json`), garantizando la independencia de tokens de sesión.
  - Eliminación de `CFBundleURLTypes` en clones de ChatGPT para evitar conflictos de activación externa.

### 📦 Calidad garantizada
- **Cobertura exhaustiva**:
  - Suite de pruebas ampliada a 485 casos automatizados con un 100 % de éxito.

---

## [v1.3.0] - 2026-09-05

### 🔬 Verificación de espacio en encabezado Mach-O (Headroom Probing)
- **Inspección estática de binarios**:
  - Incorporación de `_check_macho_injection_headroom` para comprobar el margen de espacio entre comandos de carga (`sizeofcmds`) y la primera sección antes de modificar el binario.
  - Evita daños irreparables en binarios Mach-O con encabezados compactos.

### 🎛️ Estrategia de inyección configurable (`auto`, `dylib`, `launcher`)
- **Control integral de inyección y degradación fluida**:
  - Incorporación de `injection_strategy` en modelos de receta, CloneTask, CloneRecord, CLI (`--injection-strategy`) e interfaz gráfica (asistente y editor de recetas).
  - **Modo automático (`auto`)**: Analiza el margen de Mach-O; inyecta la biblioteca dylib si es seguro o recurre automáticamente al lanzador nativo C con aviso informativo.
  - **Modo dylib (`dylib`)**: Impone la inyección de dylib, emitiendo un error `CloneError` detallado si el espacio es insuficiente.
  - **Modo lanzador (`launcher`)**: Fuerza el uso del lanzador nativo C Mach-O sin modificar el binario original.
  - Visualización del modo ejecutado en tiempo real en `CloneDetailWindow` y en el comando `inspect`.

### 📚 Documentación exhaustiva
- **Guías técnicas y manuales actualizados**:
  - Guías en `docs/guide/` y README enriquecidas con detalles sobre estrategias de inyección, arquitectura dylib y verificación de encabezados.

### 📦 Calidad garantizada
- **Cobertura exhaustiva**:
  - Suite de pruebas ampliada a 479 casos automatizados con un 100 % de éxito.

---

## [v1.2.1] - 2026-09-05

### 🧩 Inyección de Dylib desacoplada mediante @executable_path (Fix #6)
- **Mayor estabilidad en la interceptación dinámica**:
  - Actualización de la ruta de la biblioteca en `HardCloneEngine` de `@rpath` a `@executable_path/../Frameworks/libatbclone_env.dylib`.
  - Desacoplamiento total respecto a la lista `LC_RPATH` del ejecutable destino, evitando fallos de dyld en aplicaciones con rpaths no estándar o recortados (como WeChat 4.x).
  - Creación automática de enlaces simbólicos de respaldo en `Contents/Frameworks/ld/` cuando dicha estructura existe.

### ⚙️ Sincronización automática de Info.plist y artefactos intermedios
- **Alineación íntegra de versiones**:
  - Mejora de `scripts/manage_version.py` con `PlistVersionTarget` mediante `plistlib` para sincronizar automáticamente `Info.plist` (`CFBundleShortVersionString` y `CFBundleVersion`) y `welcome.html`.
  - Inspección de artefactos intermedios y aviso `[OUT OF SYNC]` en `scripts/manage_version.py --show`.
  - Protección en `scripts/build_gui.sh` para garantizar que la versión del instalador y del paquete coincidan con `pyproject.toml`.

### 📦 Calidad garantizada
- **Cobertura exhaustiva**:
  - Suite de pruebas ampliada a 468 casos automatizados con un 100 % de éxito.

---

## [v1.2.0] - 2026-09-02

### 🔔 Inyección nativa de Dylib para notificaciones de macOS e iconos en la barra de menús
- **Corrección de notificaciones y elementos de la barra de estado (Fix #5)**:
  - Habilitación de la inyección de bibliotecas dinámicas Mach-O (`.dylib`) en `HardCloneEngine`.
  - Intercepción de las API NSUserNotificationCenter y NSStatusItem, restaurando los avisos de notificación y los iconos de la barra de menús en los clones físicos.

### 🌓 Adaptación dinámica al modo oscuro y mejoras visuales
- **Seguimiento del aspecto del sistema (Fix #4)**:
  - Detección en tiempo real de cambios en el aspecto del sistema (claro / oscuro) para una adaptación fluida de la interfaz.
- **Diseño de cuadrícula y contraste de texto**:
  - Optimización del espaciado de tarjetas y ampliación del ancho predeterminado de la ventana.
  - Mejora notable del contraste de texto en las ventanas de registros y notas de la versión (conforme a WCAG 2.1 AA).

### 📖 Documentación y capturas de pantalla
- **Actualización de rutas estándar**:
  - Actualización de la ruta de instalación predeterminada en la documentación a `~/ATBClone/Apps`.
  - Nuevas capturas de pantalla de alta resolución en la documentación.

### 📦 Calidad garantizada
- **Cobertura exhaustiva**:
  - Suite de pruebas ampliada a 462 casos automatizados con un 100 % de éxito.

---

## [v1.1.1] - 2026-08-30

### 🧹 Depuración automática de versiones obsoletas de Frameworks
- **Optimización de espacio en disco y validación de firma**:
  - `HardCloneEngine` purga automáticamente versiones inactivas en `Contents/Frameworks/*.framework/Versions/` (restos de actualizaciones de Google Chrome o Electron).
  - Elimina el error `embedded framework contains modified or invalid version` durante la verificación de firmas y ahorra cientos de megabytes por clon.

### 🛡️ Limpieza profunda de autorizaciones con Python plistlib
- **Extracción atómica y filtrado exhaustivo de permisos**:
  - Uso de rutas temporales atómicas (`${TMPDIR:-/tmp}/atb_ent_XXXXXX`) para extraer los entitlements de manera segura.
  - Combinación de `PlistBuddy` y Python `plistlib` para eliminar prefijos restringidos (`com.apple.developer.`, `keychain-access-groups`, `com.apple.security.application-groups`, `com.apple.security.app-sandbox`).
  - Firma profunda multietapa en bibliotecas dinámicas, ejecutables Mach-O, frameworks y subprocesos auxiliares.

### 📦 Calidad garantizada
- **Cobertura exhaustiva**:
  - Suite de pruebas ampliada a 455 casos automatizados con un 100 % de éxito.

---

## [v1.1.0] - 2026-08-29

### 🤖 Soporte integral para clientes de IA y herramientas LLM
- **Multi-instancia en Claude Desktop y Claude Code**:
  - Inyección automática de `CLAUDE_CONFIG_DIR`, replicación y aislamiento de `~/.claude` y `~/.claude.json`.
  - Preservación de `CFBundleName` para garantizar la correcta vinculación de los procesos auxiliares de Claude.
- **Ecosistema Google Antigravity y Gemini**:
  - Inyección de variables `GEMINI_HOME` y `ANTIGRAVITY_HOME` para aislar `~/.gemini`.
- **OpenAI ChatGPT y Codex CLI**:
  - Inyección de `CODEX_HOME` y replicación de `~/.codex` para uso simultáneo con múltiples cuentas.

### 🔑 Enlace simbólico automático al Llavero de macOS (Keychains)
- **Protección de credenciales y prevención de bloqueos**:
  - Creación automática de enlaces simbólicos a `Library/Keychains` cuando se redirige la variable `HOME`.

### 🛡️ Sanitización de autorizaciones AMFI y firma segura
- **Compatibilidad con macOS Sonoma y Sequoia**:
  - Eliminación automática de entitlements restringidos de equipo durante la re-firma Ad-Hoc.
  - Prevención de terminaciones forzadas `SIGKILL` por parte de Apple Mobile File Integrity (AMFI).

### 🚀 Generalización del parche ProcessSingleton en Mach-O
- **Soporte multi-instancia en aplicaciones Electron e IA**:
  - Generalización del parche de ProcessSingleton e inyección de `--user-data-dir` en recetas de clientes de IA.

### 📦 Calidad garantizada
- **Cobertura exhaustiva**:
  - Suite de pruebas ampliada a 453 casos automatizados con un 100 % de éxito.

---

## [v1.0.2] - 2026-08-26

### 🛡️ Optimización de eliminación de Sandbox y estabilidad de Hard Clone
- **Eliminación de Sandbox en Hard Clones (`strip_sandbox: true`)**:
  - Activación de eliminación de sandbox en recetas Hard Clone para evitar bloqueos y conflictos de permisos en paquetes Mach-O modificados.
  - Optimización de la receta para WeChat con inicialización garantizada de directorios en tiempo de ejecución (`Caches`, `Containers`, `Preferences`).

### 📚 Depuración de recetas y documentación de limitaciones
- **Ajuste de recetas integradas**:
  - Eliminación de la receta experimental para WeCom debido a restricciones IPC propietarias de CEF, añadiendo detalles en la guía de solución de problemas.
  - Actualización de directrices para la creación y configuración de recetas personalizadas.

### 📦 Calidad garantizada
- **Cobertura exhaustiva**:
  - 443 pruebas automatizadas completadas con un 100 % de éxito.

---

## [v1.0.1] - 2026-08-26

### 🎨 Cumplimiento de Apple Design HIG y mejoras visuales
- **Alineación con las directrices de interfaz humana de macOS**:
  - Auditoría integral de Apple Design HIG en todas las ventanas y diálogos.
  - Eliminación de emojis decorativos en favor de una tipografía nativa SF Pro y jerarquía visual limpia.
  - Resaltado nativo de Cocoa en la barra lateral de navegación.
  - Contraste optimizado en modos claro y oscuro conforme al estándar WCAG 2.1 AA.
  - Mejora en pantallas vacías, sombras de tarjetas, arrastre de ventanas y espaciado.

### 📜 Registros en orden cronológico inverso y diseño fluido
- **Diagnóstico en tiempo real (`LogsView`)**:
  - Los registros se muestran en orden cronológico inverso (los más recientes arriba) para agilizar la depuración.
  - Eliminación de anchos fijos en los botones «Actualizar» y «Examinar», evitando el corte de texto en diversos idiomas.

### 🛡️ Mayor resistencia del motor de clonación y manejo de xattr
- **Permisos de escritura y tolerancia a fallos en atributos extendidos**:
  - Asegura permisos de escritura (`chmod -R u+w`) en el paquete clonado antes de modificar el Mach-O y firmar.
  - Tolerancia a errores al limpiar atributos extendidos (`xattr -cr`) en instantáneas de solo lectura o archivos protegidos.

### 📦 Calidad garantizada
- **Cobertura exhaustiva**:
  - Suite de pruebas ampliada a 443 casos automatizados con un 100 % de éxito.

---

## [v1.0.0] - 2026-08-24

### 🚀 Lanzamiento oficial de la versión 1.0.0
- **Ecosistema maduro de clonación de aplicaciones en macOS**:
  - ATBClone alcanza la versión 1.0.0, consolidando una solución completa y de alto rendimiento para macOS (Apple Silicon e Intel).
  - Arquitectura de doble motor: Soft Clone (sin consumo de espacio en disco) y Hard Clone (aislamiento absoluto de datos, binarios Mach-O y sandbox).

### 🧬 Parche avanzado para CEF y compatibilidad con WeCom
- **Ejecución multi-instancia en aplicaciones híbridas**:
  - Parcheo binario específico para Chromium Embedded Framework (CEF) enfocado en aplicaciones complejas como WeCom (企业微信).
  - Corrección de bloqueos críticos de `GpuDataManager` en subprocesos auxiliares y serialización de identificadores de Helper (`.helper.atbclone.X`).
  - Listas blancas de enlaces simbólicos y eliminación de colisiones internas de sandbox.

### 🛡️ Re-firma recursiva integral y neutralización de ProcessSingleton
- **Firma profunda de binarios y dependencias**:
  - `HardCloneEngine` vuelve a firmar de forma recursiva todos los binarios, Frameworks, procesos Helper, servicios XPC y dylibs.
  - Preservación de privilegios JIT y Hardened Runtime con extracción limpia de entitlements en `/tmp`.
- **Desactivación de bloqueo de instancia única**:
  - Parámetro `patch_framework_singleton` en recetas para eliminar el bloqueo de ProcessSingleton directamente en el binario Mach-O.

### 📋 Ventana de detalles mejorada e integración con el portapapeles
- **Exportación de diagnósticos**:
  - `CloneDetailWindow` incorpora vistas de texto multilínea de Cocoa y `NSPasteboard` para seleccionar y copiar información de diagnóstico al instante.

### 📦 Calidad garantizada
- **Cobertura exhaustiva**:
  - Ampliación de la suite de pruebas a 441 casos automatizados con un 100 % de éxito.

---

## [v0.9.9] - 2026-08-24

### 📋 Texto seleccionable y «Copiar toda la información» en la ventana de detalles
- **Copia y exportación interactiva**:
  - Activación del modo de texto seleccionable nativo de Cocoa (`setSelectable_`) en `CloneDetailWindow`.
  - Incorporación del botón «Copiar toda la información» para copiar un resumen de diagnóstico completo en Markdown al portapapeles.

### 🎨 Diseño visual nativo de macOS y ajuste de espaciados
- **Optimización de temas y tarjetas**:
  - Ajuste fino de la paleta de colores en `Theme` para los modos claro y oscuro (`BG_APP`, `BG_CARD`, `BG_HOVER`, `BORDER`, `TEXT_PRIMARY`, `TEXT_MUTED`, `ACCENT`).
  - Estandarización de bordes redondeados, márgenes y espaciado de controles en todas las ventanas.

### 📖 Manual de usuario multilingüe completo (`docs/guide/`)
- **Documentación exhaustiva**:
  - Publicación del manual de usuario completo en inglés (`docs/guide/en/`) y chino (`docs/guide/zh-cn/`).
  - Incluye el Capítulo 1 (Operaciones básicas), Capítulo 2 (Recetas personalizadas), Capítulo 3 (Arquitectura interna) y Capítulo 4 (Preguntas frecuentes y diagnóstico).

### 📦 Pruebas integrales
- **Ampliación de pruebas**:
  - Conjunto de pruebas ampliado a 431 pruebas automatizadas.

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
