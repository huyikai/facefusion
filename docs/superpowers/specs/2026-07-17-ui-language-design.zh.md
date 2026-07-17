# UI 语言偏好设计（中文版）

**日期：** 2026-07-17  
**仓库：** https://github.com/huyikai/facefusion（fork 自 facefusion/facefusion）  
**状态：** 待你审阅确认后进入实现  
**英文版：** [2026-07-17-ui-language-design.md](./2026-07-17-ui-language-design.md)

> 本文与英文版内容等价，便于阅读。实现以两份文档共同约定为准；若有冲突以你确认过的最新约定为准。

## 目标

为界面增加语言偏好，使用户可以：

1. 默认跟随系统语言
2. 在 Web UI 中用下拉框覆盖
3. 将偏好持久化到 `facefusion.ini`
4. 刷新页面后生效（不做热切换）

## 已锁定决策

| 主题 | 决策 |
|---|---|
| 切换入口 | 仅界面（v1 不加 `--language` CLI） |
| 持久化 | 写入 `facefusion.ini` 的 `uis.language` |
| 生效时机 | 保存 + Toast 提示；用户刷新页面 |
| 实现方案 | 配置驱动 + UI 下拉（方案 A） |
| v1 语言 | `system` / `en` / `zh` |
| 中文技术选项文案 | 保留英文 id，追加 `【中文说明】`，不替换 id |
| 参数说明交互 | `ℹ️` 图标，悬停/点击查看（不用常驻 `info=` 长文） |
| 说明覆盖范围（v1） | 仅处理器及相关主要选项 |

## 配置模型

在 `facefusion.ini` 的 `[uis]` 下增加：

```ini
[uis]
language = system
```

### 类型

- `LanguagePreference = Literal['system', 'en', 'zh']` — 配置/UI 中的偏好值
- `Language = Literal['en', 'zh']` — 解析后真正生效的语言

### 解析规则

1. 读取 `uis.language`；为空/缺失 → 视为 `system`
2. 若偏好为 `en` 或 `zh` → 直接作为生效语言
3. 若偏好为 `system`：
   - 读取系统 locale（`locale.getdefaultlocale()` / `locale.getlocale()`，必要时辅以常见环境变量）
   - 语言标签以 `zh` 开头（忽略大小写）→ `zh`
   - 否则 → `en`
4. 未知偏好 → `en`
5. 当前语言缺少词条 → 回退到英文词条

在 `run` / UI 启动早期调用 `translator.set_language(resolved)`，确保 Gradio 标签按正确语言渲染。

## 界面设计

新组件：`facefusion/uis/components/language.py`

- 位置：默认布局左上角附近（`about` 旁），主界面可见
- 控件：Gradio `Dropdown`
- 标签：走 locales（`uis.language_dropdown`）
- 选项展示：
  - `system` → 跟随系统 / Follow System
  - `en` → English
  - `zh` → 中文
- 下拉框的**值**是偏好（`system|en|zh`），不是解析后的实际语言

### 变更时

1. 更新内存中的 state（`language` 偏好）
2. 写入 `facefusion.ini` → `[uis] language = ...`
3. 用 `gr.Info` 提示：**语言已保存，请刷新页面生效**

不对已渲染控件做热更新。

## 中文界面的技术选项文案

部分选项是**技术标识**（尤其是处理器模块名）。若整段改成中文，用户对照文档、日志、配置会困难。

### 展示规则（生效语言为 `zh` 时）

```text
{英文id}【{中文说明}】
```

示例：

- `face_enhancer【面部增强】`
- `face_swapper【换脸】`
- `frame_enhancer【画面增强】`

生效语言为 `en` 时，只显示英文 id（不加括号）。

### 值规则（关键）

- **界面展示**可以带 `【…】`
- **存储/提交的值**必须仍是原始英文 id（如 `face_enhancer`）
- 使用 Gradio choice 元组 `(label, value)`，保证 state、任务、命令行兼容

### 范围（v1）

要加注解的：

- 处理器复选框选项（`face_swapper`、`face_enhancer`，…）

暂不做：

- 模型文件名 / 模型 id（保持纯英文）
- Gradio 内置控件文案（上传提示等）

可选后续：人脸选择模式等枚举（`one` / `many` / `reference`）是否同样用 `【】`，实现时可再定。

### 词条

在 locales 中增加词汇表，例如 `choices.processors.face_enhancer = 面部增强`，渲染时拼成 `f"{id}【{gloss}】"`。

## 参数说明（`ℹ️` 图标）

很多名词、模型即便有中文注解，仍看不出用途。用 **ℹ️** 提供短说明，而不是在每个控件下常驻长文。

### 交互

- 在控件标签 / 选项组旁显示 `ℹ️`（或 Gradio 可用的等价提示入口）
- **悬停**（桌面）和/或 **点击/轻触**（触控板、手机）显示说明
- 文案来自 locales（现有 `help.*` 或新建 `uis_help.*`），中英文都有
- 保持简短：1～2 句，说明做什么、何时调整

### 实现注意

- 优先 Gradio 原生能力（支持则用 tooltip；否则小按钮 + `gr.Info` / 弹层 Markdown）
- 不得改变存储值或处理器逻辑
- 若真实 tooltip 难做，可接受降级：点击 `ℹ️` 弹出同样文案
- 英文界面同样显示 `ℹ️`（英文说明）

### 范围（v1）

**要做：**

- 处理器复选组（`face_swapper`、`face_enhancer`，…）— 可为每个处理器写短说明，也可有组级说明
- 各处理器主要选项：model / weight / blend / pixel boost / morph / factor / areas 等（UI 已暴露的项）

**v1 不做：**

- 人脸检测 / 选择 / 蒙版 / 跟踪
- 输出、执行、下载、内存等区块
- Webcam / benchmark / jobs 等与处理器无关的额外界面

后续可复用同一套 `ℹ️` 模式扩展到其他区块。

## 配置读写

`facefusion/config.py` 目前只读。新增：

- `set_str_value(section, option, value)`：
  - 打开当前 `config_path`
  - 确保 section 存在
  - 写入 option
  - UTF-8 写回文件
  - 清除 `get_static_config_parser` 的 LRU 缓存

v1 仅用于语言偏好，控制范围。

## 代码改动清单

| 区域 | 改动 |
|---|---|
| `facefusion/types.py` | 增加 `LanguagePreference`；扩展 `Language`；state 增加 `language` |
| `facefusion/choices.py` | `language_preferences` 列表 |
| `facefusion/translator.py` | 保留 `set_language` 与英文回退；启动时按偏好解析，不再写死 `zh` |
| `facefusion/config.py` | `set_str_value` |
| `facefusion/program.py` / `args.py` | 从配置读取 `uis.language`（无新 CLI） |
| UI 启动路径 | resolve → `translator.set_language` 后再渲染 |
| `facefusion/uis/components/language.py` | 新下拉组件 |
| `facefusion/uis/layouts/default.py` 等 | 挂载语言组件 |
| `facefusion/locales.py` + processor locales | 保留 `en`/`zh`；补语言 UI 文案与处理器词汇表 |
| `facefusion/uis/components/processors.py` | 中文显示 `id【gloss】`，值仍为原始 id；加 `ℹ️` |
| 各处理器选项 UI 组件 | 在 model/weight/blend/… 旁加 `ℹ️` |
| `facefusion.ini` | `[uis]` 下增加 `language =` |
| `tests/test_translator.py` 等 | 覆盖解析、回退、set_language、标签拼接 |

## 非目标（v1）

- 不刷新就热切换全部标签
- 翻译 Gradio 内置文案（上传提示等）
- `en` / `zh` 以外的语言
- CLI `--language`
- 先不强制做向上游的 PR（先在 fork 落地）

## 测试计划

1. 单元：偏好 `system` + 模拟 `zh_*` locale → 解析为 `zh`
2. 单元：偏好 `system` + 模拟 `en_*` locale → 解析为 `en`
3. 单元：偏好 `zh` / `en` 时忽略系统语言
4. 单元：缺中文词条时回退英文
5. 单元：`set_str_value` 写入后能读回
6. 手工：改下拉 → ini 更新 → 刷新 → 界面语言正确
7. 手工（中文）：处理器显示 `id【gloss】`；`ℹ️` 能看到短说明
8. 手工（英文）：处理器仍为纯 id；`ℹ️` 仍有英文说明

## 仓库说明

- 设计时本地目录曾无 `.git`；实现分支跟踪 `https://github.com/huyikai/facefusion.git`
- 建议分支：`feature/ui-language`
- 本地已有中文词条可复用；去掉写死的 `CURRENT_LANGUAGE = 'zh'`，改为按偏好解析

## 成功标准

- 新安装且 `language` 为空时跟随系统
- 可在 UI 强制英文或中文
- 重启后偏好仍在（`facefusion.ini`）
- 刷新后语言生效；Toast 提示需刷新
- 无界面命令仍可用（从 ini/系统解析语言也安全）
- 中文界面处理器选项为 `id【gloss】`，值为原始 id
- 处理器组及主要选项在中英文下都提供 `ℹ️` 说明

## 修订记录

- 2026-07-17：初版设计（UI 语言偏好）
- 2026-07-17：增加中文技术文案格式 `id【gloss】`
- 2026-07-17：增加 `ℹ️` 说明；v1 仅覆盖处理器及相关选项
- 2026-07-17：新增中文版规格文件
