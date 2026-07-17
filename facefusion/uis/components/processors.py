from typing import List, Optional

import gradio

from facefusion import state_manager, translator
from facefusion.filesystem import get_file_name, resolve_file_paths
from facefusion.locales_helper import format_choice_label
from facefusion.processors.core import get_processors_modules
from facefusion.uis import help_helper
from facefusion.uis.core import register_ui_component

PROCESSORS_CHECKBOX_GROUP : Optional[gradio.CheckboxGroup] = None
PROCESSORS_HELP_BUTTON : Optional[gradio.Button] = None


def render() -> None:
	global PROCESSORS_CHECKBOX_GROUP
	global PROCESSORS_HELP_BUTTON

	with gradio.Row():
		PROCESSORS_CHECKBOX_GROUP = gradio.CheckboxGroup(
			label = translator.get('uis.processors_checkbox_group'),
			choices = build_processor_choices(state_manager.get_item('processors')),
			value = state_manager.get_item('processors')
		)
		PROCESSORS_HELP_BUTTON = help_helper.render_help_button('uis_help.processors')
	register_ui_component('processors_checkbox_group', PROCESSORS_CHECKBOX_GROUP)


def listen() -> None:
	PROCESSORS_CHECKBOX_GROUP.change(update_processors, inputs = PROCESSORS_CHECKBOX_GROUP, outputs = PROCESSORS_CHECKBOX_GROUP)
	help_helper.listen_help_button(PROCESSORS_HELP_BUTTON, 'uis_help.processors')


def update_processors(processors : List[str]) -> gradio.CheckboxGroup:
	for processor_module in get_processors_modules(state_manager.get_item('processors')):
		if hasattr(processor_module, 'clear_inference_pool'):
			processor_module.clear_inference_pool()

	for processor_module in get_processors_modules(processors):
		if not processor_module.pre_check():
			return gradio.CheckboxGroup()

	state_manager.set_item('processors', processors)
	return gradio.CheckboxGroup(value = state_manager.get_item('processors'), choices = build_processor_choices(state_manager.get_item('processors')))


def build_processor_choices(processors : List[str]) -> List[tuple[str, str]]:
	choices = []
	for processor in sort_processors(processors):
		gloss = translator.get('choices.processors.' + processor)
		label = format_choice_label(processor, gloss)
		choices.append((label, processor))
	return choices


def sort_processors(processors : List[str]) -> List[str]:
	available_processors = [ get_file_name(file_path) for file_path in resolve_file_paths('facefusion/processors/modules') ]
	current_processors = []

	for processor in processors + available_processors:
		if processor in available_processors and processor not in current_processors:
			current_processors.append(processor)

	return current_processors
