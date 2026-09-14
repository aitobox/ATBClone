# Глава 3: Внутреннее устройство & Расширенные параметры

Низкоуровневая архитектура ATBClone, технология Binary Wrapper Hijack и динамические макросы.

---

## 📑 Содержание

- [Сравнение: Soft и Hard клоны](#сравнение-soft-и-hard-клоны)
- [3 ключевые технологии Hard Clone](#3-ключевые-технологии-hard-clone)
  - [1. Изменение Bundle ID](#1-изменение-bundle-id)
  - [2. Перехват бинарной обертки (Wrapper Hijack)](#2-перехват-бинарной-обертки-wrapper-hijack)
  - [3. Удаление песочницы и локальная переподпись](#3-удаление-песочницы-и-локальная-переподпись)
- [Расширенные параметры YAML](#расширенные-параметры-yaml)

---

## ⚡ 3 ключевые технологии Hard Clone

### 1. Изменение Bundle ID
В `Info.plist` прописывается уникальный `CFBundleIdentifier`, благодаря чему macOS обрабатывает клон как отдельное приложение.

### 2. Перехват бинарной обертки (Wrapper Hijack)
1. Реальный исполняемый файл переименовывается в `<App>.real`.
2. На его место помещается POSIX shell-скрипт, переопределяющий переменные окружения:
   * `export HOME="<КаталогДанных>"`
   * `export TMPDIR="<КаталогДанных>/tmp"`
   * `export XDG_DATA_HOME="<КаталогДанных>/Library/Application Support"`
3. Скрипт запускает бинарный файл `.real`.

### 3. Удаление песочницы и локальная переподпись
Из прав удаляется флаг `com.apple.security.app-sandbox`, после чего бандл переподписывается командой `codesign -f -s -`.

---

## ⚙️ Расширенные параметры YAML

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

* Доступные макросы: `{DATA_DIR}`, `{CLONE_NAME}`, `{BUNDLE_ID}`, `{HOST_APP}`.
