import gradio

from facefusion import translator


def render_help_button(notation : str, module_name : str = 'facefusion') -> gradio.Button:
	return gradio.Button(
		value = 'ℹ️',
		size = 'sm',
		min_width = 40,
		elem_classes = [ 'ff-help-button' ],
		elem_id = None
	)


def show_help(notation : str, module_name : str = 'facefusion') -> None:
	message = translator.get(notation, module_name)
	if message:
		gradio.Info(message)


def listen_help_button(button : gradio.Button, notation : str, module_name : str = 'facefusion') -> None:
	button.click(lambda: show_help(notation, module_name))
