# UI Language Preference Design

**Date:** 2026-07-17  
**Repo:** https://github.com/huyikai/facefusion (fork of facefusion/facefusion)  
**Status:** Approved for implementation after user review of this spec

## Goal

Add a UI language preference so users can:

1. Default to the system language
2. Override via a dropdown in the web UI
3. Persist the preference in `facefusion.ini`
4. Apply the change after a page refresh (no hot-reload)

## Decisions (locked)

| Topic | Decision |
|---|---|
| Switching surface | UI only (no `--language` CLI for v1) |
| Persistence | Write `uis.language` into `facefusion.ini` |
| Apply timing | Save + toast; user refreshes page |
| Approach | Config-driven + UI dropdown (Approach A) |
| Languages (v1) | `system` / `en` / `zh` |

## Configuration model

Add under `[uis]` in `facefusion.ini`:

```ini
[uis]
language = system
```

### Types

- `LanguagePreference = Literal['system', 'en', 'zh']` — stored preference / UI value
- `Language = Literal['en', 'zh']` — resolved active locale used by `translator`

### Resolution algorithm

1. Read `uis.language` from config; empty/missing → `system`
2. If preference is `en` or `zh` → use it as active language
3. If preference is `system`:
   - Inspect system locale (`locale.getdefaultlocale()` / `locale.getlocale()`, plus common env fallbacks if needed)
   - If language tag starts with `zh` (case-insensitive) → `zh`
   - Else → `en`
4. Unknown preference → `en`
5. Missing translation key for active language → fall back to `en` string

Call `translator.set_language(resolved)` early during `run` / UI bootstrap, before Gradio labels are created.

## UI design

New component: `facefusion/uis/components/language.py`

- Placement: default layout, near top-left (`about` block), visible on main UI
- Control: Gradio `Dropdown`
- Label: translated via locales (`uis.language_dropdown`)
- Choices shown to user:
  - `system` → 跟随系统 / Follow System
  - `en` → English
  - `zh` → 中文
- Dropdown **value** is the preference (`system|en|zh`), not the resolved language

### On change

1. Update in-memory state (`language` preference)
2. Persist to `facefusion.ini` → `[uis] language = ...`
3. Show `gr.Info` toast: language saved; refresh the page to apply

No live re-labeling of existing Gradio components.

## Persistence / config write

`facefusion/config.py` currently read-only. Add:

- `set_str_value(section, option, value)` that:
  - Opens the active `config_path`
  - Ensures section exists
  - Sets option
  - Writes file with UTF-8
  - Clears `get_static_config_parser` LRU cache

Only used for language preference in v1 (keep scope tight).

## Code touch list

| Area | Change |
|---|---|
| `facefusion/types.py` | `LanguagePreference`, extend `Language`, add state key `language` |
| `facefusion/choices.py` | `language_preferences` list |
| `facefusion/translator.py` | Keep `set_language` + English fallback; default active language resolved at startup (not hard-coded `zh`) |
| `facefusion/config.py` | `set_str_value` |
| `facefusion/program.py` / `args.py` | Read `uis.language` into state for `run` (config only, no new CLI flag) |
| UI bootstrap (`core` / layouts) | Resolve preference → `translator.set_language` before render |
| `facefusion/uis/components/language.py` | New dropdown component |
| `facefusion/uis/layouts/default.py` (+ other layouts if needed) | Mount language component |
| `facefusion/locales.py` + processor locales | Keep `en`/`zh`; add strings for language UI + toast |
| `facefusion.ini` | `language =` under `[uis]` |
| `tests/test_translator.py` (+ small config/resolve tests) | Cover resolve, fallback, set_language |

## Non-goals (v1)

- Hot-swap labels without refresh
- Translating Gradio built-in chrome (upload prompts, etc.)
- Languages beyond `en` / `zh`
- CLI `--language`
- Upstream PR packaging (fork first; upstream later if desired)

## Testing plan

1. Unit: preference `system` with mocked `zh_*` locale → resolves `zh`
2. Unit: preference `system` with mocked `en_*` locale → resolves `en`
3. Unit: preference `zh` / `en` ignores system
4. Unit: missing zh key falls back to en
5. Unit: `set_str_value` writes ini and subsequent read returns new value
6. Manual: change dropdown → ini updated → refresh → UI labels match selection

## Rollout / repo notes

- Local tree was not a git repo at design time; implementation branch should track `https://github.com/huyikai/facefusion.git`
- Suggested branch: `feature/ui-language`
- Existing zh locale strings already present locally can be reused; remove hard-coded `CURRENT_LANGUAGE = 'zh'` in favor of resolved preference

## Success criteria

- Fresh install with empty `language` follows system locale
- User can force English or Chinese from UI
- Choice survives restart via `facefusion.ini`
- Refresh applies language; toast tells user to refresh
- Headless / non-UI commands remain functional (language resolve from ini/system still safe)
