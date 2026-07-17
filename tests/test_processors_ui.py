from facefusion import translator
from facefusion.locales import LOCALES
from facefusion.uis.components.processors import build_processor_choices


def test_build_processor_choices_zh() -> None:
	translator.load(LOCALES, __name__)
	translator.set_language('zh')

	choices = build_processor_choices([ 'face_enhancer', 'face_swapper' ])
	choice_map = { value: label for label, value in choices }

	assert choice_map['face_enhancer'] == 'face_enhancer【面部增强】'
	assert choice_map['face_swapper'] == 'face_swapper【换脸】'
	assert all(isinstance(value, str) for value in choice_map)


def test_build_processor_choices_en() -> None:
	translator.load(LOCALES, __name__)
	translator.set_language('en')

	choices = build_processor_choices([ 'face_enhancer' ])
	choice_map = { value: label for label, value in choices }

	assert choice_map['face_enhancer'] == 'face_enhancer'
