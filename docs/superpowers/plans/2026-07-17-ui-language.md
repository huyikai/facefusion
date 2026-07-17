# UI 多语言与处理器说明 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 实现可持久化的 UI 语言偏好（跟随系统 / en / zh）、中文下处理器选项 `id【说明】` 展示，以及处理器相关控件的 `ℹ️` 说明。

**Architecture:** 配置项 `uis.language` 存偏好；启动时解析为生效语言并 `translator.set_language`；UI 下拉改偏好并写回 ini，提示刷新。处理器选项用 Gradio `(label, value)` 元组；`ℹ️` 用小按钮点击触发 `gr.Info`（悬停用 `elem_title`/`title` 作辅助）。

**Tech Stack:** Python 3.12、现有 `translator`/`config`/`state_manager`、Gradio 5.x、pytest

**规格：** `docs/superpowers/specs/2026-07-17-ui-language-design.zh.md`

## Global Constraints

- 切换入口仅 UI（v1 不加 `--language` CLI）
- 偏好写入 `facefusion.ini` 的 `uis.language`
- 默认 `system`；刷新后生效
- 生效语言仅 `en` / `zh`
- 中文技术选项：`{id}【{gloss}】`，提交值仍为原始 id
- `ℹ️` v1 仅覆盖处理器列表 + 各处理器主要选项
- 词条缺失回退英文
- 不做热切换、不翻译 Gradio 内置 chrome、不翻译模型文件名

## File Structure

| 文件 | 职责 |
|---|---|
| `facefusion/types.py` | `LanguagePreference`、扩展 `Language`、State 增加 `language` |
| `facefusion/choices.py` | `language_preferences` |
| `facefusion/translator.py` | `set_language` / `get_language`、默认 `en`、英文回退 |
| `facefusion/locales_helper.py` | **新建**：系统语言探测、偏好解析、选项标签拼接 |
| `facefusion/config.py` | `set_str_value` 写 ini 并清缓存 |
| `facefusion/args.py` | 从 config 读 `uis.language` 进 state（无 CLI） |
| `facefusion/core.py` | `apply_args` 后解析并 `set_language` |
| `facefusion/locales.py` | 中英文：语言 UI、处理器 gloss、处理器帮助文案 |
| `facefusion/processors/modules/*/locales.py` | 各处理器选项的帮助文案（若放模块内） |
| `facefusion/uis/help_helper.py` | **新建**：`ℹ️` 按钮工厂 + 点击展示 |
| `facefusion/uis/components/language.py` | **新建**：语言下拉 |
| `facefusion/uis/layouts/default.py` | 挂载 language |
| `facefusion/uis/components/processors.py` | `id【gloss】` + 组级 `ℹ️` |
| `facefusion/uis/components/*_options.py`（处理器相关） | 主要控件旁加 `ℹ️` |
| `facefusion/uis/types.py` | 如需注册新 component name |
| `facefusion.ini` | `language =` |
| `tests/test_translator.py` / `tests/test_locales_helper.py` / `tests/test_config.py` | 单元测试 |

---

### Task 1: 语言类型、解析与 translator API

**Files:**
- Modify: `facefusion/types.py`
- Modify: `facefusion/choices.py`
- Modify: `facefusion/translator.py`
- Create: `facefusion/locales_helper.py`
- Modify: `tests/test_translator.py`
- Create: `tests/test_locales_helper.py`

**Interfaces:**
- Produces: `LanguagePreference`, `Language`, `choices.language_preferences`
- Produces: `translator.set_language(language: Language) -> None`
- Produces: `translator.get_language() -> Language`
- Produces: `locales_helper.resolve_language(preference: LanguagePreference) -> Language`
- Produces: `locales_helper.detect_system_language() -> Language`
- Produces: `locales_helper.format_choice_label(choice_id: str, gloss: Optional[str]) -> str`

- [ ] **Step 1: 写失败测试 `tests/test_locales_helper.py`**

```python
from facefusion import translator
from facefusion.locales_helper import detect_system_language, format_choice_label, resolve_language


def test_resolve_language_explicit() -> None:
	assert resolve_language('zh') == 'zh'
	assert resolve_language('en') == 'en'


def test_resolve_language_system_zh(monkeypatch) -> None:
	monkeypatch.setattr('facefusion.locales_helper.detect_system_language', lambda: 'zh')
	assert resolve_language('system') == 'zh'


def test_resolve_language_system_en(monkeypatch) -> None:
	monkeypatch.setattr('facefusion.locales_helper.detect_system_language', lambda: 'en')
	assert resolve_language('system') == 'en'


def test_resolve_language_unknown_falls_back_to_en() -> None:
	assert resolve_language('fr') == 'en'  # type: ignore[arg-type]


def test_format_choice_label_zh() -> None:
	translator.set_language('zh')
	assert format_choice_label('face_enhancer', '面部增强') == 'face_enhancer【面部增强】'


def test_format_choice_label_en() -> None:
	translator.set_language('en')
	assert format_choice_label('face_enhancer', '面部增强') == 'face_enhancer'
```

- [ ] **Step 2: 运行测试确认失败**

Run: `pip install pytest -q && pytest tests/test_locales_helper.py -v`  
Expected: FAIL（模块不存在）

- [ ] **Step 3: 实现类型与 choices**

在 `facefusion/types.py`：

```python
Language = Literal['en', 'zh']
LanguagePreference = Literal['system', 'en', 'zh']
```

在 `StateKey` 字面量列表与 `State` TypedDict 中增加 `'language'`，类型为 `LanguagePreference`。

在 `facefusion/choices.py`：

```python
from facefusion.types import LanguagePreference
# ...
language_preferences : List[LanguagePreference] = list(get_args(LanguagePreference))
```

- [ ] **Step 4: 实现 `translator.py`**

```python
CURRENT_LANGUAGE : Language = 'en'

def set_language(language : Language) -> None:
	global CURRENT_LANGUAGE
	CURRENT_LANGUAGE = language

def get_language() -> Language:
	return CURRENT_LANGUAGE
```

保留现有 `get()` 的英文回退逻辑。

- [ ] **Step 5: 实现 `locales_helper.py`**

```python
import locale
import os
from typing import Optional

from facefusion import translator
from facefusion.types import Language, LanguagePreference


def detect_system_language() -> Language:
	candidates = []
	for getter in (locale.getdefaultlocale, locale.getlocale):
		try:
			value = getter()
			if value and value[0]:
				candidates.append(value[0])
		except Exception:
			pass
	for key in ('LANG', 'LC_ALL', 'LC_MESSAGES'):
		env_value = os.environ.get(key)
		if env_value:
			candidates.append(env_value)
	for candidate in candidates:
		normalized = candidate.replace('-', '_').lower()
		if normalized.startswith('zh'):
			return 'zh'
	return 'en'


def resolve_language(preference : LanguagePreference) -> Language:
	if preference in ('en', 'zh'):
		return preference
	if preference == 'system':
		return detect_system_language()
	return 'en'


def format_choice_label(choice_id : str, gloss : Optional[str]) -> str:
	if translator.get_language() == 'zh' and gloss:
		return f'{choice_id}【{gloss}】'
	return choice_id
```

- [ ] **Step 6: 更新 `tests/test_translator.py`**

```python
def test_get() -> None:
	translator.set_language('en')
	assert translator.get('conda_not_activated') == 'conda is not activated'
	assert translator.get('invalid') is None

	translator.set_language('zh')
	assert translator.get_language() == 'zh'
```

（若 `zh` 词条尚不完整，本任务只断言 `get_language`；完整中文断言放到 Task 4。）

- [ ] **Step 7: 跑测试通过并提交**

Run: `pytest tests/test_locales_helper.py tests/test_translator.py -v`  
Expected: PASS

```bash
git add facefusion/types.py facefusion/choices.py facefusion/translator.py facefusion/locales_helper.py tests/test_locales_helper.py tests/test_translator.py
git commit -m "feat: add language preference types and locale resolution"
```

---

### Task 2: 配置写回 `set_str_value`

**Files:**
- Modify: `facefusion/config.py`
- Create: `tests/test_config.py`

**Interfaces:**
- Consumes: `state_manager.get_item('config_path')`
- Produces: `config.set_str_value(section: str, option: str, value: str) -> None`

- [ ] **Step 1: 写失败测试**

```python
import configparser
from pathlib import Path

from facefusion import config, state_manager


def test_set_str_value_writes_ini(tmp_path: Path, monkeypatch) -> None:
	ini_path = tmp_path / 'facefusion.ini'
	ini_path.write_text('[uis]\nlanguage = system\n', encoding='utf-8')
	state_manager.init_item('config_path', str(ini_path))
	config.get_static_config_parser.cache_clear()

	config.set_str_value('uis', 'language', 'zh')

	parser = configparser.ConfigParser()
	parser.read(ini_path, encoding='utf-8')
	assert parser.get('uis', 'language') == 'zh'
	assert config.get_str_value('uis', 'language') == 'zh'
```

- [ ] **Step 2: 跑测试确认失败**

Run: `pytest tests/test_config.py::test_set_str_value_writes_ini -v`  
Expected: FAIL

- [ ] **Step 3: 实现写回**

在 `facefusion/config.py` 末尾增加：

```python
def set_str_value(section : str, option : str, value : str) -> None:
	config_path = state_manager.get_item('config_path')
	config_parser = ConfigParser()
	config_parser.read(config_path, encoding = 'utf-8')
	if not config_parser.has_section(section):
		config_parser.add_section(section)
	config_parser.set(section, option, value)
	with open(config_path, 'w', encoding = 'utf-8') as config_file:
		config_parser.write(config_file)
	get_static_config_parser.cache_clear()
```

- [ ] **Step 4: 测试通过并提交**

Run: `pytest tests/test_config.py -v`  
Expected: PASS

```bash
git add facefusion/config.py tests/test_config.py
git commit -m "feat: allow writing string values back to facefusion.ini"
```

---

### Task 3: 启动时加载语言偏好

**Files:**
- Modify: `facefusion/args.py`
- Modify: `facefusion/core.py`
- Modify: `facefusion.ini`

**Interfaces:**
- Consumes: `config.get_str_value('uis', 'language', 'system')`, `locales_helper.resolve_language`, `translator.set_language`
- Produces: state key `language` 在 `apply_args` 后可用

- [ ] **Step 1: 在 `facefusion.ini` `[uis]` 增加空项**

```ini
[uis]
open_browser =
ui_layouts =
ui_workflow =
language =
```

- [ ] **Step 2: 在 `args.py` 的 `apply_args` 中读取偏好（无 CLI 参数）**

在 `apply_state_item('ui_workflow', ...)` 附近加入：

```python
from facefusion import config
# ...
language_preference = config.get_str_value('uis', 'language', 'system') or 'system'
if language_preference not in ('system', 'en', 'zh'):
	language_preference = 'system'
apply_state_item('language', language_preference)
```

注意：`config_path` 必须已由 `apply_state_item('config_path', ...)` 初始化（确认 `create_config_path_program` 更早执行；`apply_args` 开头通常已有 paths。若 `config_path` 不在 `apply_args` 内，则在 `core.cli` 里于 `apply_args` 前 `state_manager.init_item('config_path', args.get('config_path') or 'facefusion.ini')`，或在读取 language 时用 `args.get('config_path')`。检查现有 `apply_args`：若无 `config_path`，先加：

```python
apply_state_item('config_path', args.get('config_path') or 'facefusion.ini')
```

（若项目已在别处 init，保持一致，避免重复冲突。）

- [ ] **Step 3: 在 `core.cli` 于 `apply_args` 之后立刻解析语言**

```python
from facefusion.locales_helper import resolve_language

# after apply_args(...)
preference = state_manager.get_item('language') or 'system'
translator.set_language(resolve_language(preference))
```

- [ ] **Step 4: 手动快速验证**

```bash
conda activate facefusion
python -c "
from facefusion import state_manager, translator, config
from facefusion.args import apply_args
from facefusion.locales_helper import resolve_language
state_manager.init_item('config_path', 'facefusion.ini')
config.get_static_config_parser.cache_clear()
pref = config.get_str_value('uis', 'language', 'system') or 'system'
translator.set_language(resolve_language(pref))
print(pref, translator.get_language())
"
```

Expected: 打印偏好与解析后的 `en` 或 `zh`

- [ ] **Step 5: 提交**

```bash
git add facefusion/args.py facefusion/core.py facefusion.ini
git commit -m "feat: resolve UI language preference at startup"
```

---

### Task 4: 补齐 locales（语言 UI + 处理器 gloss + 帮助）

**Files:**
- Modify: `facefusion/locales.py`
- Modify: `facefusion/processors/modules/*/locales.py`（各处理器模块）
- Modify: `tests/test_translator.py`

**Interfaces:**
- Produces: `uis.language_dropdown`, `uis.language_saved`, `uis.language_choices.*`
- Produces: `choices.processors.<id>`（中文 gloss）
- Produces: `uis_help.processors`, `uis_help.processors.<id>`
- Produces: 各处理器 `uis_help.model` / `uis_help.weight` / …（或沿用/扩展现有 `help.*` 作为 `ℹ️` 文案）

- [ ] **Step 1: 在主 `locales.py` 的 `en` 与 `zh` 增加键**

英文示例：

```python
'uis': {
	# ...existing...
	'language_dropdown': 'LANGUAGE',
	'language_saved': 'Language saved. Refresh the page to apply.',
},
'language_choices': {
	'system': 'Follow System',
	'en': 'English',
	'zh': '中文',
},
'choices': {
	'processors': {
		'age_modifier': 'Age Modifier',
		'background_remover': 'Background Remover',
		'deep_swapper': 'Deep Swapper',
		'expression_restorer': 'Expression Restorer',
		'face_debugger': 'Face Debugger',
		'face_editor': 'Face Editor',
		'face_enhancer': 'Face Enhancer',
		'face_swapper': 'Face Swapper',
		'frame_colorizer': 'Frame Colorizer',
		'frame_enhancer': 'Frame Enhancer',
		'lip_syncer': 'Lip Syncer',
	}
},
'uis_help': {
	'processors': 'Enable one or more processors. Order matters for the pipeline.',
	'processors_face_swapper': 'Swap the source face onto faces detected in the target.',
	'processors_face_enhancer': 'Enhance face clarity after swapping. High blend may look artificial.',
	# ... one short line per processor id ...
}
```

中文示例：

```python
'uis': {
	'language_dropdown': '语言',
	'language_saved': '语言已保存，请刷新页面生效。',
	# ...
},
'language_choices': {
	'system': '跟随系统',
	'en': 'English',
	'zh': '中文',
},
'choices': {
	'processors': {
		'face_swapper': '换脸',
		'face_enhancer': '面部增强',
		'frame_enhancer': '画面增强',
		# ... 其余处理器 ...
	}
},
'uis_help': {
	'processors': '勾选一个或多个处理器，执行顺序会影响结果。',
	'processors_face_swapper': '将源脸替换到目标画面中的人脸。',
	'processors_face_enhancer': '换脸后增强面部清晰度；混合过高可能发假。',
	# ...
}
```

处理器选项帮助：在各 `processors/modules/<name>/locales.py` 的 `en`/`zh` 增加：

```python
'uis_help': {
	'model': '...',
	'pixel_boost': '...',
	'weight': '...',
}
```

内容用 1～2 句说明用途与调整时机（可参考规格与现有 `help.*`）。

- [ ] **Step 2: 断言中文词条**

```python
def test_zh_ui_strings() -> None:
	translator.set_language('zh')
	assert translator.get('uis.language_dropdown') == '语言'
	assert translator.get('choices.processors.face_enhancer') == '面部增强'
```

- [ ] **Step 3: 测试通过并提交**

```bash
git add facefusion/locales.py facefusion/processors/modules/*/locales.py tests/test_translator.py
git commit -m "feat: add zh/en strings for language UI, glosses, and help"
```

---

### Task 5: 语言下拉 UI 组件

**Files:**
- Create: `facefusion/uis/components/language.py`
- Modify: `facefusion/uis/layouts/default.py`
- Modify: `facefusion/uis/types.py`（如项目要求注册 component name）

**Interfaces:**
- Consumes: `state_manager.get_item('language')`, `config.set_str_value`, `translator.get`
- Produces: UI dropdown；变更写 ini + `gr.Info`

- [ ] **Step 1: 创建 `language.py`**

```python
from typing import Optional

import gradio

import facefusion.choices
from facefusion import config, state_manager, translator
from facefusion.types import LanguagePreference

LANGUAGE_DROPDOWN : Optional[gradio.Dropdown] = None


def render() -> None:
	global LANGUAGE_DROPDOWN
	LANGUAGE_DROPDOWN = gradio.Dropdown(
		label = translator.get('uis.language_dropdown'),
		choices =
		[
			(translator.get('language_choices.system'), 'system'),
			(translator.get('language_choices.en'), 'en'),
			(translator.get('language_choices.zh'), 'zh')
		],
		value = state_manager.get_item('language') or 'system'
	)


def listen() -> None:
	LANGUAGE_DROPDOWN.change(update_language, inputs = LANGUAGE_DROPDOWN)


def update_language(language : LanguagePreference) -> None:
	if language not in facefusion.choices.language_preferences:
		language = 'system'
	state_manager.set_item('language', language)
	config.set_str_value('uis', 'language', language)
	gradio.Info(translator.get('uis.language_saved'))
```

- [ ] **Step 2: 挂到 `default.py`**

在 `about.render()` 后：

```python
from facefusion.uis.components import language
# render:
language.render()
# listen:
language.listen()
```

同步检查 `webcam`/`benchmark`/`jobs` 布局：若也有 about，按同样方式挂载；否则至少保证 `default`。

- [ ] **Step 3: 手动验证**

启动 UI，切换语言，确认 `facefusion.ini` 出现 `language = zh`，Toast 提示刷新；刷新后标签语言变化。

- [ ] **Step 4: 提交**

```bash
git add facefusion/uis/components/language.py facefusion/uis/layouts/default.py facefusion/uis/types.py
git commit -m "feat: add language preference dropdown to the UI"
```

---

### Task 6: 处理器选项 `id【gloss】`

**Files:**
- Modify: `facefusion/uis/components/processors.py`
- Create or extend: `tests/test_locales_helper.py`（可选组合函数测试）

**Interfaces:**
- Consumes: `format_choice_label`, `translator.get('choices.processors.<id>')`
- Produces: CheckboxGroup choices 为 `(label, value)`，value 为原始 id

- [ ] **Step 1: 增加 choice 构建函数**

```python
from facefusion.locales_helper import format_choice_label

def build_processor_choices(processors : List[str]) -> List[tuple[str, str]]:
	choices = []
	for processor in sort_processors(processors):
		gloss = translator.get('choices.processors.' + processor)
		label = format_choice_label(processor, gloss)
		choices.append((label, processor))
	return choices
```

- [ ] **Step 2: 改 `render` / `update_processors`**

```python
PROCESSORS_CHECKBOX_GROUP = gradio.CheckboxGroup(
	label = translator.get('uis.processors_checkbox_group'),
	choices = build_processor_choices(state_manager.get_item('processors')),
	value = state_manager.get_item('processors')
)
```

`update_processors` 返回时同样用 `build_processor_choices`；`value` 必须是原始 id 列表。  
`remote_update` 下游组件用 `'face_swapper' in processors` 判断 —— 确认 Gradio 传回的是 value 而非 label（元组 choices 时应为 value）。

- [ ] **Step 3: 手动验证中文界面**

期望看到 `face_enhancer【面部增强】`；勾选后 state/处理仍使用 `face_enhancer`。

- [ ] **Step 4: 提交**

```bash
git add facefusion/uis/components/processors.py
git commit -m "feat: show processor ids with Chinese gloss labels"
```

---

### Task 7: `ℹ️` 帮助辅助函数 + 处理器组

**Files:**
- Create: `facefusion/uis/help_helper.py`
- Modify: `facefusion/uis/components/processors.py`
- Modify: `facefusion/uis/assets/overrides.css`（可选微调按钮样式）

**Interfaces:**
- Produces: `help_helper.render_help_button(notation: str, module_name: str = 'facefusion') -> gradio.Button`
- Produces: `help_helper.listen_help_button(button, notation, module_name)`

- [ ] **Step 1: 实现 help_helper**

```python
from typing import Optional

import gradio

from facefusion import translator


def render_help_button(notation : str, module_name : str = 'facefusion') -> gradio.Button:
	text = translator.get(notation, module_name) or ''
	return gradio.Button(
		value = 'ℹ️',
		size = 'sm',
		min_width = 40,
		elem_classes = [ 'ff-help-button' ],
		elem_id = None
	)


def show_help(notation : str, module_name : str = 'facefusion') -> None:
	message = translator.get(notation, module_name)
	if message:
		gradio.Info(message)
```

在 `processors.render` 中用 `gradio.Row`：左侧 CheckboxGroup，右侧或标签旁放 `ℹ️`；`listen` 里 `help_button.click(lambda: show_help('uis_help.processors'), ...)`。

若需按「当前勾选」显示更具体说明，v1 先做组级 `uis_help.processors` 即可；可选：点击时根据第一个选中项显示 `uis_help.processors_face_swapper`。

- [ ] **Step 2: CSS（可选）**

```css
:root:root:root:root .ff-help-button {
	min-width: 2.5rem !important;
	max-width: 2.5rem;
	padding: 0 !important;
}
```

- [ ] **Step 3: 手动点 `ℹ️` 看到中英文说明**

- [ ] **Step 4: 提交**

```bash
git add facefusion/uis/help_helper.py facefusion/uis/components/processors.py facefusion/uis/assets/overrides.css
git commit -m "feat: add processor help info button"
```

---

### Task 8: 各处理器选项旁加 `ℹ️`

**Files:**
- Modify:  
  `facefusion/uis/components/face_swapper_options.py`  
  `facefusion/uis/components/face_enhancer_options.py`  
  `facefusion/uis/components/frame_enhancer_options.py`  
  `facefusion/uis/components/expression_restorer_options.py`  
  `facefusion/uis/components/age_modifier_options.py`  
  `facefusion/uis/components/deep_swapper_options.py`  
  `facefusion/uis/components/lip_syncer_options.py`  
  `facefusion/uis/components/frame_colorizer_options.py`  
  `facefusion/uis/components/face_editor_options.py`  
  `facefusion/uis/components/face_debugger_options.py`  
  `facefusion/uis/components/background_remover_options.py`  
  （以及 `voice_extractor.py` 若视为处理器相关且在默认布局处理器区）

**Interfaces:**
- Consumes: `help_helper.render_help_button` / `show_help`
- Consumes: 模块 locales 的 `uis_help.*`

- [ ] **Step 1: 以 `face_swapper_options` 为模板**

每个主要控件用 Row 包一层：控件 + `ℹ️`。

```python
with gradio.Row():
	FACE_SWAPPER_MODEL_DROPDOWN = gradio.Dropdown(...)
	model_help = help_helper.render_help_button('uis_help.model', 'facefusion.processors.modules.face_swapper')
```

`listen`：

```python
model_help.click(lambda: help_helper.show_help('uis_help.model', 'facefusion.processors.modules.face_swapper'))
```

对 `pixel_boost`、`weight` 同样处理。可见性与原控件 `visible` 联动（help 按钮 `visible=has_face_swapper`）。

- [ ] **Step 2: 复制模式到其余处理器 options 组件**

每个模块至少覆盖：**model** + 其他主要滑块/下拉（weight/blend/morph/factor/areas/items/colors 等 UI 已有项）。

- [ ] **Step 3: 手动抽查 face_swapper / face_enhancer / expression_restorer**

- [ ] **Step 4: 提交**

```bash
git add facefusion/uis/components/*_options.py
git commit -m "feat: add help buttons to processor option controls"
```

---

### Task 9: 回归与收尾

**Files:**
- 按需小修
- 可选：中文版计划已在 `docs/superpowers/plans/`；确认 README 不强制改动（YAGNI）

- [ ] **Step 1: 跑相关测试**

```bash
conda activate facefusion
pip install pytest -q
pytest tests/test_locales_helper.py tests/test_config.py tests/test_translator.py -v
```

Expected: PASS

- [ ] **Step 2: 端到端手工清单**

1. `language=` 空 → 跟随系统  
2. UI 选中文 → ini 为 `zh` → 刷新 → 中文标签  
3. 处理器显示 `face_swapper【换脸】`  
4. 勾选换脸仍能预览/处理  
5. `ℹ️` 组级与选项级有说明  
6. 切回 English → 刷新 → 无 `【】`，帮助为英文  

- [ ] **Step 3: 最终提交（若有修修补补）**

```bash
git status
git add -A
git commit -m "chore: finalize UI language preference feature"
```

- [ ] **Step 4:（可选）推送到 fork**

```bash
git push -u origin feature/ui-language
```

仅在用户明确要求 push 时执行。

---

## Spec coverage self-check

| 规格要求 | 对应任务 |
|---|---|
| `uis.language` system/en/zh | Task 1–3, 5 |
| 系统语言探测 | Task 1 |
| 写回 ini + 刷新提示 | Task 2, 5 |
| 启动解析 set_language | Task 3 |
| 无 CLI `--language` | Task 3（仅 config） |
| `id【gloss】` + value 为 id | Task 4, 6 |
| `ℹ️` 处理器 + 选项 | Task 4, 7, 8 |
| 英文回退 | Task 1 translator |
| 不做热切换 / 模型名不加【】 | 全局约束，未列入实现 |
| 测试计划 | Task 1,2,4,9 |

## Placeholder scan

无 TBD/TODO 占位步骤；关键函数均给出签名与示例代码。

## Type consistency

- 偏好类型统一为 `LanguagePreference`（`system|en|zh`）
- 生效类型统一为 `Language`（`en|zh`）
- state 键名统一为 `language`
- 帮助文案键：主包 `uis_help.*`，处理器模块 `uis_help.*`
