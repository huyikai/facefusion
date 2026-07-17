from typing import List, Optional, Tuple

import gradio

from facefusion import state_manager, translator
from facefusion.common_helper import calculate_float_step, get_first
from facefusion.processors.core import load_processor_module
from facefusion.processors.modules.face_swapper import choices as face_swapper_choices
from facefusion.processors.modules.face_swapper.types import FaceSwapperModel, FaceSwapperWeight
from facefusion.uis import help_helper
from facefusion.uis.core import get_ui_component, register_ui_component

MODULE_NAME = 'facefusion.processors.modules.face_swapper'

FACE_SWAPPER_MODEL_DROPDOWN : Optional[gradio.Dropdown] = None
FACE_SWAPPER_MODEL_HELP_BUTTON : Optional[gradio.Button] = None
FACE_SWAPPER_PIXEL_BOOST_DROPDOWN : Optional[gradio.Dropdown] = None
FACE_SWAPPER_PIXEL_BOOST_HELP_BUTTON : Optional[gradio.Button] = None
FACE_SWAPPER_WEIGHT_SLIDER : Optional[gradio.Slider] = None
FACE_SWAPPER_WEIGHT_HELP_BUTTON : Optional[gradio.Button] = None


def render() -> None:
	global FACE_SWAPPER_MODEL_DROPDOWN
	global FACE_SWAPPER_MODEL_HELP_BUTTON
	global FACE_SWAPPER_PIXEL_BOOST_DROPDOWN
	global FACE_SWAPPER_PIXEL_BOOST_HELP_BUTTON
	global FACE_SWAPPER_WEIGHT_SLIDER
	global FACE_SWAPPER_WEIGHT_HELP_BUTTON

	has_face_swapper = 'face_swapper' in state_manager.get_item('processors')
	with gradio.Row():
		FACE_SWAPPER_MODEL_DROPDOWN = gradio.Dropdown(
			label = translator.get('uis.model_dropdown', MODULE_NAME),
			choices = face_swapper_choices.face_swapper_models,
			value = state_manager.get_item('face_swapper_model'),
			visible = has_face_swapper
		)
		FACE_SWAPPER_MODEL_HELP_BUTTON = help_helper.render_help_button('uis_help.model', MODULE_NAME, visible = has_face_swapper)
	with gradio.Row():
		FACE_SWAPPER_PIXEL_BOOST_DROPDOWN = gradio.Dropdown(
			label = translator.get('uis.pixel_boost_dropdown', MODULE_NAME),
			choices = face_swapper_choices.face_swapper_set.get(state_manager.get_item('face_swapper_model')),
			value = state_manager.get_item('face_swapper_pixel_boost'),
			visible = has_face_swapper
		)
		FACE_SWAPPER_PIXEL_BOOST_HELP_BUTTON = help_helper.render_help_button('uis_help.pixel_boost', MODULE_NAME, visible = has_face_swapper)
	with gradio.Row():
		FACE_SWAPPER_WEIGHT_SLIDER = gradio.Slider(
			label = translator.get('uis.weight_slider', MODULE_NAME),
			value = state_manager.get_item('face_swapper_weight'),
			minimum = face_swapper_choices.face_swapper_weight_range[0],
			maximum = face_swapper_choices.face_swapper_weight_range[-1],
			step = calculate_float_step(face_swapper_choices.face_swapper_weight_range),
			visible = has_face_swapper and has_face_swapper_weight()
		)
		FACE_SWAPPER_WEIGHT_HELP_BUTTON = help_helper.render_help_button('uis_help.weight', MODULE_NAME, visible = has_face_swapper and has_face_swapper_weight())
	register_ui_component('face_swapper_model_dropdown', FACE_SWAPPER_MODEL_DROPDOWN)
	register_ui_component('face_swapper_pixel_boost_dropdown', FACE_SWAPPER_PIXEL_BOOST_DROPDOWN)
	register_ui_component('face_swapper_weight_slider', FACE_SWAPPER_WEIGHT_SLIDER)


def listen() -> None:
	FACE_SWAPPER_MODEL_DROPDOWN.change(update_face_swapper_model, inputs = FACE_SWAPPER_MODEL_DROPDOWN, outputs = [ FACE_SWAPPER_MODEL_DROPDOWN, FACE_SWAPPER_PIXEL_BOOST_DROPDOWN, FACE_SWAPPER_WEIGHT_SLIDER, FACE_SWAPPER_WEIGHT_HELP_BUTTON ])
	FACE_SWAPPER_PIXEL_BOOST_DROPDOWN.change(update_face_swapper_pixel_boost, inputs = FACE_SWAPPER_PIXEL_BOOST_DROPDOWN)
	FACE_SWAPPER_WEIGHT_SLIDER.change(update_face_swapper_weight, inputs = FACE_SWAPPER_WEIGHT_SLIDER)
	help_helper.listen_help_button(FACE_SWAPPER_MODEL_HELP_BUTTON, 'uis_help.model', MODULE_NAME)
	help_helper.listen_help_button(FACE_SWAPPER_PIXEL_BOOST_HELP_BUTTON, 'uis_help.pixel_boost', MODULE_NAME)
	help_helper.listen_help_button(FACE_SWAPPER_WEIGHT_HELP_BUTTON, 'uis_help.weight', MODULE_NAME)

	processors_checkbox_group = get_ui_component('processors_checkbox_group')
	if processors_checkbox_group:
		processors_checkbox_group.change(remote_update, inputs = processors_checkbox_group, outputs = [ FACE_SWAPPER_MODEL_DROPDOWN, FACE_SWAPPER_MODEL_HELP_BUTTON, FACE_SWAPPER_PIXEL_BOOST_DROPDOWN, FACE_SWAPPER_PIXEL_BOOST_HELP_BUTTON, FACE_SWAPPER_WEIGHT_SLIDER, FACE_SWAPPER_WEIGHT_HELP_BUTTON ])


def remote_update(processors : List[str]) -> Tuple[gradio.Dropdown, gradio.Button, gradio.Dropdown, gradio.Button, gradio.Slider, gradio.Button]:
	has_face_swapper = 'face_swapper' in processors
	weight_visible = has_face_swapper and has_face_swapper_weight()
	return gradio.Dropdown(visible = has_face_swapper), gradio.Button(visible = has_face_swapper), gradio.Dropdown(visible = has_face_swapper), gradio.Button(visible = has_face_swapper), gradio.Slider(visible = weight_visible), gradio.Button(visible = weight_visible)


def update_face_swapper_model(face_swapper_model : FaceSwapperModel) -> Tuple[gradio.Dropdown, gradio.Dropdown, gradio.Slider, gradio.Button]:
	face_swapper_module = load_processor_module('face_swapper')
	face_swapper_module.clear_inference_pool()
	state_manager.set_item('face_swapper_model', face_swapper_model)

	if face_swapper_module.pre_check():
		face_swapper_pixel_boost_dropdown_choices = face_swapper_choices.face_swapper_set.get(state_manager.get_item('face_swapper_model'))
		state_manager.set_item('face_swapper_pixel_boost', get_first(face_swapper_pixel_boost_dropdown_choices))
		weight_visible = has_face_swapper_weight()
		return gradio.Dropdown(value = state_manager.get_item('face_swapper_model')), gradio.Dropdown(value = state_manager.get_item('face_swapper_pixel_boost'), choices = face_swapper_pixel_boost_dropdown_choices), gradio.Slider(visible = weight_visible), gradio.Button(visible = weight_visible)
	return gradio.Dropdown(), gradio.Dropdown(), gradio.Slider(), gradio.Button()


def update_face_swapper_pixel_boost(face_swapper_pixel_boost : str) -> None:
	state_manager.set_item('face_swapper_pixel_boost', face_swapper_pixel_boost)


def update_face_swapper_weight(face_swapper_weight : FaceSwapperWeight) -> None:
	state_manager.set_item('face_swapper_weight', face_swapper_weight)


def has_face_swapper_weight() -> bool:
	return state_manager.get_item('face_swapper_model') in [ 'ghost_1_256', 'ghost_2_256', 'ghost_3_256', 'hififace_unofficial_256', 'hyperswap_1a_256', 'hyperswap_1b_256', 'hyperswap_1c_256', 'inswapper_128', 'inswapper_128_fp16', 'simswap_256', 'simswap_unofficial_512' ]
