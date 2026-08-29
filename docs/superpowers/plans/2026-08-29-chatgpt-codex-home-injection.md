# ChatGPT Codex CODEX_HOME Injection & ~/.codex Replication Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Inject `CODEX_HOME` environment variable into ChatGPT / Codex clone processes (`com.openai.codex` and `com.openai.chat`) and automatically replicate host `~/.codex` configuration files into the clone's custom `CODEX_HOME` directory both at creation time and on initial launch.

**Architecture:** Update builtin recipes to declare `CODEX_HOME: '{{ATB_DATA_DIR}}/Codex'`, enhance `CloneEngine` (in `src/atbclone/core/engines.py`) to copy `~/.codex` at clone creation time and generate wrapper scripts with runtime `CODEX_HOME` directory initialization and copy fallback, and add comprehensive unit tests.

**Tech Stack:** Python 3.12, PySide6/Toga, Pytest, Bash, YAML, Pydantic.

## Global Constraints
- Target macOS native patterns, Python 3.12+ in conda environment `ATBClone`.
- Run tests via `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/`.
- Maintain backward compatibility with all existing recipes and clone engines.
- Do not overwrite existing non-empty `CODEX_HOME` data on subsequent app launches.

---

### Task 1: Update Builtin Recipes for ChatGPT and Codex

**Files:**
- Modify: `src/atbclone/recipes/builtin/com.openai.codex.yaml`
- Modify: `src/atbclone/recipes/builtin/com.openai.chat.yaml`
- Test: `tests/test_recipes.py`

**Interfaces:**
- Consumes: `RecipeLoader.match(bundle_id)`
- Produces: `recipe.environment_injection["CODEX_HOME"] == "{{ATB_DATA_DIR}}/Codex"`

- [ ] **Step 1: Write the failing test for CODEX_HOME in recipes**

Update `tests/test_recipes.py`:
```python
def test_load_builtin_chatgpt():
    recipe = RecipeLoader.match("com.openai.codex")
    assert recipe is not None
    assert recipe.bundle_id == "com.openai.codex"
    assert recipe.app_name == "ChatGPT"
    assert recipe.strategy == "hard_clone"
    assert recipe.strip_sandbox is True
    assert "HOME" in recipe.environment_injection
    assert "TMPDIR" in recipe.environment_injection
    assert recipe.environment_injection.get("CODEX_HOME") == "{{ATB_DATA_DIR}}/Codex"


def test_load_builtin_chatgpt_chat():
    recipe = RecipeLoader.match("com.openai.chat")
    assert recipe is not None
    assert recipe.bundle_id == "com.openai.chat"
    assert recipe.app_name == "ChatGPT"
    assert recipe.strategy == "hard_clone"
    assert recipe.strip_sandbox is True
    assert "HOME" in recipe.environment_injection
    assert "TMPDIR" in recipe.environment_injection
    assert recipe.environment_injection.get("CODEX_HOME") == "{{ATB_DATA_DIR}}/Codex"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/test_recipes.py::test_load_builtin_chatgpt tests/test_recipes.py::test_load_builtin_chatgpt_chat -v`
Expected: FAIL with `AssertionError: assert None == '{{ATB_DATA_DIR}}/Codex'`

- [ ] **Step 3: Update `com.openai.codex.yaml` and `com.openai.chat.yaml`**

In `src/atbclone/recipes/builtin/com.openai.codex.yaml`:
```yaml
bundle_id: com.openai.codex
app_name: ChatGPT
strategy: hard_clone
app_type: cocoa
strip_sandbox: true
environment_injection:
  HOME: '{{ATB_DATA_DIR}}/Home'
  TMPDIR: '{{ATB_DATA_DIR}}/Tmp'
  CODEX_HOME: '{{ATB_DATA_DIR}}/Codex'
```

In `src/atbclone/recipes/builtin/com.openai.chat.yaml`:
```yaml
bundle_id: com.openai.chat
app_name: ChatGPT
strategy: hard_clone
app_type: cocoa
strip_sandbox: true
environment_injection:
  HOME: '{{ATB_DATA_DIR}}/Home'
  TMPDIR: '{{ATB_DATA_DIR}}/Tmp'
  CODEX_HOME: '{{ATB_DATA_DIR}}/Codex'
```

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/test_recipes.py -v`
Expected: PASS

- [ ] **Step 5: Commit recipe updates**

```bash
git add src/atbclone/recipes/builtin/com.openai.codex.yaml src/atbclone/recipes/builtin/com.openai.chat.yaml tests/test_recipes.py
git commit -m "feat(recipes): add CODEX_HOME environment variable to ChatGPT and Codex recipes"
```

---

### Task 2: Enhance Clone Engines with Creation-Time and Runtime CODEX_HOME Support

**Files:**
- Modify: `src/atbclone/core/engines.py`
- Test: `tests/test_engines.py`

**Interfaces:**
- Consumes: `task: CloneTask` with `task.recipe.environment_injection`
- Produces: `HardCloneEngine.execute` and `SoftCloneEngine.execute` generating creation script with `~/.codex` copying and wrapper script with `CODEX_HOME` initialization snippet.

- [ ] **Step 1: Write failing unit tests in `tests/test_engines.py`**

Add tests to `tests/test_engines.py` verifying:
1. When `CODEX_HOME` is present in `task.recipe.environment_injection`, the generated script in `HardCloneEngine.execute` includes creation-time `cp -R "$HOME/.codex/."` to the target Codex path.
2. The generated wrapper script contains `export CODEX_HOME=...` and the runtime check copying `$REAL_USER_HOME/.codex` if `$CODEX_HOME` is empty.
3. Test similar behavior for `SoftCloneEngine.execute`.

```python
def test_hard_clone_codex_home_script(mock_app_info, base_recipe):
    base_recipe.environment_injection = {
        "HOME": "{{ATB_DATA_DIR}}/Home",
        "TMPDIR": "{{ATB_DATA_DIR}}/Tmp",
        "CODEX_HOME": "{{ATB_DATA_DIR}}/Codex",
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
        assert "export CODEX_HOME='/Users/test/data/Codex'" in script
        assert 'if [ -d "$HOME/.codex" ] && [ ! -d \'/Users/test/data/Codex\' ]; then' in script
        assert 'cp -R "$HOME/.codex/." \'/Users/test/data/Codex/\'' in script
        assert 'if [ -n "$CODEX_HOME" ] && [ "$CODEX_HOME" != "$REAL_USER_HOME/.codex" ]; then' in script
        assert 'cp -R "$REAL_USER_HOME/.codex/." "$CODEX_HOME/"' in script
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/test_engines.py -k test_hard_clone_codex_home_script -v`
Expected: FAIL

- [ ] **Step 3: Implement `CODEX_HOME` handling in `HardCloneEngine` and `SoftCloneEngine`**

In `src/atbclone/core/engines.py`:
1. Add helper `_build_codex_init_cmd(cls, effective_env: dict[str, str], data_dir: Path) -> str`:
```python
    @staticmethod
    def _build_codex_init_cmd(effective_env: dict[str, str], data_dir: Path) -> str:
        """Return shell snippet to initialize CODEX_HOME from ~/.codex at clone creation time."""
        if "CODEX_HOME" not in effective_env:
            return ""
        raw_val = effective_env["CODEX_HOME"]
        target_path = raw_val.replace("{{ATB_DATA_DIR}}", str(data_dir))
        target_quoted = shlex.quote(target_path)
        return textwrap.dedent(f"""\
            if [ -d "$HOME/.codex" ] && [ ! -d {target_quoted} ]; then
                mkdir -p {target_quoted}
                cp -R "$HOME/.codex/." {target_quoted}/ 2>/dev/null || true
            fi
        """).strip() + "\n"
```

2. Add runtime snippet in wrapper lines of `HardCloneEngine` and `SoftCloneEngine`:
```python
            'if [ -n "$CODEX_HOME" ] && [ "$CODEX_HOME" != "$REAL_USER_HOME/.codex" ]; then',
            '    mkdir -p "$CODEX_HOME" 2>/dev/null || true',
            '    if [ -d "$REAL_USER_HOME/.codex" ] && [ -z "$(ls -A "$CODEX_HOME" 2>/dev/null)" ]; then',
            '        cp -R "$REAL_USER_HOME/.codex/." "$CODEX_HOME/" 2>/dev/null || true',
            '    fi',
            'fi',
```

3. Include `codex_init_cmd` in the main execution script during clone creation.

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/test_engines.py -v`
Expected: PASS

- [ ] **Step 5: Commit engine changes**

```bash
git add src/atbclone/core/engines.py tests/test_engines.py
git commit -m "feat(engine): add creation-time copy and runtime initialization for CODEX_HOME"
```

---

### Task 3: Full Test Suite Verification

**Files:**
- Test: `tests/`

- [ ] **Step 1: Run full test suite**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/`
Expected: All tests pass (0 failures).

- [ ] **Step 2: Verify all builtin recipes have valid schema and app_type**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/test_recipes.py -v`
Expected: All builtin recipes pass validity and explicit app_type checks.
