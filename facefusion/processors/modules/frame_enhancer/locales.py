from facefusion.types import Locales

LOCALES : Locales =\
{'en': {'help': {'model': 'choose the model responsible for enhancing the frame',
                 'blend': 'blend the enhanced into the previous frame'},
        'uis_help': {'model': 'Choose the frame enhancement model to improve sharpness and detail.',
                     'blend': 'Mix enhanced output with the original frame. Raise slowly to avoid halos or artifacts.'},
        'uis': {'blend_slider': 'FRAME ENHANCER BLEND', 'model_dropdown': 'FRAME ENHANCER MODEL'}},
 'zh': {'help': {'model': '选择负责增强画面的模型', 'blend': '将增强结果混合到先前帧'},
        'uis_help': {'model': '选择画面增强模型，提升清晰度与细节。',
                     'blend': '将增强结果与原帧混合。过高可能出现光晕或伪影。'},
        'uis': {'blend_slider': '画面增强混合', 'model_dropdown': '画面增强模型'}}}
