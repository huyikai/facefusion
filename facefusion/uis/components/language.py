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
