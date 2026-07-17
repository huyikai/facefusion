# UI Language Preference Design

**Date:** 2026-07-17  
**Repo:** https://github.com/huyikai/facefusion (fork of facefusion/facefusion)  
**Status:** Approved for implementation after user review of this spec  
**中文版：** [2026-07-17-ui-language-design.zh.md](./2026-07-17-ui-language-design.zh.md)

## Goal

Add a UI language preference so users can:

1. Default to the system language
2. Override via a dropdown in the web UI
3. Persist the preference in `facefusion.ini`
4. Apply the change after restarting the application (no hot-reload; browser refresh is not enough)

## Decisions (locked)

| Topic | Decision |
|---|---|
| Switching surface | UI only (no `--language` CLI for v1) |
| Persistence | Write `uis.language` into `facefusion.ini` |
| Apply timing | Save + toast; user restarts the application |
| Approach | Config-driven + UI dropdown (Approach A) |
| Languages (v1) | `system` / `en` / `zh` |
| Technical choice labels (zh) | Keep English id + append `【中文说明】` (do not replace the id) |
| Parameter help UX | `ℹ️` icon with hover/click explanation (not always-visible `info=` text) |
| Help coverage (v1) | Processors + major processor options only |

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
3. Show `gr.Info` toast: language saved; restart the application to apply

No live re-labeling of existing Gradio components (Blocks are built once at process start).

## Technical choice label convention (Chinese UI)

Some UI options are **technical identifiers** (especially processor module names). Fully translating them to Chinese alone is inappropriate because users still need the original id for docs, logs, and configs.

### Display rule (when active language is `zh`)

```text
{english_id}【{chinese_gloss}】
```

Examples:

- `face_enhancer【面部增强】`
- `face_swapper【换脸】`
- `frame_enhancer【画面增强】`

When active language is `en`, keep the plain English id (no brackets).

### Value rule (critical)

- **Displayed label** may include `【…】`
- **Stored / submitted value** must remain the raw English id (e.g. `face_enhancer`)
- Implement with Gradio choice tuples `(label, value)` so state, jobs, and CLI stay compatible

### Scope (v1)

In scope for annotated labels:

- Processor checkbox choices (`face_swapper`, `face_enhancer`, …)

Out of scope unless later expanded:

- Model filenames / model ids (keep English only)
- Gradio built-in chrome strings

Optional follow-up (same format if needed): enum-like UI values such as `one` / `many` / `reference` for face selector — confirm during implementation if user wants them annotated the same way.

### Locales

Add a dedicated glossary map under locales, e.g. `choices.processors.face_enhancer = 面部增强`, composed at render time as `f"{id}【{gloss}】"` for zh.

## Parameter help (`ℹ️` icon)

Many labels (processor names, models, detector options) remain unclear even with Chinese glosses. Provide short explanations via an **info icon**, not permanent helper text under every control.

### Interaction

- Show a `ℹ️` (or Gradio-compatible info affordance) next to the control label / choice group
- **Hover** (desktop) and/or **click/tap** (needed for trackpads/mobile) reveals the explanation
- Content comes from locales (`help.*` / new `uis_help.*` keys), so `en`/`zh` both work
- Keep copy short: 1–2 sentences, what it does + when to change it

### Implementation notes

- Prefer Gradio-native patterns first (e.g. label markdown with title/tooltip where supported, or a small adjacent HTML/Button + `gr.Info` / popover pattern that fits current Gradio 5.x)
- Must not change stored values or processor logic
- If a true tooltip widget is awkward in Gradio, acceptable fallback: clicking `ℹ️` shows `gr.Info` / modal markdown with the same locale text
- English UI gets the same icons (English help text)

### Scope (v1)

**In scope:**

- Processor checkbox group (`face_swapper`, `face_enhancer`, …) — each processor id may have its own short help entry; group-level help also allowed
- Major options of enabled processors: model / weight / blend / pixel boost / morph / factor / areas / etc. (whatever each processor module already exposes in UI)

**Out of scope for v1:**

- Face detector / selector / masker / tracker
- Output, execution, download, memory blocks
- Webcam / benchmark / jobs layouts extras beyond shared processor widgets

Later versions can reuse the same `ℹ️` helper pattern for other blocks.

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
| `facefusion/locales.py` + processor locales | Keep `en`/`zh`; add language UI strings + processor gloss map |
| `facefusion/uis/components/processors.py` | zh: show `id【gloss】`, value stays raw id; add `ℹ️` help |
| Processor option UI components | Add `ℹ️` help next to model/weight/blend/… controls |
| `facefusion.ini` | `language =` under `[uis]` |
| `tests/test_translator.py` (+ small config/resolve/label tests) | Cover resolve, fallback, set_language, label composition |

## Non-goals (v1)

- Hot-swap labels without application restart
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
6. Manual: change dropdown → ini updated → restart app → UI labels match selection
7. Manual (zh): processors show `id【gloss】`; `ℹ️` reveals short help for processors and key processor options
8. Manual (en): processors stay plain ids; `ℹ️` still available with English help

## Rollout / repo notes

- Local tree was not a git repo at design time; implementation branch should track `https://github.com/huyikai/facefusion.git`
- Suggested branch: `feature/ui-language`
- Existing zh locale strings already present locally can be reused; remove hard-coded `CURRENT_LANGUAGE = 'zh'` in favor of resolved preference

## Success criteria

- Fresh install with empty `language` follows system locale
- User can force English or Chinese from UI
- Choice survives restart via `facefusion.ini`
- Application restart applies language; toast tells user to restart
- Headless / non-UI commands remain functional (language resolve from ini/system still safe)
- In zh UI, processor choices use `id【gloss】` while values remain raw ids
- Processor group and major processor options expose `ℹ️` help in both languages

## Spec changelog

- 2026-07-17: Initial approved design (UI language preference)
- 2026-07-17: Add zh technical label format `id【gloss】`
- 2026-07-17: Add `ℹ️` help icon UX; v1 limited to processors + major processor options
- 2026-07-17: Add Chinese version of this spec (`2026-07-17-ui-language-design.zh.md`)
- 2026-07-17: Clarify apply timing — restart application (Gradio Blocks are not rebuilt on browser refresh)
