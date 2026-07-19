import html as html_module
from typing import Tuple

import gradio

from facefusion import translator


def render_help_button(notation : str, module_name : str = 'facefusion', visible : bool = True) -> gradio.Button:
	return gradio.Button(
		value = 'ℹ️',
		size = 'sm',
		scale = 0,
		min_width = 24,
		elem_classes = [ 'ff-help-button' ],
		elem_id = None,
		visible = visible
	)


def render_help_label(label : str, notation : str, module_name : str = 'facefusion', visible : bool = True) -> Tuple[gradio.Row, gradio.Button]:
	with gradio.Row(elem_classes = [ 'ff-help-label-row' ], visible = visible) as row:
		gradio.HTML(
			value = '<span class="ff-help-label-text">{label}</span>'.format(label = html_module.escape(label)),
			elem_classes = [ 'ff-help-label' ]
		)
		button = render_help_button(notation, module_name, visible = True)
	return row, button


def show_help(notation : str, module_name : str = 'facefusion') -> None:
	message = translator.get(notation, module_name)
	if message:
		gradio.Info(message)


def listen_help_button(button : gradio.Button, notation : str, module_name : str = 'facefusion') -> None:
	button.click(lambda: show_help(notation, module_name))
