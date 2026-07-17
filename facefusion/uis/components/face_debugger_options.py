from typing import List, Optional, Tuple

import gradio

from facefusion import state_manager, translator
from facefusion.processors.modules.face_debugger import choices as face_debugger_choices
from facefusion.processors.modules.face_debugger.types import FaceDebuggerItem
from facefusion.uis import help_helper
from facefusion.uis.core import get_ui_component, register_ui_component

MODULE_NAME = 'facefusion.processors.modules.face_debugger'

FACE_DEBUGGER_ITEMS_CHECKBOX_GROUP : Optional[gradio.CheckboxGroup] = None
FACE_DEBUGGER_ITEMS_HELP_BUTTON : Optional[gradio.Button] = None


def render() -> None:
	global FACE_DEBUGGER_ITEMS_CHECKBOX_GROUP
	global FACE_DEBUGGER_ITEMS_HELP_BUTTON

	has_face_debugger = 'face_debugger' in state_manager.get_item('processors')
	with gradio.Row():
		FACE_DEBUGGER_ITEMS_CHECKBOX_GROUP = gradio.CheckboxGroup(
			label = translator.get('uis.items_checkbox_group', MODULE_NAME),
			choices = face_debugger_choices.face_debugger_items,
			value = state_manager.get_item('face_debugger_items'),
			visible = has_face_debugger
		)
		FACE_DEBUGGER_ITEMS_HELP_BUTTON = help_helper.render_help_button('uis_help.items', MODULE_NAME, visible = has_face_debugger)
	register_ui_component('face_debugger_items_checkbox_group', FACE_DEBUGGER_ITEMS_CHECKBOX_GROUP)


def listen() -> None:
	FACE_DEBUGGER_ITEMS_CHECKBOX_GROUP.change(update_face_debugger_items, inputs = FACE_DEBUGGER_ITEMS_CHECKBOX_GROUP)
	help_helper.listen_help_button(FACE_DEBUGGER_ITEMS_HELP_BUTTON, 'uis_help.items', MODULE_NAME)

	processors_checkbox_group = get_ui_component('processors_checkbox_group')
	if processors_checkbox_group:
		processors_checkbox_group.change(remote_update, inputs = processors_checkbox_group, outputs = [ FACE_DEBUGGER_ITEMS_CHECKBOX_GROUP, FACE_DEBUGGER_ITEMS_HELP_BUTTON ])


def remote_update(processors : List[str]) -> Tuple[gradio.CheckboxGroup, gradio.Button]:
	has_face_debugger = 'face_debugger' in processors
	return gradio.CheckboxGroup(visible = has_face_debugger), gradio.Button(visible = has_face_debugger)


def update_face_debugger_items(face_debugger_items : List[FaceDebuggerItem]) -> None:
	state_manager.set_item('face_debugger_items', face_debugger_items)
