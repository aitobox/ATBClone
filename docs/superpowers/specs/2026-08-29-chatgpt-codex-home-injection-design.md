# Design Spec: ChatGPT Codex CODEX_HOME Injection & ~/.codex Data Replication

## Problem Statement
When running clones of ChatGPT / Codex desktop applications (`com.openai.codex` and `com.openai.chat`), the clone processes need an isolated `CODEX_HOME` directory to prevent session, auth, or configuration conflicts with the host system or other clone instances. Additionally, for a seamless user experience, newly created clone instances should initialize with a copy of existing configuration and state from the host default `~/.codex` directory, while keeping subsequent changes fully isolated in the clone's dedicated `CODEX_HOME` directory.

## Scope & Requirements
1. **Builtin Recipe Enhancement**:
   - Update `src/atbclone/recipes/builtin/com.openai.codex.yaml` and `src/atbclone/recipes/builtin/com.openai.chat.yaml` to include `CODEX_HOME: '{{ATB_DATA_DIR}}/Codex'` in `environment_injection`.
2. **Clone Engine & Wrapper Enhancements**:
   - **Creation-time initialization**: During clone creation (in `HardCloneEngine` / `SoftCloneEngine`), if `CODEX_HOME` is present in the recipe's injected environment (or data directory targets `Codex`), copy existing files from host `~/.codex` to the target `<data_dir>/Codex` folder if `~/.codex` exists.
   - **Runtime wrapper safety**: In the generated App executable wrapper script, ensure `$CODEX_HOME` is created and populated on first launch if not already initialized, without overwriting existing clone data on subsequent launches.
3. **Automated Verification**:
   - Unit tests for recipe loading, environment variable injection, and script generation.
   - Full test suite regression pass.

## Technical Architecture

### 1. Builtin Recipes Configuration
The builtin recipes `com.openai.codex.yaml` and `com.openai.chat.yaml` will be structured as follows:

```yaml
bundle_id: com.openai.codex # and com.openai.chat
app_name: ChatGPT
strategy: hard_clone
app_type: cocoa
strip_sandbox: true
environment_injection:
  HOME: '{{ATB_DATA_DIR}}/Home'
  TMPDIR: '{{ATB_DATA_DIR}}/Tmp'
  CODEX_HOME: '{{ATB_DATA_DIR}}/Codex'
```

### 2. Clone Engine Script Generation (`src/atbclone/core/engines.py`)

#### A. Creation Script Enhancement
During clone execution (`execute` method of `HardCloneEngine` and `SoftCloneEngine`), if `CODEX_HOME` is configured in `effective_env`:
- Compute the destination directory for `CODEX_HOME` (replacing `{{ATB_DATA_DIR}}` with `task.data_dir`).
- Append a shell command to ensure the target directory is created and copy existing `~/.codex` files if present:
```bash
if [ -d "$HOME/.codex" ] && [ ! -d "<resolved_codex_home>" ]; then
    mkdir -p "<resolved_codex_home>"
    cp -R "$HOME/.codex/." "<resolved_codex_home>/" 2>/dev/null || true
fi
```

#### B. Executable Wrapper Shell Script Enhancement
In the generated wrapper script:
- `export CODEX_HOME=...` is emitted via `effective_env`.
- A startup verification snippet is added to guarantee initialization even if data directories are created out-of-band:
```bash
if [ -n "$CODEX_HOME" ] && [ "$CODEX_HOME" != "$REAL_USER_HOME/.codex" ]; then
    mkdir -p "$CODEX_HOME" 2>/dev/null || true
    if [ -d "$REAL_USER_HOME/.codex" ] && [ -z "$(ls -A "$CODEX_HOME" 2>/dev/null)" ]; then
        cp -R "$REAL_USER_HOME/.codex/." "$CODEX_HOME/" 2>/dev/null || true
    fi
fi
```

### 3. Testing & Verification

- **`tests/test_recipes.py`**:
  - Verify `com.openai.codex` and `com.openai.chat` recipes contain `CODEX_HOME` in `environment_injection`.
- **`tests/test_engines.py`**:
  - Test that `HardCloneEngine` and `SoftCloneEngine` generate wrapper scripts containing `CODEX_HOME` export and `~/.codex` replication snippet.
  - Test clone creation command generation contains the creation-time copy logic.
- **Regression Testing**:
  - Run `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/` to ensure all existing test suites pass.
