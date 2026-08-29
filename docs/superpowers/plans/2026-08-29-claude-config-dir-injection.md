# Claude CLAUDE_CONFIG_DIR Injection & ~/.claude Replication Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Inject `CLAUDE_CONFIG_DIR` environment variable into Claude desktop / Claude Code clone processes (`com.anthropic.claudefordesktop`) and automatically replicate host `~/.claude` configuration files into the clone's custom `Claude` directory both at clone creation time and on initial launch.

**Architecture:** Update builtin recipe `com.anthropic.claudefordesktop.yaml` to inject `CLAUDE_CONFIG_DIR: '{{ATB_DATA_DIR}}/Claude'`, update `CloneEngine` (in `src/atbclone/core/engines.py`) with `_build_claude_init_cmd` and runtime wrapper safety check, and verify via automated pytest suite.

**Tech Stack:** Python 3.12, PySide6/Toga, Pytest, Bash, YAML, Pydantic.

## Global Constraints
- Target macOS native patterns, Python 3.12+ in conda environment `ATBClone`.
- Run tests via `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/`.
- Maintain backward compatibility with all existing recipes and clone engines.
- Do not overwrite existing non-empty `Claude` directory data on subsequent app launches.

---

### Task 1: Update Builtin Recipe for Claude

**Files:**
- Modify: `src/atbclone/recipes/builtin/com.anthropic.claudefordesktop.yaml`
- Test: `tests/test_recipes.py`

**Interfaces:**
- Consumes: `RecipeLoader.match(bundle_id)`
- Produces: `recipe.environment_injection["CLAUDE_CONFIG_DIR"] == "{{ATB_DATA_DIR}}/Claude"`

- [ ] **Step 1: Write the failing test for Claude recipe in `tests/test_recipes.py`**

Add test to `tests/test_recipes.py`:
```python
def test_load_builtin_claude():
    recipe = RecipeLoader.match("com.anthropic.claudefordesktop")
    assert recipe is not None
    assert recipe.bundle_id == "com.anthropic.claudefordesktop"
    assert "HOME" in recipe.environment_injection
    assert "TMPDIR" in recipe.environment_injection
    assert recipe.environment_injection.get("CLAUDE_CONFIG_DIR") == "{{ATB_DATA_DIR}}/Claude"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/test_recipes.py::test_load_builtin_claude -v`
Expected: FAIL with `AssertionError: assert None == '{{ATB_DATA_DIR}}/Claude'`

- [ ] **Step 3: Update `com.anthropic.claudefordesktop.yaml`**

In `src/atbclone/recipes/builtin/com.anthropic.claudefordesktop.yaml`:
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

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/test_recipes.py -v`
Expected: PASS

- [ ] **Step 5: Commit recipe updates**

```bash
git add src/atbclone/recipes/builtin/com.anthropic.claudefordesktop.yaml tests/test_recipes.py
git commit -m "feat(recipes): add CLAUDE_CONFIG_DIR to Claude recipe"
```

---

### Task 2: Enhance Clone Engines with Creation-Time and Runtime CLAUDE_CONFIG_DIR Support

**Files:**
- Modify: `src/atbclone/core/engines.py`
- Test: `tests/test_engines.py`

**Interfaces:**
- Consumes: `task: CloneTask` with `task.recipe.environment_injection`
- Produces: `HardCloneEngine.execute` and `SoftCloneEngine.execute` generating creation script with `~/.claude` copying and wrapper script with `CLAUDE_CONFIG_DIR` initialization snippet.

- [ ] **Step 1: Write failing unit tests in `tests/test_engines.py`**

Add tests to `tests/test_engines.py` verifying:
1. When `CLAUDE_CONFIG_DIR` is present in `task.recipe.environment_injection`, the generated script in `HardCloneEngine.execute` includes creation-time `cp -R "$HOME/.claude/."` to the target Claude path.
2. The generated wrapper script contains `export CLAUDE_CONFIG_DIR=...` and the runtime check copying `$REAL_USER_HOME/.claude` if `$CLAUDE_CONFIG_DIR` is empty.
3. Test similar behavior for `SoftCloneEngine.execute`.

```python
    def test_hard_clone_claude_script(self, mock_app_info, base_recipe):
        base_recipe.environment_injection = {
            "HOME": "{{ATB_DATA_DIR}}/Home",
            "TMPDIR": "{{ATB_DATA_DIR}}/Tmp",
            "CLAUDE_CONFIG_DIR": "{{ATB_DATA_DIR}}/Claude",
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
            assert "export CLAUDE_CONFIG_DIR=/Users/test/data/Claude" in script
            assert 'if [ -d "$HOME/.claude" ] && [ ! -d /Users/test/data/Claude ]; then' in script
            assert 'cp -R "$HOME/.claude/." /Users/test/data/Claude/' in script
            assert 'if [ -n "$CLAUDE_CONFIG_DIR" ] && [ "$CLAUDE_CONFIG_DIR" != "$REAL_USER_HOME/.claude" ]; then' in script
            assert 'cp -R "$REAL_USER_HOME/.claude/." "$CLAUDE_CONFIG_DIR/"' in script

    def test_soft_clone_claude_script(self, mock_app_info, base_recipe):
        base_recipe.environment_injection = {
            "HOME": "{{ATB_DATA_DIR}}/Home",
            "TMPDIR": "{{ATB_DATA_DIR}}/Tmp",
            "CLAUDE_CONFIG_DIR": "{{ATB_DATA_DIR}}/Claude",
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
            assert "export CLAUDE_CONFIG_DIR=/Users/test/data/Claude" in script
            assert 'if [ -d "$HOME/.claude" ] && [ ! -d /Users/test/data/Claude ]; then' in script
            assert 'cp -R "$HOME/.claude/." /Users/test/data/Claude/' in script
            assert 'if [ -n "$CLAUDE_CONFIG_DIR" ] && [ "$CLAUDE_CONFIG_DIR" != "$REAL_USER_HOME/.claude" ]; then' in script
            assert 'cp -R "$REAL_USER_HOME/.claude/." "$CLAUDE_CONFIG_DIR/"' in script
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/test_engines.py -k "test_hard_clone_claude_script or test_soft_clone_claude_script" -v`
Expected: FAIL

- [ ] **Step 3: Implement `CLAUDE_CONFIG_DIR` handling in `CloneEngine`, `HardCloneEngine`, and `SoftCloneEngine`**

In `src/atbclone/core/engines.py`:
1. Add `_build_claude_init_cmd(effective_env: dict[str, str], data_dir: Path) -> str`:
```python
    @staticmethod
    def _build_claude_init_cmd(effective_env: dict[str, str], data_dir: Path) -> str:
        """Return shell snippet to initialize CLAUDE_CONFIG_DIR from ~/.claude at clone creation time."""
        if "CLAUDE_CONFIG_DIR" not in effective_env:
            return ""
        raw_val = effective_env["CLAUDE_CONFIG_DIR"]
        target_path = raw_val.replace("{{ATB_DATA_DIR}}", str(data_dir))
        target_quoted = shlex.quote(target_path)
        return textwrap.dedent(f"""\
            if [ -d "$HOME/.claude" ] && [ ! -d {target_quoted} ]; then
                mkdir -p {target_quoted}
                cp -R "$HOME/.claude/." {target_quoted}/ 2>/dev/null || true
            fi
        """).strip() + "\n"
```

2. Add runtime snippet in wrapper lines of `HardCloneEngine` and `SoftCloneEngine`:
```python
            'if [ -n "$CLAUDE_CONFIG_DIR" ] && [ "$CLAUDE_CONFIG_DIR" != "$REAL_USER_HOME/.claude" ]; then',
            '    mkdir -p "$CLAUDE_CONFIG_DIR" 2>/dev/null || true',
            '    if [ -d "$REAL_USER_HOME/.claude" ] && [ -z "$(ls -A "$CLAUDE_CONFIG_DIR" 2>/dev/null)" ]; then',
            '        cp -R "$REAL_USER_HOME/.claude/." "$CLAUDE_CONFIG_DIR/" 2>/dev/null || true',
            '    fi',
            'fi',
```

3. Include `claude_init_cmd` in the clone creation execution script (`SoftCloneEngine` & `HardCloneEngine`).

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/test_engines.py -v`
Expected: PASS

- [ ] **Step 5: Commit engine changes**

```bash
git add src/atbclone/core/engines.py tests/test_engines.py
git commit -m "feat(engine): add creation-time copy and runtime initialization for CLAUDE_CONFIG_DIR"
```

---

### Task 3: Full Test Suite Verification

**Files:**
- Test: `tests/`

- [ ] **Step 1: Run full test suite**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/`
Expected: All tests pass (0 failures).
