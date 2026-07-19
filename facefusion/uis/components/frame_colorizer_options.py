from typing import List, Optional, Tuple

import gradio

from facefusion import state_manager, translator
from facefusion.common_helper import calculate_int_step
from facefusion.processors.core import load_processor_module
from facefusion.processors.modules.frame_colorizer import choices as frame_colorizer_choices
from facefusion.processors.modules.frame_colorizer.types import FrameColorizerModel
from facefusion.uis import help_helper
from facefusion.uis.core import get_ui_component, register_ui_component

MODULE_NAME = 'facefusion.processors.modules.frame_colorizer'

FRAME_COLORIZER_MODEL_LABEL_ROW : Optional[gradio.Row] = None
FRAME_COLORIZER_MODEL_DROPDOWN : Optional[gradio.Dropdown] = None
FRAME_COLORIZER_MODEL_HELP_BUTTON : Optional[gradio.Button] = None
FRAME_COLORIZER_SIZE_LABEL_ROW : Optional[gradio.Row] = None
FRAME_COLORIZER_SIZE_DROPDOWN : Optional[gradio.Dropdown] = None
FRAME_COLORIZER_SIZE_HELP_BUTTON : Optional[gradio.Button] = None
FRAME_COLORIZER_BLEND_LABEL_ROW : Optional[gradio.Row] = None
FRAME_COLORIZER_BLEND_SLIDER : Optional[gradio.Slider] = None
FRAME_COLORIZER_BLEND_HELP_BUTTON : Optional[gradio.Button] = None


def render() -> None:
	global FRAME_COLORIZER_MODEL_LABEL_ROW
	global FRAME_COLORIZER_MODEL_DROPDOWN
	global FRAME_COLORIZER_MODEL_HELP_BUTTON
	global FRAME_COLORIZER_SIZE_LABEL_ROW
	global FRAME_COLORIZER_SIZE_DROPDOWN
	global FRAME_COLORIZER_SIZE_HELP_BUTTON
	global FRAME_COLORIZER_BLEND_LABEL_ROW
	global FRAME_COLORIZER_BLEND_SLIDER
	global FRAME_COLORIZER_BLEND_HELP_BUTTON

	has_frame_colorizer = 'frame_colorizer' in state_manager.get_item('processors')
	model_label = translator.get('uis.model_dropdown', MODULE_NAME)
	size_label = translator.get('uis.size_dropdown', MODULE_NAME)
	blend_label = translator.get('uis.blend_slider', MODULE_NAME)

	FRAME_COLORIZER_MODEL_LABEL_ROW, FRAME_COLORIZER_MODEL_HELP_BUTTON = help_helper.render_help_label(model_label, 'uis_help.model', MODULE_NAME, visible = has_frame_colorizer)
	FRAME_COLORIZER_MODEL_DROPDOWN = gradio.Dropdown(
		label = model_label,
		show_label = False,
		choices = frame_colorizer_choices.frame_colorizer_models,
		value = state_manager.get_item('frame_colorizer_model'),
		visible = has_frame_colorizer
	)
	FRAME_COLORIZER_SIZE_LABEL_ROW, FRAME_COLORIZER_SIZE_HELP_BUTTON = help_helper.render_help_label(size_label, 'uis_help.size', MODULE_NAME, visible = has_frame_colorizer)
	FRAME_COLORIZER_SIZE_DROPDOWN = gradio.Dropdown(
		label = size_label,
		show_label = False,
		choices = frame_colorizer_choices.frame_colorizer_sizes,
		value = state_manager.get_item('frame_colorizer_size'),
		visible = has_frame_colorizer
	)
	FRAME_COLORIZER_BLEND_LABEL_ROW, FRAME_COLORIZER_BLEND_HELP_BUTTON = help_helper.render_help_label(blend_label, 'uis_help.blend', MODULE_NAME, visible = has_frame_colorizer)
	FRAME_COLORIZER_BLEND_SLIDER = gradio.Slider(
		label = blend_label,
		show_label = False,
		value = state_manager.get_item('frame_colorizer_blend'),
		step = calculate_int_step(frame_colorizer_choices.frame_colorizer_blend_range),
		minimum = frame_colorizer_choices.frame_colorizer_blend_range[0],
		maximum = frame_colorizer_choices.frame_colorizer_blend_range[-1],
		visible = has_frame_colorizer
	)
	register_ui_component('frame_colorizer_model_dropdown', FRAME_COLORIZER_MODEL_DROPDOWN)
	register_ui_component('frame_colorizer_size_dropdown', FRAME_COLORIZER_SIZE_DROPDOWN)
	register_ui_component('frame_colorizer_blend_slider', FRAME_COLORIZER_BLEND_SLIDER)


def listen() -> None:
	FRAME_COLORIZER_MODEL_DROPDOWN.change(update_frame_colorizer_model, inputs = FRAME_COLORIZER_MODEL_DROPDOWN, outputs = FRAME_COLORIZER_MODEL_DROPDOWN)
	FRAME_COLORIZER_SIZE_DROPDOWN.change(update_frame_colorizer_size, inputs = FRAME_COLORIZER_SIZE_DROPDOWN)
	FRAME_COLORIZER_BLEND_SLIDER.release(update_frame_colorizer_blend, inputs = FRAME_COLORIZER_BLEND_SLIDER)
	help_helper.listen_help_button(FRAME_COLORIZER_MODEL_HELP_BUTTON, 'uis_help.model', MODULE_NAME)
	help_helper.listen_help_button(FRAME_COLORIZER_SIZE_HELP_BUTTON, 'uis_help.size', MODULE_NAME)
	help_helper.listen_help_button(FRAME_COLORIZER_BLEND_HELP_BUTTON, 'uis_help.blend', MODULE_NAME)

	processors_checkbox_group = get_ui_component('processors_checkbox_group')
	if processors_checkbox_group:
		processors_checkbox_group.change(remote_update, inputs = processors_checkbox_group, outputs = [ FRAME_COLORIZER_MODEL_LABEL_ROW, FRAME_COLORIZER_MODEL_DROPDOWN, FRAME_COLORIZER_SIZE_LABEL_ROW, FRAME_COLORIZER_SIZE_DROPDOWN, FRAME_COLORIZER_BLEND_LABEL_ROW, FRAME_COLORIZER_BLEND_SLIDER ])


def remote_update(processors : List[str]) -> Tuple[gradio.Row, gradio.Dropdown, gradio.Row, gradio.Dropdown, gradio.Row, gradio.Slider]:
	has_frame_colorizer = 'frame_colorizer' in processors
	return gradio.Row(visible = has_frame_colorizer), gradio.Dropdown(visible = has_frame_colorizer), gradio.Row(visible = has_frame_colorizer), gradio.Dropdown(visible = has_frame_colorizer), gradio.Row(visible = has_frame_colorizer), gradio.Slider(visible = has_frame_colorizer)


def update_frame_colorizer_model(frame_colorizer_model : FrameColorizerModel) -> gradio.Dropdown:
	frame_colorizer_module = load_processor_module('frame_colorizer')
	frame_colorizer_module.clear_inference_pool()
	state_manager.set_item('frame_colorizer_model', frame_colorizer_model)

	if frame_colorizer_module.pre_check():
		return gradio.Dropdown(value = state_manager.get_item('frame_colorizer_model'))
	return gradio.Dropdown()


def update_frame_colorizer_size(frame_colorizer_size : str) -> None:
	state_manager.set_item('frame_colorizer_size', frame_colorizer_size)


def update_frame_colorizer_blend(frame_colorizer_blend : float) -> None:
	state_manager.set_item('frame_colorizer_blend', int(frame_colorizer_blend))
