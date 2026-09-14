# Capítulo 4: Preguntas frecuentes (FAQ), Diagnóstico & Soporte

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
