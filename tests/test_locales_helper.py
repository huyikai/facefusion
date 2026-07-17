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
