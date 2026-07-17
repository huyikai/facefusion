from facefusion.types import Locales

LOCALES : Locales =\
{'en': {'help': {'model': 'choose the model responsible for colorizing the frame',
                 'size': 'specify the frame size provided to the frame colorizer',
                 'blend': 'blend the colorized into the previous frame'},
        'uis_help': {'model': 'Choose the colorization model for black and white or faded footage.',
                     'size': 'Input resolution for the colorizer. Match the frame size when possible.',
                     'blend': 'Mix colorized output with the original frame. Lower to keep more of the source look.'},
        'uis': {'blend_slider': 'FRAME COLORIZER BLEND',
                'model_dropdown': 'FRAME COLORIZER MODEL',
                'size_dropdown': 'FRAME COLORIZER SIZE'}},
 'zh': {'help': {'model': '选择负责画面上色的模型', 'size': '指定提供给上色器的帧尺寸', 'blend': '将上色结果混合到先前帧'},
        'uis_help': {'model': '选择上色模型，用于黑白或褪色画面。',
                     'size': '上色器输入分辨率。尽量与画面尺寸匹配。',
                     'blend': '将上色结果与原帧混合。降低可保留更多原始观感。'},
        'uis': {'blend_slider': '画面上色混合', 'model_dropdown': '画面上色模型', 'size_dropdown': '画面上色尺寸'}}}
