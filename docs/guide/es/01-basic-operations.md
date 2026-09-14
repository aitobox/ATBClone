# Capítulo 1: Operaciones básicas & Gestión de clones

![Demostración de la interfaz de ATBClone](assets/images/screenshot-20260821-110121.png)

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
