from facefusion.types import Locales

LOCALES : Locales =\
{'en': {'help': {'model': 'choose the model responsible for restoring the expression',
                 'factor': 'restore factor of expression from the target face',
                 'areas': 'choose the items used for the expression areas (choices: {choices})'},
        'uis_help': {'model': 'Choose the expression restoration model.',
                     'factor': 'How much expression to pull from the target face. Raise if the result looks too neutral.',
                     'areas': 'Limit restoration to specific facial regions such as eyes or mouth.'},
        'uis': {'model_dropdown': 'EXPRESSION RESTORER MODEL',
                'factor_slider': 'EXPRESSION RESTORER FACTOR',
                'areas_checkbox_group': 'EXPRESSION RESTORER AREAS'}},
 'zh': {'help': {'model': '选择负责恢复表情的模型', 'factor': '从目标脸恢复表情的强度', 'areas': '选择表情恢复区域（可选：{choices}）'},
        'uis_help': {'model': '选择表情恢复模型。',
                     'factor': '从目标脸恢复表情的强度。结果过于平淡时可适当提高。',
                     'areas': '限定恢复范围，如仅眼睛或嘴部区域。'},
        'uis': {'model_dropdown': '表情恢复模型', 'factor_slider': '表情恢复强度', 'areas_checkbox_group': '表情恢复区域'}}}
