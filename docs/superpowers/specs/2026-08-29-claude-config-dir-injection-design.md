# Design Spec: Claude Desktop & Claude Code CLAUDE_CONFIG_DIR Injection & ~/.claude Data Replication

## Problem Statement
When creating and running clones of Claude Desktop / Claude Code (`com.anthropic.claudefordesktop`), the clone processes need an isolated directory for configurations, authentication, and session storage via the `CLAUDE_CONFIG_DIR` environment variable. In addition, new clone instances should be bootstrapped with existing configuration from the host default `~/.claude` directory without mutating the host's original directory or other clones.

## Scope & Requirements
1. **Builtin Recipe Enhancement**:
   - Update `src/atbclone/recipes/builtin/com.anthropic.claudefordesktop.yaml` to include:
     - `CLAUDE_CONFIG_DIR: '{{ATB_DATA_DIR}}/Claude'`
2. **Clone Engine & Wrapper Enhancements**:
   - **Creation-time initialization**: During clone creation (`HardCloneEngine` / `SoftCloneEngine`), if `CLAUDE_CONFIG_DIR` is present in the recipe's injected environment, copy existing files from host `~/.claude` to the target `<data_dir>/Claude` directory if `~/.claude` exists.
   - **Runtime wrapper safety**: In the generated App executable wrapper script, ensure `$CLAUDE_CONFIG_DIR` is created and populated on first launch if empty, while preserving existing clone data across subsequent launches.
3. **Automated Verification**:
   - Recipe tests in `tests/test_recipes.py`.
   - Engine script generation tests in `tests/test_engines.py`.
   - Full regression suite execution.

## Technical Architecture

### 1. Builtin Recipe Configuration
The builtin recipe `com.anthropic.claudefordesktop.yaml` will include:

```yaml
bundle_id: com.anthropic.claudefordesktop
app_name: Claude
strategy: hard_clone
app_type: electron
strip_sandbox: true
environment_injection:
  HOME: '{{ATB_DATA_DIR}}/Home'
  TMPDIR: '{{ATB_DATA_DIR}}/Tmp'
  CLAUDE_CONFIG_DIR: '{{ATB_DATA_DIR}}/Claude'
```

### 2. Clone Engine Script Generation (`src/atbclone/core/engines.py`)

#### A. Creation-Time Data Initialization
In `CloneEngine._build_claude_init_cmd(effective_env, data_dir)`:
- Check if `CLAUDE_CONFIG_DIR` is present in `effective_env`.
- Resolve the target path (`{{ATB_DATA_DIR}}` -> `data_dir`).
- Generate shell commands to copy `~/.claude/.` to the target path if `~/.claude` exists and target directory does not yet exist.

```bash
if [ -d "$HOME/.claude" ] && [ ! -d "<resolved_claude_path>" ]; then
    mkdir -p "<resolved_claude_path>"
    cp -R "$HOME/.claude/." "<resolved_claude_path>/" 2>/dev/null || true
fi
```

#### B. Runtime Executable Wrapper Script
In `wrapper_lines`:
```bash
if [ -n "$CLAUDE_CONFIG_DIR" ] && [ "$CLAUDE_CONFIG_DIR" != "$REAL_USER_HOME/.claude" ]; then
    mkdir -p "$CLAUDE_CONFIG_DIR" 2>/dev/null || true
    if [ -d "$REAL_USER_HOME/.claude" ] && [ -z "$(ls -A "$CLAUDE_CONFIG_DIR" 2>/dev/null)" ]; then
        cp -R "$REAL_USER_HOME/.claude/." "$CLAUDE_CONFIG_DIR/" 2>/dev/null || true
    fi
fi
```

### 3. Testing & Verification
- `tests/test_recipes.py`: Check `com.anthropic.claudefordesktop` contains `CLAUDE_CONFIG_DIR`.
- `tests/test_engines.py`: Verify creation-time script and runtime wrapper snippets for both `HardCloneEngine` and `SoftCloneEngine`.
- Full pytest regression suite.
