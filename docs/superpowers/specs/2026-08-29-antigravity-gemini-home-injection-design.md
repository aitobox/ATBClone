# Design Spec: Antigravity & Gemini Family GEMINI_HOME / ANTIGRAVITY_HOME Injection & ~/.gemini Data Replication

## Problem Statement
When creating and running clones of Google Antigravity, Antigravity IDE, and Gemini desktop apps (`com.google.antigravity`, `com.google.antigravity-ide`, and `com.google.GeminiMacOS`), the clone processes need an isolated directory for configurations, extensions, skills, and session storage. In addition, new clone instances should be bootstrapped with existing configuration from the host default `~/.gemini` directory without mutating the host's original directory or other clones.

## Scope & Requirements
1. **Builtin Recipe Enhancement**:
   - Update `com.google.antigravity.yaml`, `com.google.antigravity-ide.yaml`, and `com.google.GeminiMacOS.yaml` to include:
     - `GEMINI_HOME: '{{ATB_DATA_DIR}}/Gemini'`
     - `GEMINI_CONFIG_DIR: '{{ATB_DATA_DIR}}/Gemini'`
     - `ANTIGRAVITY_HOME: '{{ATB_DATA_DIR}}/Gemini'`
2. **Clone Engine & Wrapper Enhancements**:
   - **Creation-time initialization**: During clone creation (`HardCloneEngine` / `SoftCloneEngine`), if `GEMINI_HOME` / `GEMINI_CONFIG_DIR` / `ANTIGRAVITY_HOME` is present in the recipe's injected environment, copy existing files from host `~/.gemini` to the target `<data_dir>/Gemini` directory if `~/.gemini` exists.
   - **Runtime wrapper safety**: In the generated App executable wrapper script, ensure the target directory is created and populated on first launch if empty, while preserving existing clone data across subsequent launches.
3. **Automated Verification**:
   - Recipe tests in `tests/test_recipes.py`.
   - Engine script generation tests in `tests/test_engines.py`.
   - Full regression suite execution.

## Technical Architecture

### 1. Builtin Recipes Configuration
The builtin recipes `com.google.antigravity.yaml`, `com.google.antigravity-ide.yaml`, and `com.google.GeminiMacOS.yaml` will include:

```yaml
environment_injection:
  HOME: '{{ATB_DATA_DIR}}/Home'
  TMPDIR: '{{ATB_DATA_DIR}}/Tmp'
  GEMINI_HOME: '{{ATB_DATA_DIR}}/Gemini'
  GEMINI_CONFIG_DIR: '{{ATB_DATA_DIR}}/Gemini'
  ANTIGRAVITY_HOME: '{{ATB_DATA_DIR}}/Gemini'
```

### 2. Clone Engine Script Generation (`src/atbclone/core/engines.py`)

#### A. Creation-Time Data Initialization
In `CloneEngine._build_gemini_init_cmd(effective_env, data_dir)`:
- Check if `GEMINI_HOME`, `ANTIGRAVITY_HOME`, or `GEMINI_CONFIG_DIR` is present in `effective_env`.
- If so, resolve the target path (`{{ATB_DATA_DIR}}` -> `data_dir`).
- Generate shell commands to copy `~/.gemini/.` to the target path if `~/.gemini` exists and target directory does not yet exist.

```bash
if [ -d "$HOME/.gemini" ] && [ ! -d "<resolved_gemini_path>" ]; then
    mkdir -p "<resolved_gemini_path>"
    cp -R "$HOME/.gemini/." "<resolved_gemini_path>/" 2>/dev/null || true
fi
```

#### B. Runtime Executable Wrapper Script
In `wrapper_lines`:
```bash
_TARGET_GEMINI_DIR="${GEMINI_HOME:-${ANTIGRAVITY_HOME:-$GEMINI_CONFIG_DIR}}"
if [ -n "$_TARGET_GEMINI_DIR" ] && [ "$_TARGET_GEMINI_DIR" != "$REAL_USER_HOME/.gemini" ]; then
    mkdir -p "$_TARGET_GEMINI_DIR" 2>/dev/null || true
    if [ -d "$REAL_USER_HOME/.gemini" ] && [ -z "$(ls -A "$_TARGET_GEMINI_DIR" 2>/dev/null)" ]; then
        cp -R "$REAL_USER_HOME/.gemini/." "$_TARGET_GEMINI_DIR/" 2>/dev/null || true
    fi
fi
```

### 3. Testing & Verification
- `tests/test_recipes.py`: Check `com.google.antigravity`, `com.google.antigravity-ide`, and `com.google.GeminiMacOS`.
- `tests/test_engines.py`: Verify creation-time script and runtime wrapper snippets for both `HardCloneEngine` and `SoftCloneEngine`.
- Full pytest regression suite.
