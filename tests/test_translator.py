from facefusion import translator
from facefusion.locales import LOCALES


def test_load() -> None:
	translator.load(LOCALES, __name__)

	assert __name__ in translator.LOCALE_POOL_SET


def test_get() -> None:
	translator.set_language('en')
	assert translator.get('conda_not_activated') == 'conda is not activated'
	assert translator.get('invalid') is None

	translator.set_language('zh')
	assert translator.get_language() == 'zh'


def test_zh_ui_strings() -> None:
	translator.set_language('zh')
	assert translator.get('uis.language_dropdown') == '语言'
	assert translator.get('choices.processors.face_enhancer') == '面部增强'
