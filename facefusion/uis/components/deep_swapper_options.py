from typing import List, Optional, Tuple

import gradio

from facefusion import state_manager, translator
from facefusion.common_helper import calculate_int_step
from facefusion.processors.core import load_processor_module
from facefusion.processors.modules.deep_swapper import choices as deep_swapper_choices
from facefusion.processors.modules.deep_swapper.types import DeepSwapperModel
from facefusion.uis import help_helper
from facefusion.uis.core import get_ui_component, register_ui_component

MODULE_NAME = 'facefusion.processors.modules.deep_swapper'

DEEP_SWAPPER_MODEL_DROPDOWN : Optional[gradio.Dropdown] = None
DEEP_SWAPPER_MODEL_HELP_BUTTON : Optional[gradio.Button] = None
DEEP_SWAPPER_MORPH_SLIDER : Optional[gradio.Slider] = None
DEEP_SWAPPER_MORPH_HELP_BUTTON : Optional[gradio.Button] = None


def render() -> None:
	global DEEP_SWAPPER_MODEL_DROPDOWN
	global DEEP_SWAPPER_MODEL_HELP_BUTTON
	global DEEP_SWAPPER_MORPH_SLIDER
	global DEEP_SWAPPER_MORPH_HELP_BUTTON

	has_deep_swapper = 'deep_swapper' in state_manager.get_item('processors')
	morph_visible = has_deep_swapper and load_processor_module('deep_swapper').get_inference_pool() and load_processor_module('deep_swapper').has_morph_input()
	with gradio.Row():
		DEEP_SWAPPER_MODEL_DROPDOWN = gradio.Dropdown(
			label = translator.get('uis.model_dropdown', MODULE_NAME),
			choices = deep_swapper_choices.deep_swapper_models,
			value = state_manager.get_item('deep_swapper_model'),
			visible = has_deep_swapper
		)
		DEEP_SWAPPER_MODEL_HELP_BUTTON = help_helper.render_help_button('uis_help.model', MODULE_NAME, visible = has_deep_swapper)
	with gradio.Row():
		DEEP_SWAPPER_MORPH_SLIDER = gradio.Slider(
			label = translator.get('uis.morph_slider', MODULE_NAME),
			value = state_manager.get_item('deep_swapper_morph'),
			step = calculate_int_step(deep_swapper_choices.deep_swapper_morph_range),
			minimum = deep_swapper_choices.deep_swapper_morph_range[0],
			maximum = deep_swapper_choices.deep_swapper_morph_range[-1],
			visible = morph_visible
		)
		DEEP_SWAPPER_MORPH_HELP_BUTTON = help_helper.render_help_button('uis_help.morph', MODULE_NAME, visible = morph_visible)
	register_ui_component('deep_swapper_model_dropdown', DEEP_SWAPPER_MODEL_DROPDOWN)
	register_ui_component('deep_swapper_morph_slider', DEEP_SWAPPER_MORPH_SLIDER)


def listen() -> None:
	DEEP_SWAPPER_MODEL_DROPDOWN.change(update_deep_swapper_model, inputs = DEEP_SWAPPER_MODEL_DROPDOWN, outputs = [ DEEP_SWAPPER_MODEL_DROPDOWN, DEEP_SWAPPER_MORPH_SLIDER, DEEP_SWAPPER_MORPH_HELP_BUTTON ])
	DEEP_SWAPPER_MORPH_SLIDER.release(update_deep_swapper_morph, inputs = DEEP_SWAPPER_MORPH_SLIDER)
	help_helper.listen_help_button(DEEP_SWAPPER_MODEL_HELP_BUTTON, 'uis_help.model', MODULE_NAME)
	help_helper.listen_help_button(DEEP_SWAPPER_MORPH_HELP_BUTTON, 'uis_help.morph', MODULE_NAME)

	processors_checkbox_group = get_ui_component('processors_checkbox_group')
	if processors_checkbox_group:
		processors_checkbox_group.change(remote_update, inputs = processors_checkbox_group, outputs = [ DEEP_SWAPPER_MODEL_DROPDOWN, DEEP_SWAPPER_MODEL_HELP_BUTTON, DEEP_SWAPPER_MORPH_SLIDER, DEEP_SWAPPER_MORPH_HELP_BUTTON ])


def remote_update(processors : List[str]) -> Tuple[gradio.Dropdown, gradio.Button, gradio.Slider, gradio.Button]:
	has_deep_swapper = 'deep_swapper' in processors
	morph_visible = has_deep_swapper and load_processor_module('deep_swapper').get_inference_pool() and load_processor_module('deep_swapper').has_morph_input()
	return gradio.Dropdown(visible = has_deep_swapper), gradio.Button(visible = has_deep_swapper), gradio.Slider(visible = morph_visible), gradio.Button(visible = morph_visible)


def update_deep_swapper_model(deep_swapper_model : DeepSwapperModel) -> Tuple[gradio.Dropdown, gradio.Slider, gradio.Button]:
	deep_swapper_module = load_processor_module('deep_swapper')
	deep_swapper_module.clear_inference_pool()
	state_manager.set_item('deep_swapper_model', deep_swapper_model)

	if deep_swapper_module.pre_check():
		morph_visible = deep_swapper_module.has_morph_input()
		return gradio.Dropdown(value = state_manager.get_item('deep_swapper_model')), gradio.Slider(visible = morph_visible), gradio.Button(visible = morph_visible)
	return gradio.Dropdown(), gradio.Slider(), gradio.Button()


def update_deep_swapper_morph(deep_swapper_morph : int) -> None:
	state_manager.set_item('deep_swapper_morph', deep_swapper_morph)
