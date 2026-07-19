from typing import List, Optional, Tuple

import gradio

from facefusion import state_manager, translator
from facefusion.common_helper import calculate_float_step, calculate_int_step
from facefusion.processors.core import load_processor_module
from facefusion.processors.modules.face_enhancer import choices as face_enhancer_choices
from facefusion.processors.modules.face_enhancer.types import FaceEnhancerModel, FaceEnhancerWeight
from facefusion.uis import help_helper
from facefusion.uis.core import get_ui_component, register_ui_component

MODULE_NAME = 'facefusion.processors.modules.face_enhancer'

FACE_ENHANCER_MODEL_LABEL_ROW : Optional[gradio.Row] = None
FACE_ENHANCER_MODEL_DROPDOWN : Optional[gradio.Dropdown] = None
FACE_ENHANCER_MODEL_HELP_BUTTON : Optional[gradio.Button] = None
FACE_ENHANCER_BLEND_LABEL_ROW : Optional[gradio.Row] = None
FACE_ENHANCER_BLEND_SLIDER : Optional[gradio.Slider] = None
FACE_ENHANCER_BLEND_HELP_BUTTON : Optional[gradio.Button] = None
FACE_ENHANCER_WEIGHT_LABEL_ROW : Optional[gradio.Row] = None
FACE_ENHANCER_WEIGHT_SLIDER : Optional[gradio.Slider] = None
FACE_ENHANCER_WEIGHT_HELP_BUTTON : Optional[gradio.Button] = None


def render() -> None:
	global FACE_ENHANCER_MODEL_LABEL_ROW
	global FACE_ENHANCER_MODEL_DROPDOWN
	global FACE_ENHANCER_MODEL_HELP_BUTTON
	global FACE_ENHANCER_BLEND_LABEL_ROW
	global FACE_ENHANCER_BLEND_SLIDER
	global FACE_ENHANCER_BLEND_HELP_BUTTON
	global FACE_ENHANCER_WEIGHT_LABEL_ROW
	global FACE_ENHANCER_WEIGHT_SLIDER
	global FACE_ENHANCER_WEIGHT_HELP_BUTTON

	has_face_enhancer = 'face_enhancer' in state_manager.get_item('processors')
	weight_visible = has_face_enhancer and load_processor_module('face_enhancer').get_inference_pool() and load_processor_module('face_enhancer').has_weight_input()
	model_label = translator.get('uis.model_dropdown', MODULE_NAME)
	blend_label = translator.get('uis.blend_slider', MODULE_NAME)
	weight_label = translator.get('uis.weight_slider', MODULE_NAME)

	FACE_ENHANCER_MODEL_LABEL_ROW, FACE_ENHANCER_MODEL_HELP_BUTTON = help_helper.render_help_label(model_label, 'uis_help.model', MODULE_NAME, visible = has_face_enhancer)
	FACE_ENHANCER_MODEL_DROPDOWN = gradio.Dropdown(
		label = model_label,
		show_label = False,
		choices = face_enhancer_choices.face_enhancer_models,
		value = state_manager.get_item('face_enhancer_model'),
		visible = has_face_enhancer
	)
	FACE_ENHANCER_BLEND_LABEL_ROW, FACE_ENHANCER_BLEND_HELP_BUTTON = help_helper.render_help_label(blend_label, 'uis_help.blend', MODULE_NAME, visible = has_face_enhancer)
	FACE_ENHANCER_BLEND_SLIDER = gradio.Slider(
		label = blend_label,
		show_label = False,
		value = state_manager.get_item('face_enhancer_blend'),
		step = calculate_int_step(face_enhancer_choices.face_enhancer_blend_range),
		minimum = face_enhancer_choices.face_enhancer_blend_range[0],
		maximum = face_enhancer_choices.face_enhancer_blend_range[-1],
		visible = has_face_enhancer
	)
	FACE_ENHANCER_WEIGHT_LABEL_ROW, FACE_ENHANCER_WEIGHT_HELP_BUTTON = help_helper.render_help_label(weight_label, 'uis_help.weight', MODULE_NAME, visible = weight_visible)
	FACE_ENHANCER_WEIGHT_SLIDER = gradio.Slider(
		label = weight_label,
		show_label = False,
		value = state_manager.get_item('face_enhancer_weight'),
		step = calculate_float_step(face_enhancer_choices.face_enhancer_weight_range),
		minimum = face_enhancer_choices.face_enhancer_weight_range[0],
		maximum = face_enhancer_choices.face_enhancer_weight_range[-1],
		visible = weight_visible
	)
	register_ui_component('face_enhancer_model_dropdown', FACE_ENHANCER_MODEL_DROPDOWN)
	register_ui_component('face_enhancer_blend_slider', FACE_ENHANCER_BLEND_SLIDER)
	register_ui_component('face_enhancer_weight_slider', FACE_ENHANCER_WEIGHT_SLIDER)


def listen() -> None:
	FACE_ENHANCER_MODEL_DROPDOWN.change(update_face_enhancer_model, inputs = FACE_ENHANCER_MODEL_DROPDOWN, outputs = [ FACE_ENHANCER_MODEL_DROPDOWN, FACE_ENHANCER_WEIGHT_LABEL_ROW, FACE_ENHANCER_WEIGHT_SLIDER ])
	FACE_ENHANCER_BLEND_SLIDER.release(update_face_enhancer_blend, inputs = FACE_ENHANCER_BLEND_SLIDER)
	FACE_ENHANCER_WEIGHT_SLIDER.release(update_face_enhancer_weight, inputs = FACE_ENHANCER_WEIGHT_SLIDER)
	help_helper.listen_help_button(FACE_ENHANCER_MODEL_HELP_BUTTON, 'uis_help.model', MODULE_NAME)
	help_helper.listen_help_button(FACE_ENHANCER_BLEND_HELP_BUTTON, 'uis_help.blend', MODULE_NAME)
	help_helper.listen_help_button(FACE_ENHANCER_WEIGHT_HELP_BUTTON, 'uis_help.weight', MODULE_NAME)

	processors_checkbox_group = get_ui_component('processors_checkbox_group')
	if processors_checkbox_group:
		processors_checkbox_group.change(remote_update, inputs = processors_checkbox_group, outputs = [ FACE_ENHANCER_MODEL_LABEL_ROW, FACE_ENHANCER_MODEL_DROPDOWN, FACE_ENHANCER_BLEND_LABEL_ROW, FACE_ENHANCER_BLEND_SLIDER, FACE_ENHANCER_WEIGHT_LABEL_ROW, FACE_ENHANCER_WEIGHT_SLIDER ])


def remote_update(processors : List[str]) -> Tuple[gradio.Row, gradio.Dropdown, gradio.Row, gradio.Slider, gradio.Row, gradio.Slider]:
	has_face_enhancer = 'face_enhancer' in processors
	weight_visible = has_face_enhancer and load_processor_module('face_enhancer').get_inference_pool() and load_processor_module('face_enhancer').has_weight_input()
	return gradio.Row(visible = has_face_enhancer), gradio.Dropdown(visible = has_face_enhancer), gradio.Row(visible = has_face_enhancer), gradio.Slider(visible = has_face_enhancer), gradio.Row(visible = weight_visible), gradio.Slider(visible = weight_visible)


def update_face_enhancer_model(face_enhancer_model : FaceEnhancerModel) -> Tuple[gradio.Dropdown, gradio.Row, gradio.Slider]:
	face_enhancer_module = load_processor_module('face_enhancer')
	face_enhancer_module.clear_inference_pool()
	state_manager.set_item('face_enhancer_model', face_enhancer_model)

	if face_enhancer_module.pre_check():
		weight_visible = face_enhancer_module.has_weight_input()
		return gradio.Dropdown(value = state_manager.get_item('face_enhancer_model')), gradio.Row(visible = weight_visible), gradio.Slider(visible = weight_visible)
	return gradio.Dropdown(), gradio.Row(), gradio.Slider()


def update_face_enhancer_blend(face_enhancer_blend : float) -> None:
	state_manager.set_item('face_enhancer_blend', int(face_enhancer_blend))


def update_face_enhancer_weight(face_enhancer_weight : FaceEnhancerWeight) -> None:
	state_manager.set_item('face_enhancer_weight', face_enhancer_weight)
