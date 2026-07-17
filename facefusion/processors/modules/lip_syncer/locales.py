from facefusion.types import Locales

LOCALES : Locales =\
{'en': {'help': {'model': 'choose the model responsible for syncing the lips',
                 'weight': 'specify the degree of weight applied to the lips'},
        'uis_help': {'model': 'Choose the lip sync model. Use when audio and mouth movement need to match.',
                     'weight': 'How strongly lip sync is applied. Lower if mouth shapes look exaggerated.'},
        'uis': {'model_dropdown': 'LIP SYNCER MODEL', 'weight_slider': 'LIP SYNCER WEIGHT'}},
 'zh': {'help': {'model': '选择负责口型同步的模型', 'weight': '指定应用到嘴唇的权重'},
        'uis_help': {'model': '选择口型同步模型。用于让嘴型与音频对齐。',
                     'weight': '口型同步强度。嘴型夸张时可适当降低。'},
        'uis': {'model_dropdown': '口型同步模型', 'weight_slider': '口型同步权重'}}}
