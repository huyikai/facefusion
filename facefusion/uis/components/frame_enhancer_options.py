from typing import List, Optional, Tuple

import gradio

from facefusion import state_manager, translator
from facefusion.common_helper import calculate_int_step
from facefusion.processors.core import load_processor_module
from facefusion.processors.modules.frame_enhancer import choices as frame_enhancer_choices
from facefusion.processors.modules.frame_enhancer.types import FrameEnhancerModel
from facefusion.uis import help_helper
from facefusion.uis.core import get_ui_component, register_ui_component

MODULE_NAME = 'facefusion.processors.modules.frame_enhancer'

FRAME_ENHANCER_MODEL_LABEL_ROW : Optional[gradio.Row] = None
FRAME_ENHANCER_MODEL_DROPDOWN : Optional[gradio.Dropdown] = None
FRAME_ENHANCER_MODEL_HELP_BUTTON : Optional[gradio.Button] = None
FRAME_ENHANCER_BLEND_LABEL_ROW : Optional[gradio.Row] = None
FRAME_ENHANCER_BLEND_SLIDER : Optional[gradio.Slider] = None
FRAME_ENHANCER_BLEND_HELP_BUTTON : Optional[gradio.Button] = None


def render() -> None:
	global FRAME_ENHANCER_MODEL_LABEL_ROW
	global FRAME_ENHANCER_MODEL_DROPDOWN
	global FRAME_ENHANCER_MODEL_HELP_BUTTON
	global FRAME_ENHANCER_BLEND_LABEL_ROW
	global FRAME_ENHANCER_BLEND_SLIDER
	global FRAME_ENHANCER_BLEND_HELP_BUTTON

	has_frame_enhancer = 'frame_enhancer' in state_manager.get_item('processors')
	model_label = translator.get('uis.model_dropdown', MODULE_NAME)
	blend_label = translator.get('uis.blend_slider', MODULE_NAME)

	FRAME_ENHANCER_MODEL_LABEL_ROW, FRAME_ENHANCER_MODEL_HELP_BUTTON = help_helper.render_help_label(model_label, 'uis_help.model', MODULE_NAME, visible = has_frame_enhancer)
	FRAME_ENHANCER_MODEL_DROPDOWN = gradio.Dropdown(
		label = model_label,
		show_label = False,
		choices = frame_enhancer_choices.frame_enhancer_models,
		value = state_manager.get_item('frame_enhancer_model'),
		visible = has_frame_enhancer
	)
	FRAME_ENHANCER_BLEND_LABEL_ROW, FRAME_ENHANCER_BLEND_HELP_BUTTON = help_helper.render_help_label(blend_label, 'uis_help.blend', MODULE_NAME, visible = has_frame_enhancer)
	FRAME_ENHANCER_BLEND_SLIDER = gradio.Slider(
		label = blend_label,
		show_label = False,
		value = state_manager.get_item('frame_enhancer_blend'),
		step = calculate_int_step(frame_enhancer_choices.frame_enhancer_blend_range),
		minimum = frame_enhancer_choices.frame_enhancer_blend_range[0],
		maximum = frame_enhancer_choices.frame_enhancer_blend_range[-1],
		visible = has_frame_enhancer
	)
	register_ui_component('frame_enhancer_model_dropdown', FRAME_ENHANCER_MODEL_DROPDOWN)
	register_ui_component('frame_enhancer_blend_slider', FRAME_ENHANCER_BLEND_SLIDER)


def listen() -> None:
	FRAME_ENHANCER_MODEL_DROPDOWN.change(update_frame_enhancer_model, inputs = FRAME_ENHANCER_MODEL_DROPDOWN, outputs = FRAME_ENHANCER_MODEL_DROPDOWN)
	FRAME_ENHANCER_BLEND_SLIDER.release(update_frame_enhancer_blend, inputs = FRAME_ENHANCER_BLEND_SLIDER)
	help_helper.listen_help_button(FRAME_ENHANCER_MODEL_HELP_BUTTON, 'uis_help.model', MODULE_NAME)
	help_helper.listen_help_button(FRAME_ENHANCER_BLEND_HELP_BUTTON, 'uis_help.blend', MODULE_NAME)

	processors_checkbox_group = get_ui_component('processors_checkbox_group')
	if processors_checkbox_group:
		processors_checkbox_group.change(remote_update, inputs = processors_checkbox_group, outputs = [ FRAME_ENHANCER_MODEL_LABEL_ROW, FRAME_ENHANCER_MODEL_DROPDOWN, FRAME_ENHANCER_BLEND_LABEL_ROW, FRAME_ENHANCER_BLEND_SLIDER ])


def remote_update(processors : List[str]) -> Tuple[gradio.Row, gradio.Dropdown, gradio.Row, gradio.Slider]:
	has_frame_enhancer = 'frame_enhancer' in processors
	return gradio.Row(visible = has_frame_enhancer), gradio.Dropdown(visible = has_frame_enhancer), gradio.Row(visible = has_frame_enhancer), gradio.Slider(visible = has_frame_enhancer)


def update_frame_enhancer_model(frame_enhancer_model : FrameEnhancerModel) -> gradio.Dropdown:
	frame_enhancer_module = load_processor_module('frame_enhancer')
	frame_enhancer_module.clear_inference_pool()
	state_manager.set_item('frame_enhancer_model', frame_enhancer_model)

	if frame_enhancer_module.pre_check():
		return gradio.Dropdown(value = state_manager.get_item('frame_enhancer_model'))
	return gradio.Dropdown()


def update_frame_enhancer_blend(frame_enhancer_blend : float) -> None:
	state_manager.set_item('frame_enhancer_blend', int(frame_enhancer_blend))
