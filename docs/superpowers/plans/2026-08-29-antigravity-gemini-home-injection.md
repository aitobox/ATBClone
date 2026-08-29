# Antigravity & Gemini Family GEMINI_HOME Injection & ~/.gemini Replication Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Inject `GEMINI_HOME`, `GEMINI_CONFIG_DIR`, and `ANTIGRAVITY_HOME` environment variables into Google Antigravity, Antigravity IDE, and Gemini clone processes (`com.google.antigravity`, `com.google.antigravity-ide`, `com.google.GeminiMacOS`) and automatically replicate host `~/.gemini` configuration files into the clone's custom `Gemini` directory both at clone creation time and on initial launch.

**Architecture:** Update builtin recipes to inject `GEMINI_HOME`, `GEMINI_CONFIG_DIR`, and `ANTIGRAVITY_HOME` pointing to `{{ATB_DATA_DIR}}/Gemini`, update `CloneEngine` (in `src/atbclone/core/engines.py`) with `_build_gemini_init_cmd` and runtime wrapper safety check, and verify via automated pytest suite.

**Tech Stack:** Python 3.12, PySide6/Toga, Pytest, Bash, YAML, Pydantic.

## Global Constraints
- Target macOS native patterns, Python 3.12+ in conda environment `ATBClone`.
- Run tests via `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/`.
- Maintain backward compatibility with all existing recipes and clone engines.
- Do not overwrite existing non-empty `Gemini` directory data on subsequent app launches.

---

### Task 1: Update Builtin Recipes for Antigravity, Antigravity IDE, and Gemini

**Files:**
- Modify: `src/atbclone/recipes/builtin/com.google.antigravity.yaml`
- Modify: `src/atbclone/recipes/builtin/com.google.antigravity-ide.yaml`
- Modify: `src/atbclone/recipes/builtin/com.google.GeminiMacOS.yaml`
- Test: `tests/test_recipes.py`

**Interfaces:**
- Consumes: `RecipeLoader.match(bundle_id)`
- Produces: `recipe.environment_injection["GEMINI_HOME"] == "{{ATB_DATA_DIR}}/Gemini"`, `recipe.environment_injection["GEMINI_CONFIG_DIR"] == "{{ATB_DATA_DIR}}/Gemini"`, `recipe.environment_injection["ANTIGRAVITY_HOME"] == "{{ATB_DATA_DIR}}/Gemini"`

- [ ] **Step 1: Write the failing test for Antigravity & Gemini recipes in `tests/test_recipes.py`**

Add tests to `tests/test_recipes.py`:
```python
def test_load_builtin_antigravity():
    for bid in ["com.google.antigravity", "com.google.antigravity-ide", "com.google.GeminiMacOS"]:
        recipe = RecipeLoader.match(bid)
        assert recipe is not None
        assert recipe.bundle_id == bid
        assert "HOME" in recipe.environment_injection
        assert "TMPDIR" in recipe.environment_injection
        assert recipe.environment_injection.get("GEMINI_HOME") == "{{ATB_DATA_DIR}}/Gemini"
        assert recipe.environment_injection.get("GEMINI_CONFIG_DIR") == "{{ATB_DATA_DIR}}/Gemini"
        assert recipe.environment_injection.get("ANTIGRAVITY_HOME") == "{{ATB_DATA_DIR}}/Gemini"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/test_recipes.py::test_load_builtin_antigravity -v`
Expected: FAIL with `AssertionError: assert None == '{{ATB_DATA_DIR}}/Gemini'`

- [ ] **Step 3: Update `com.google.antigravity.yaml`, `com.google.antigravity-ide.yaml`, and `com.google.GeminiMacOS.yaml`**

In `src/atbclone/recipes/builtin/com.google.antigravity.yaml`:
```yaml
bundle_id: com.google.antigravity
app_name: Antigravity
strategy: hard_clone
app_type: electron
strip_sandbox: true
environment_injection:
  HOME: '{{ATB_DATA_DIR}}/Home'
  TMPDIR: '{{ATB_DATA_DIR}}/Tmp'
  GEMINI_HOME: '{{ATB_DATA_DIR}}/Gemini'
  GEMINI_CONFIG_DIR: '{{ATB_DATA_DIR}}/Gemini'
  ANTIGRAVITY_HOME: '{{ATB_DATA_DIR}}/Gemini'
```

In `src/atbclone/recipes/builtin/com.google.antigravity-ide.yaml`:
```yaml
bundle_id: com.google.antigravity-ide
app_name: Antigravity IDE
strategy: hard_clone
app_type: electron
strip_sandbox: true
environment_injection:
  HOME: '{{ATB_DATA_DIR}}/Home'
  TMPDIR: '{{ATB_DATA_DIR}}/Tmp'
  GEMINI_HOME: '{{ATB_DATA_DIR}}/Gemini'
  GEMINI_CONFIG_DIR: '{{ATB_DATA_DIR}}/Gemini'
  ANTIGRAVITY_HOME: '{{ATB_DATA_DIR}}/Gemini'
```

In `src/atbclone/recipes/builtin/com.google.GeminiMacOS.yaml`:
```yaml
bundle_id: com.google.GeminiMacOS
app_name: Gemini
strategy: hard_clone
app_type: cocoa
strip_sandbox: true
environment_injection:
  HOME: '{{ATB_DATA_DIR}}/Home'
  TMPDIR: '{{ATB_DATA_DIR}}/Tmp'
  GEMINI_HOME: '{{ATB_DATA_DIR}}/Gemini'
  GEMINI_CONFIG_DIR: '{{ATB_DATA_DIR}}/Gemini'
  ANTIGRAVITY_HOME: '{{ATB_DATA_DIR}}/Gemini'
```

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/test_recipes.py -v`
Expected: PASS

- [ ] **Step 5: Commit recipe updates**

```bash
git add src/atbclone/recipes/builtin/com.google.antigravity.yaml src/atbclone/recipes/builtin/com.google.antigravity-ide.yaml src/atbclone/recipes/builtin/com.google.GeminiMacOS.yaml tests/test_recipes.py
git commit -m "feat(recipes): add GEMINI_HOME, GEMINI_CONFIG_DIR, and ANTIGRAVITY_HOME to Antigravity and Gemini recipes"
```

---

### Task 2: Enhance Clone Engines with Creation-Time and Runtime GEMINI_HOME Support

**Files:**
- Modify: `src/atbclone/core/engines.py`
- Test: `tests/test_engines.py`

**Interfaces:**
- Consumes: `task: CloneTask` with `task.recipe.environment_injection`
- Produces: `HardCloneEngine.execute` and `SoftCloneEngine.execute` generating creation script with `~/.gemini` copying and wrapper script with `GEMINI_HOME` / `ANTIGRAVITY_HOME` / `GEMINI_CONFIG_DIR` initialization snippet.

- [ ] **Step 1: Write failing unit tests in `tests/test_engines.py`**

Add tests to `tests/test_engines.py` verifying:
1. When `GEMINI_HOME` is present in `task.recipe.environment_injection`, the generated script in `HardCloneEngine.execute` includes creation-time `cp -R "$HOME/.gemini/."` to the target Gemini path.
2. The generated wrapper script contains `export GEMINI_HOME=...` and the runtime check copying `$REAL_USER_HOME/.gemini` if `_TARGET_GEMINI_DIR` is empty.
3. Test similar behavior for `SoftCloneEngine.execute`.

```python
    def test_hard_clone_gemini_home_script(self, mock_app_info, base_recipe):
        base_recipe.environment_injection = {
            "HOME": "{{ATB_DATA_DIR}}/Home",
            "TMPDIR": "{{ATB_DATA_DIR}}/Tmp",
            "GEMINI_HOME": "{{ATB_DATA_DIR}}/Gemini",
            "GEMINI_CONFIG_DIR": "{{ATB_DATA_DIR}}/Gemini",
            "ANTIGRAVITY_HOME": "{{ATB_DATA_DIR}}/Gemini",
        }
        task = CloneTask(
            source=mock_app_info,
            dest_path=Path("/Applications/TestApp2.app"),
            data_dir=Path("/Users/test/data"),
            recipe=base_recipe,
            clone_name="TestApp2",
            new_bundle_id="com.example.testapp2",
        )
        with patch("atbclone.executor.runner.Runner.run") as mock_run:
            HardCloneEngine.execute(task, needs_admin=False)
            mock_run.assert_called_once()
            script, _ = mock_run.call_args[0]
            assert "export GEMINI_HOME=/Users/test/data/Gemini" in script
            assert "export GEMINI_CONFIG_DIR=/Users/test/data/Gemini" in script
            assert "export ANTIGRAVITY_HOME=/Users/test/data/Gemini" in script
            assert 'if [ -d "$HOME/.gemini" ] && [ ! -d /Users/test/data/Gemini ]; then' in script
            assert 'cp -R "$HOME/.gemini/." /Users/test/data/Gemini/' in script
            assert 'cp -R "$REAL_USER_HOME/.gemini/." "$_TARGET_GEMINI_DIR/"' in script

    def test_soft_clone_gemini_home_script(self, mock_app_info, base_recipe):
        base_recipe.environment_injection = {
            "HOME": "{{ATB_DATA_DIR}}/Home",
            "TMPDIR": "{{ATB_DATA_DIR}}/Tmp",
            "GEMINI_HOME": "{{ATB_DATA_DIR}}/Gemini",
            "GEMINI_CONFIG_DIR": "{{ATB_DATA_DIR}}/Gemini",
            "ANTIGRAVITY_HOME": "{{ATB_DATA_DIR}}/Gemini",
        }
        task = CloneTask(
            source=mock_app_info,
            dest_path=Path("/Applications/TestApp2.app"),
            data_dir=Path("/Users/test/data"),
            recipe=base_recipe,
            clone_name="TestApp2",
            new_bundle_id="com.example.testapp2",
        )
        with patch("atbclone.executor.runner.Runner.run") as mock_run:
            SoftCloneEngine.execute(task, needs_admin=False)
            mock_run.assert_called_once()
            script, _ = mock_run.call_args[0]
            assert "export GEMINI_HOME=/Users/test/data/Gemini" in script
            assert "export GEMINI_CONFIG_DIR=/Users/test/data/Gemini" in script
            assert "export ANTIGRAVITY_HOME=/Users/test/data/Gemini" in script
            assert 'if [ -d "$HOME/.gemini" ] && [ ! -d /Users/test/data/Gemini ]; then' in script
            assert 'cp -R "$HOME/.gemini/." /Users/test/data/Gemini/' in script
            assert 'cp -R "$REAL_USER_HOME/.gemini/." "$_TARGET_GEMINI_DIR/"' in script
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/test_engines.py -k "test_hard_clone_gemini_home_script or test_soft_clone_gemini_home_script" -v`
Expected: FAIL

- [ ] **Step 3: Implement `GEMINI_HOME` handling in `CloneEngine`, `HardCloneEngine`, and `SoftCloneEngine`**

In `src/atbclone/core/engines.py`:
1. Add `_build_gemini_init_cmd(effective_env: dict[str, str], data_dir: Path) -> str`:
```python
    @staticmethod
    def _build_gemini_init_cmd(effective_env: dict[str, str], data_dir: Path) -> str:
        """Return shell snippet to initialize GEMINI_HOME from ~/.gemini at clone creation time."""
        target_val = (
            effective_env.get("GEMINI_HOME")
            or effective_env.get("ANTIGRAVITY_HOME")
            or effective_env.get("GEMINI_CONFIG_DIR")
        )
        if not target_val:
            return ""
        target_path = target_val.replace("{{ATB_DATA_DIR}}", str(data_dir))
        target_quoted = shlex.quote(target_path)
        return textwrap.dedent(f"""\
            if [ -d "$HOME/.gemini" ] && [ ! -d {target_quoted} ]; then
                mkdir -p {target_quoted}
                cp -R "$HOME/.gemini/." {target_quoted}/ 2>/dev/null || true
            fi
        """).strip() + "\n"
```

2. Add runtime snippet in wrapper lines of `HardCloneEngine` and `SoftCloneEngine`:
```python
            '_TARGET_GEMINI_DIR="${GEMINI_HOME:-${ANTIGRAVITY_HOME:-$GEMINI_CONFIG_DIR}}"',
            'if [ -n "$_TARGET_GEMINI_DIR" ] && [ "$_TARGET_GEMINI_DIR" != "$REAL_USER_HOME/.gemini" ]; then',
            '    mkdir -p "$_TARGET_GEMINI_DIR" 2>/dev/null || true',
            '    if [ -d "$REAL_USER_HOME/.gemini" ] && [ -z "$(ls -A "$_TARGET_GEMINI_DIR" 2>/dev/null)" ]; then',
            '        cp -R "$REAL_USER_HOME/.gemini/." "$_TARGET_GEMINI_DIR/" 2>/dev/null || true',
            '    fi',
            'fi',
```

3. Include `gemini_init_cmd` in the clone creation execution script (`SoftCloneEngine` & `HardCloneEngine`).

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/test_engines.py -v`
Expected: PASS

- [ ] **Step 5: Commit engine changes**

```bash
git add src/atbclone/core/engines.py tests/test_engines.py
git commit -m "feat(engine): add creation-time copy and runtime initialization for GEMINI_HOME and ANTIGRAVITY_HOME"
```

---

### Task 3: Full Test Suite Verification

**Files:**
- Test: `tests/`

- [ ] **Step 1: Run full test suite**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/`
Expected: All tests pass (0 failures).
