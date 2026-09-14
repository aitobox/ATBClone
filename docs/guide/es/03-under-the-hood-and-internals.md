# Capítulo 3: Funcionamiento interno & Parámetros avanzados

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
