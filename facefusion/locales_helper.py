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
