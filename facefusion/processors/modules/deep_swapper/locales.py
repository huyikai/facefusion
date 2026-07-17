from facefusion.types import Locales

LOCALES : Locales =\
{'en': {'help': {'model': 'choose the model responsible for swapping the face',
                 'morph': 'morph between source face and target faces'},
        'uis_help': {'model': 'Choose the deep swapper model.',
                     'morph': 'Blend between source and target faces. Adjust when edges or identity look mismatched.'},
        'uis': {'model_dropdown': 'DEEP SWAPPER MODEL', 'morph_slider': 'DEEP SWAPPER MORPH'}},
 'zh': {'help': {'model': '选择负责深度换脸的模型', 'morph': '在源脸与目标脸之间进行形态融合'},
        'uis_help': {'model': '选择深度换脸模型。',
                     'morph': '在源脸与目标脸之间融合。边缘或身份不协调时可调整。'},
        'uis': {'model_dropdown': '深度换脸模型', 'morph_slider': '深度换脸融合'}}}
